import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { salvaPratica } from "../src/lib/schedaPratica.js";
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
