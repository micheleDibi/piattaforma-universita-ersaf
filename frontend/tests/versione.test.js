import { test } from "node:test";
import assert from "node:assert/strict";
import { descriviVersione, leggiVersione } from "../src/lib/versione.js";

const descrivi = (ambiente) => descriviVersione(leggiVersione(ambiente));

test("progressivo e data del deploy diventano le due righe del menu", () => {
  assert.deepEqual(descrivi({ VITE_VERSIONE: "117", VITE_AGGIORNATA_IL: "2026-09-16T19:30:00+02:00" }), {
    versione: "Versione 117",
    aggiornamento: "Aggiornata il 16/09/2026 alle 19:30",
  });
});

test("l'ora e' quella di Roma anche se il deploy la scrive in UTC o d'inverno", () => {
  assert.equal(descrivi({ VITE_VERSIONE: "118", VITE_AGGIORNATA_IL: "2026-09-16T17:30:00Z" }).aggiornamento,
    "Aggiornata il 16/09/2026 alle 19:30");
  assert.equal(descrivi({ VITE_VERSIONE: "240", VITE_AGGIORNATA_IL: "2026-12-01T08:05:00Z" }).aggiornamento,
    "Aggiornata il 01/12/2026 alle 09:05");
});

test("fuori dal deploy e' la versione di sviluppo", () => {
  assert.deepEqual(descrivi({}), { versione: "Versione di sviluppo", aggiornamento: null });
  assert.deepEqual(descrivi({ VITE_VERSIONE: "", VITE_AGGIORNATA_IL: "" }), { versione: "Versione di sviluppo", aggiornamento: null });
  assert.equal(leggiVersione(undefined).numero, null);
});

test("valori malformati non producono testi sbagliati", () => {
  assert.equal(descrivi({ VITE_VERSIONE: "12a" }).versione, "Versione di sviluppo");
  assert.deepEqual(descrivi({ VITE_VERSIONE: "117", VITE_AGGIORNATA_IL: "ieri" }), { versione: "Versione 117", aggiornamento: null });
});
