import { test } from "node:test";
import assert from "node:assert/strict";
import { vociMenuPerRuolo } from "../src/config/routes/rotte.js";

test("il Nazionale vede tutti gli elenchi gestionali", () => {
  assert.deepEqual(vociMenuPerRuolo("nazionale").map((voce) => voce.rotta), [
    "/dashboard", "/sottoscrittori", "/attuatori", "/aziende", "/pratiche", "/prodotti", "/edunews24",
  ]);
});

test("Regionale e Provinciale vedono attuatori, aziende e pratiche ma non i prodotti formativi", () => {
  for (const ruolo of ["regionale", "provinciale"]) {
    assert.deepEqual(vociMenuPerRuolo(ruolo).map((voce) => voce.rotta), [
      "/dashboard", "/sottoscrittori", "/attuatori", "/aziende", "/pratiche", "/edunews24",
    ], `menu per ruolo ${ruolo}`);
  }
});

test("l'Aderente vede le pratiche ma non attuatori, aziende o prodotti formativi", () => {
  assert.deepEqual(vociMenuPerRuolo("aderente").map((voce) => voce.rotta), [
    "/dashboard", "/sottoscrittori", "/pratiche", "/edunews24",
  ]);
});

test("gli altri ruoli vedono dashboard, sottoscrittori e aziende ma non attuatori, pratiche o prodotti formativi", () => {
  for (const ruolo of ["utente", "operatore", "consulente", "sconosciuto", "", null, undefined]) {
    assert.deepEqual(vociMenuPerRuolo(ruolo).map((voce) => voce.rotta), [
      "/dashboard", "/sottoscrittori", "/aziende", "/edunews24",
    ], `menu per ruolo ${String(ruolo)}`);
  }
});

test("EduNews24 è l'ultima voce per ogni ruolo", () => {
  for (const ruolo of ["nazionale", "regionale", "provinciale", "aderente", "utente", "", null, undefined]) {
    const voci = vociMenuPerRuolo(ruolo);
    assert.equal(voci.at(-1).rotta, "/edunews24", `menu per ruolo ${String(ruolo)}`);
    assert.equal(voci.at(-1).etichetta, "EduNews24", `menu per ruolo ${String(ruolo)}`);
    assert.equal(voci.filter((voce) => voce.rotta === "/edunews24").length, 1, `menu per ruolo ${String(ruolo)}`);
  }
});
