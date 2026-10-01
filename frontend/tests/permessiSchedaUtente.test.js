import { test } from "node:test";
import assert from "node:assert/strict";
import { permessiSchedaUtente } from "../src/lib/permessiSchedaUtente.js";

const sessione = (ruoloCodice, utenteId = 10) => ({ ruoloCodice, utenteId });
const ordinati = (codici) => [...codici].sort();
const scheda = (chi, attuale, utenteId = 99) =>
  ordinati(permessiSchedaUtente(sessione(chi), utenteId, attuale).ruoliScheda);
const attuatore = (chi, attuale = "", utenteId = 99) =>
  ordinati(permessiSchedaUtente(sessione(chi), utenteId, attuale).ruoliAttuatore);

test("nazionale: tutti e sette i ruoli, anche sulla propria scheda", () => {
  assert.equal(scheda("nazionale", "Aderente").length, 7);
  assert.equal(scheda("nazionale", "Nazionale", 10).length, 7);
  assert.deepEqual(attuatore("nazionale"), ["Aderente", "Nazionale", "Provinciale", "Regionale"]);
});

test("regionale: promuove a Aderente o Provinciale, declassa a Utente chi sta sotto", () => {
  assert.deepEqual(scheda("regionale", "Utente"), ["Aderente", "Provinciale", "Utente"]);
  assert.deepEqual(scheda("regionale", "Aderente"), ["Aderente", "Provinciale", "Utente"]);
  assert.deepEqual(scheda("regionale", "Provinciale"), ["Aderente", "Provinciale", "Utente"]);
  assert.deepEqual(scheda("regionale", "Regionale"), ["Regionale"]);
  assert.deepEqual(scheda("regionale", "Nazionale"), ["Nazionale"]);
  assert.deepEqual(attuatore("regionale"), ["Aderente", "Provinciale"]);
});

test("provinciale: solo Aderente, e declassa a Utente un Aderente", () => {
  assert.deepEqual(scheda("provinciale", "Utente"), ["Aderente", "Utente"]);
  assert.deepEqual(scheda("provinciale", "Aderente"), ["Aderente", "Utente"]);
  assert.deepEqual(scheda("provinciale", "Provinciale"), ["Provinciale"]);
  // Creando un attuatore c'e' una sola scelta: valore bloccato.
  assert.deepEqual(attuatore("provinciale"), ["Aderente"]);
  // In Dati principali niente Utente: si declassa solo dalla scheda Utente.
  assert.deepEqual(attuatore("provinciale", "Aderente"), ["Aderente"]);
});

test("aderente: un solo valore, quello attuale, anche su un sottoscrittore", () => {
  assert.deepEqual(scheda("aderente", "Utente"), ["Utente"]);
  assert.deepEqual(scheda("aderente", "Aderente"), ["Aderente"]);
});

test("chi non e' nazionale non cambia il proprio ruolo; account sempre sulla propria scheda", () => {
  assert.deepEqual(scheda("regionale", "Regionale", "10"), ["Regionale"]);
  assert.deepEqual(attuatore("regionale", "Regionale", 10), ["Regionale"]);
  assert.equal(permessiSchedaUtente(sessione("aderente"), 10, "Aderente").account, true);
  assert.equal(permessiSchedaUtente(sessione("aderente"), 99, "Utente").account, false);
  assert.equal(permessiSchedaUtente(sessione("regionale"), 99, "Utente").account, true);
  assert.equal(permessiSchedaUtente(null, 10).account, false);
});

test("consulente e operatore si promuovono, ma li assegna solo il nazionale", () => {
  assert.deepEqual(scheda("regionale", "Consulente"), ["Aderente", "Consulente", "Provinciale"]);
  assert.ok(!scheda("regionale", "Utente").includes("Operatore"));
});
