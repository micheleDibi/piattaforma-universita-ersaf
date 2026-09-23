import { test } from "node:test";
import assert from "node:assert/strict";
import { vociMenuPerRuolo } from "../src/config/routes/rotte.js";

test("il Nazionale vede tutti gli elenchi gestionali", () => {
  assert.deepEqual(vociMenuPerRuolo("nazionale").map((voce) => voce.rotta), [
    "/dashboard", "/sottoscrittori", "/attuatori", "/aziende", "/pratiche", "/prodotti",
  ]);
});

test("Regionale e Provinciale vedono attuatori, aziende e pratiche ma non i prodotti formativi", () => {
  for (const ruolo of ["regionale", "provinciale"]) {
    assert.deepEqual(vociMenuPerRuolo(ruolo).map((voce) => voce.rotta), [
      "/dashboard", "/sottoscrittori", "/attuatori", "/aziende", "/pratiche",
    ], `menu per ruolo ${ruolo}`);
  }
});

test("l'Aderente vede le pratiche ma non attuatori, aziende o prodotti formativi", () => {
  assert.deepEqual(vociMenuPerRuolo("aderente").map((voce) => voce.rotta), [
    "/dashboard", "/sottoscrittori", "/pratiche",
  ]);
});

test("gli altri ruoli vedono dashboard, sottoscrittori e aziende ma non attuatori, pratiche o prodotti formativi", () => {
  for (const ruolo of ["utente", "operatore", "consulente", "sconosciuto", "", null, undefined]) {
    assert.deepEqual(vociMenuPerRuolo(ruolo).map((voce) => voce.rotta), [
      "/dashboard", "/sottoscrittori", "/aziende",
    ], `menu per ruolo ${String(ruolo)}`);
  }
});
