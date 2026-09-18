import { test } from "node:test";
import assert from "node:assert/strict";
import { vociMenuPerRuolo } from "../src/config/routes/rotte.js";

test("il Nazionale vede gli elenchi gestionali e il nuovo ingresso Pratiche", () => {
  assert.deepEqual(vociMenuPerRuolo("nazionale").map((voce) => voce.rotta), [
    "/dashboard", "/sottoscrittori", "/attuatori", "/aziende", "/pratiche", "/prodotti",
  ]);
});

test("Aziende e visibile a Regionale e Provinciale, non all'Aderente", () => {
  for (const ruolo of ["regionale", "provinciale"]) {
    assert.deepEqual(vociMenuPerRuolo(ruolo).map((voce) => voce.rotta), [
      "/dashboard", "/sottoscrittori", "/aziende",
    ]);
  }
  assert.deepEqual(vociMenuPerRuolo("aderente").map((voce) => voce.rotta), [
    "/dashboard", "/sottoscrittori",
  ]);
});
