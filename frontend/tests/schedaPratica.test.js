import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { caricaSchedaPratica, salvaPratica } from "../src/lib/schedaPratica.js";
import { salvaSessione, pulisciSessione } from "../src/lib/sessione.js";

const richieste = [], risposte = [];
beforeEach(() => {
  globalThis.window = { localStorage: { removeItem() {} }, sessionStorage: { removeItem() {} } };
  pulisciSessione();
  salvaSessione({ utente_id: 999, ruolo_codice: "Aderente", csrf_token: "a".repeat(64) });
  richieste.length = risposte.length = 0;
  globalThis.fetch = async (url, opzioni) => { richieste.push({ url, ...opzioni }); return risposte.shift(); };
});
test("creazione e modifica Pratiche usano cookie/CSRF e non ripetono automaticamente la scrittura", async () => {
  const payload = { cliente_id: 17, listTesta_id: 42, pratica_numero: "TEST" };
  risposte.push(new Response(JSON.stringify({ pratica_id: 101 }), { status: 201 }));
  assert.equal((await salvaPratica(null, payload)).pratica_id, 101);
  assert.match(richieste[0].url, /\/pratiche\/$/);
  assert.equal(richieste[0].method, "POST");
  assert.equal(richieste[0].credentials, "include");
  assert.equal(richieste[0].headers["X-CSRF-Token"], "a".repeat(64));
  assert.deepEqual(JSON.parse(richieste[0].body), payload);
  risposte.push(new Response("<html>Bad Gateway</html>", { status: 502 }));
  await assert.rejects(salvaPratica(101, { pratica_note: null }), /temporaneamente/i);
  assert.equal(richieste.length, 2);
  assert.equal(richieste[1].method, "PUT");
});
test("un 200 senza pratica valida non viene presentato come salvataggio riuscito", async () => {
  for (const contenuto of ["<html>errore</html>", "{}", "null"]) {
    risposte.push(new Response(contenuto, { status: 200 }));
    await assert.rejects(salvaPratica(null, {}));
  }
});

function rispondiPerUrl(mappa) {
  globalThis.fetch = async (url, opzioni) => {
    richieste.push({ url, ...opzioni });
    const percorso = new URL(url, "https://test.example.org").pathname;
    const [stato, corpo] = mappa[percorso] ?? [404, { detail: "non previsto" }];
    return new Response(JSON.stringify(corpo), { status: stato });
  };
}

const CATALOGHI = {
  "/pratiche/filtri/stati": [200, [{ id: 1, label: "Aperta" }]],
  "/listini-testa/opzioni/universita": [200, []],
};

test("la scheda prende l'emittente dalla pratica, senza chiedere /clienti/", async () => {
  const emittente = { cliente_id: 7, cliente_nome: "Elena", cliente_cognome: "Rossi", cliente_codice: "COD7" };
  rispondiPerUrl({ ...CATALOGHI,
    "/pratiche/101": [200, { pratica_id: 101, cliente_id: 3, cliente_emittente_aderente_id: 7, emittente }] });

  const scheda = await caricaSchedaPratica(101);

  assert.deepEqual(scheda.emittente, { id: 7, label: "Elena Rossi", dettaglio: "COD7" });
  assert.equal(scheda.pratica.cliente_id, 3);
  assert.equal(richieste.length, 3);
  assert.ok(richieste.every(({ url }) => !url.includes("/clienti/")));
});

test("senza emittente nella risposta la scheda non ne inventa uno", async () => {
  rispondiPerUrl({ ...CATALOGHI,
    "/pratiche/102": [200, { pratica_id: 102, cliente_emittente_aderente_id: 7, emittente: null }] });
  assert.equal((await caricaSchedaPratica(102)).emittente, null);
  assert.ok(richieste.every(({ url }) => !url.includes("/clienti/")));
});

test("una pratica non visibile arriva come 404 con il messaggio del servizio", async () => {
  rispondiPerUrl({ ...CATALOGHI, "/pratiche/103": [404, { detail: "Pratica non trovata." }] });
  await assert.rejects(caricaSchedaPratica(103), (errore) =>
    errore.status === 404 && errore.message === "Pratica non trovata.");
});

test("una scheda nuova non chiede nessuna pratica", async () => {
  rispondiPerUrl(CATALOGHI);
  const scheda = await caricaSchedaPratica(null);
  assert.equal(scheda.pratica, null);
  assert.equal(scheda.emittente, null);
  assert.equal(richieste.length, 2);
});

