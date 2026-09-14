import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { caricaProfilo, nomeProfilo, sezioniProfilo } from "../src/lib/profilo.js";
import { leggiSessione, osservaSessione, pulisciSessione, salvaSessione } from "../src/lib/sessione.js";

const sessione = { utente_id: 4, utente_username: "elena.bianchi", nome: "Elena", cognome: "Bianchi", ruolo_codice: "Regionale", csrf_token: "a".repeat(64) };
beforeEach(() => pulisciSessione());

test("identità usa nome e cognome, ripiega sullo username e gestisce nomi parziali", () => {
  assert.equal(nomeProfilo({ nome: " Elena ", cognome: "Bianchi" }), "Elena Bianchi");
  assert.equal(nomeProfilo({ nome: " ", cognome: null, username: "operatore.roma" }), "operatore.roma");
  assert.equal(nomeProfilo({ cognome: "D'Amico" }), "D'Amico");
  assert.equal(nomeProfilo(null), "Il tuo account");
});

test("snapshot stabile, notifiche reattive e nessun nome ereditato cambiando account", () => {
  const notifiche = [];
  const rimuovi = osservaSessione(() => notifiche.push(leggiSessione()));
  salvaSessione(sessione);
  const primo = leggiSessione();
  assert.equal(leggiSessione(), primo);
  assert.equal(nomeProfilo(primo), "Elena Bianchi");
  salvaSessione({ utente_id: 9, csrf_token: "b".repeat(64), utente_username: "altro.account" });
  assert.equal(nomeProfilo(leggiSessione()), "altro.account");
  pulisciSessione();
  assert.equal(leggiSessione(), null);
  assert.equal(notifiche.length, 3);
  rimuovi();
  salvaSessione(sessione);
  assert.equal(notifiche.length, 3);
});

test("profilo legge solo la rotta personale tramite cookie e senza cache", async () => {
  const profilo = { username: "elena.bianchi", residenza: {}, domicilio: {} };
  globalThis.fetch = async (url, opzioni) => {
    assert.match(url, /\/profilo\/me$/);
    assert.equal(opzioni.credentials, "include");
    assert.equal(opzioni.cache, "no-store");
    assert.equal(opzioni.body, undefined);
    assert.equal(opzioni.headers.Authorization, undefined);
    return new Response(JSON.stringify(profilo));
  };
  assert.deepEqual(await caricaProfilo(), profilo);
});

test("campi assenti espliciti, CAP con zeri iniziali e domicilio non dedotto dalla residenza", () => {
  const sezioni = sezioniProfilo({ nome: "Elena", residenza: { cap: "00100" }, domicilio: {} });
  assert.equal(sezioni[0].campi.find((c) => c.chiave === "codice_fiscale").valore, "Non indicato");
  assert.equal(sezioni[2].campi.find((c) => c.chiave === "cap").valore, "00100");
  assert.equal(sezioni[3].campi.find((c) => c.chiave === "cap").valore, "Non indicato");
});

test("errori servizio e risposta incompleta non diventano un profilo vuoto", async () => {
  globalThis.fetch = async () => new Response("Bad Gateway", { status: 502 });
  await assert.rejects(caricaProfilo(), /Servizio temporaneamente/);
  globalThis.fetch = async () => new Response("{}");
  await assert.rejects(caricaProfilo(), /caricare il tuo profilo/);
  globalThis.fetch = async () => { throw new TypeError("Failed to fetch"); };
  await assert.rejects(caricaProfilo(), /connessione/i);
});
