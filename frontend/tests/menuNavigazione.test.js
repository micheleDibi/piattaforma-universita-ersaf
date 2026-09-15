import { test } from "node:test";
import assert from "node:assert/strict";
import { vociMenuPerRuolo } from "../src/config/routes/rotte.js";

test("il Nazionale vede tutti gli elenchi gestionali nel menu condiviso", () => {
  assert.deepEqual(vociMenuPerRuolo("nazionale").map((voce) => voce.rotta), [
    "/dashboard", "/sottoscrittori", "/attuatori", "/aziende", "/pratiche", "/prodotti",
  ]);
});

test("gli elenchi riservati al Nazionale non sono mostrati agli altri ruoli", () => {
  for (const ruolo of ["aderente", "regionale", "provinciale", "utente", "sconosciuto", "", null, undefined]) {
    assert.deepEqual(vociMenuPerRuolo(ruolo).map((voce) => voce.rotta), [
      "/dashboard", "/sottoscrittori",
    ], `menu per ruolo ${String(ruolo)}`);
  }
});
