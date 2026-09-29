import { test } from "node:test";
import assert from "node:assert/strict";
import { ROTTE, VOCI_MENU, vociMenuPerRuolo } from "../src/config/routes/rotte.js";
import { TESTI_DASHBOARD } from "../src/config/testi/dashboard.js";
import { descrizioneDashboard, salutoDashboard, scorciatoieDashboard } from "../src/lib/dashboard.js";

const RUOLI = ["nazionale", "regionale", "provinciale", "aderente", "utente", "", null, undefined];

test("le scorciatoie sono il menu del ruolo senza la Dashboard, con la descrizione", () => {
  for (const ruolo of RUOLI) {
    const scorciatoie = scorciatoieDashboard(ruolo);
    const menu = vociMenuPerRuolo(ruolo).filter((voce) => voce.rotta !== ROTTE.dashboard);
    assert.deepEqual(scorciatoie.map((s) => s.rotta), menu.map((v) => v.rotta), String(ruolo));
    assert.deepEqual(scorciatoie.map((s) => s.etichetta), menu.map((v) => v.etichetta), String(ruolo));
    assert.deepEqual(scorciatoie.map((s) => s.icona), menu.map((v) => v.icona), String(ruolo));
    for (const scorciatoia of scorciatoie) assert.ok(scorciatoia.descrizione, scorciatoia.rotta);
  }
});

test("scorciatoie per i 4 ruoli e per gli altri, con EduNews24 in coda", () => {
  const rotte = (ruolo) => scorciatoieDashboard(ruolo).map((s) => s.rotta);
  assert.deepEqual(rotte("nazionale"), ["/sottoscrittori", "/attuatori", "/aziende", "/pratiche", "/prodotti", "/edunews24"]);
  for (const ruolo of ["regionale", "provinciale"]) {
    assert.deepEqual(rotte(ruolo), ["/sottoscrittori", "/attuatori", "/aziende", "/pratiche", "/edunews24"], ruolo);
  }
  assert.deepEqual(rotte("aderente"), ["/sottoscrittori", "/pratiche", "/edunews24"]);
  for (const ruolo of ["utente", "", null, undefined]) {
    assert.deepEqual(rotte(ruolo), ["/sottoscrittori", "/aziende", "/edunews24"], String(ruolo));
  }
});

test("ogni voce del menu tranne la Dashboard ha una descrizione non vuota", () => {
  for (const voce of VOCI_MENU) {
    if (voce.rotta === ROTTE.dashboard) continue;
    const descrizione = TESTI_DASHBOARD.scorciatoie[voce.rotta];
    assert.equal(typeof descrizione, "string", voce.rotta);
    assert.ok(descrizione.trim(), voce.rotta);
  }
  assert.equal(TESTI_DASHBOARD.scorciatoie[ROTTE.dashboard], undefined);
});

test("nessuna descrizione orfana", () => {
  const menu = VOCI_MENU.map((voce) => voce.rotta).filter((rotta) => rotta !== ROTTE.dashboard);
  assert.deepEqual(Object.keys(TESTI_DASHBOARD.scorciatoie).sort(), [...menu].sort());
});

test("il saluto usa solo il nome della sessione", () => {
  assert.equal(salutoDashboard({ nome: "Mario", cognome: "Rossi", username: "mrossi" }), "Buon lavoro, Mario.");
  assert.equal(salutoDashboard({ nome: "  Anna   Maria " }), "Buon lavoro, Anna Maria.");
  assert.equal(salutoDashboard({ nome: "", cognome: "Rossi", username: "mrossi" }), "Buon lavoro.");
  assert.equal(salutoDashboard({ nome: "", cognome: "", username: "mrossi" }), "Buon lavoro.");
  assert.equal(salutoDashboard({ nome: "   " }), "Buon lavoro.");
  assert.equal(salutoDashboard({ nome: 42 }), "Buon lavoro.");
  assert.equal(salutoDashboard(null), "Buon lavoro.");
  assert.equal(salutoDashboard(undefined), "Buon lavoro.");
  assert.equal(descrizioneDashboard({ nome: "Mario" }), "Buon lavoro, Mario. Da qui raggiungi le sezioni della piattaforma.");
  assert.equal(descrizioneDashboard(null), "Buon lavoro. Da qui raggiungi le sezioni della piattaforma.");
});
