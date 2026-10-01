import { test } from "node:test";
import assert from "node:assert/strict";
import { permessiSchedaUtente } from "../src/lib/permessiSchedaUtente.js";

const sessione = (ruoloCodice, utenteId = 10) => ({ ruoloCodice, utenteId });

test("nazionale: modifica tutto, anche la propria scheda, e assegna Nazionale", () => {
  assert.deepEqual(permessiSchedaUtente(sessione("nazionale"), 10), {
    account: true, ruolo: true, assegnaNazionale: true,
  });
  assert.deepEqual(permessiSchedaUtente(sessione("nazionale"), 99), {
    account: true, ruolo: true, assegnaNazionale: true,
  });
});

test("regionale: account e ruolo degli altri, non il proprio ruolo, mai Nazionale", () => {
  assert.deepEqual(permessiSchedaUtente(sessione("regionale"), 99), {
    account: true, ruolo: true, assegnaNazionale: false,
  });
  assert.deepEqual(permessiSchedaUtente(sessione("regionale"), 10), {
    account: true, ruolo: false, assegnaNazionale: false,
  });
});

test("aderente o provinciale: account solo sulla propria scheda, ruolo solo degli altri", () => {
  for (const ruolo of ["aderente", "provinciale"]) {
    assert.deepEqual(permessiSchedaUtente(sessione(ruolo), 99), {
      account: false, ruolo: true, assegnaNazionale: false,
    });
    assert.deepEqual(permessiSchedaUtente(sessione(ruolo), "10"), {
      account: true, ruolo: false, assegnaNazionale: false,
    });
  }
});

test("scheda non ancora caricata o in creazione: nessuna scheda 'propria'", () => {
  assert.equal(permessiSchedaUtente(sessione("aderente"), null).ruolo, true);
  assert.equal(permessiSchedaUtente(sessione("aderente"), null).account, false);
  assert.equal(permessiSchedaUtente(null, 10).account, false);
});
