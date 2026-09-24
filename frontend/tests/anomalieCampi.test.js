import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  anomaliePerCampo,
  DUPLICATI_CLIENTE,
  noteVisibili,
} from "../src/lib/anomalieCampi.js";

test("cliente: le note brevi di codice fiscale, email e cellulare, come nell'esempio del design", () => {
  const note = anomaliePerCampo([
    "Codice fiscale non valido: carattere di controllo errato.",
    "Email duplicato con: Mario Rossi, Mario Rossi",
    "Cellulare duplicato con: Mario Rossi, Mario Rossi, Mario Rossi, Anna Bianchi, Luca Verdi, Paolo Neri",
  ], "cliente");
  assert.deepEqual(note, {
    codiceFiscale: ["Carattere di controllo errato"],
    email: ["Duplicata con 2 anagrafiche"],
    cellulare: ["Duplicato con 6 anagrafiche"],
  });
});

test("cliente: i nominativi ripetuti contano una volta ciascuno", () => {
  const note = anomaliePerCampo(["Telefono duplicato con: Mario Rossi, Mario Rossi"], "cliente");
  assert.deepEqual(note, { telefono: ["Duplicato con 2 anagrafiche"] });
});

test("cliente: con una sola anagrafica la nota e' al singolare, al femminile per PEC ed email", () => {
  assert.deepEqual(anomaliePerCampo(["PEC duplicato con: Giulia Esempio"], "cliente"),
    { pec: ["Duplicata con un'altra anagrafica"] });
  assert.deepEqual(anomaliePerCampo(["Email duplicato con: Giulia Esempio"], "cliente"),
    { email: ["Duplicata con un'altra anagrafica"] });
  assert.deepEqual(anomaliePerCampo(["Cellulare duplicato con: Giulia Esempio"], "cliente"),
    { cellulare: ["Duplicato con un'altra anagrafica"] });
});

test("cliente: il numero di documento duplicato va sul campo nDocumento", () => {
  assert.deepEqual(anomaliePerCampo(["Numero documento duplicato con: Mario Rossi, cliente #12"], "cliente"),
    { nDocumento: ["Duplicato con 2 anagrafiche"] });
});

test("cliente: le tre frasi del codice fiscale diventano note senza punto e con l'iniziale maiuscola", () => {
  const note = anomaliePerCampo([
    "Codice fiscale non valido: carattere di controllo errato.",
    "Codice fiscale non valido: deve essere lungo 16 caratteri.",
    "Codice fiscale non valido: formato non conforme.",
  ], "cliente");
  assert.deepEqual(note, {
    codiceFiscale: ["Carattere di controllo errato", "Deve essere lungo 16 caratteri", "Formato non conforme"],
  });
});

test("cliente: email non valida", () => {
  assert.deepEqual(anomaliePerCampo(["Email non valida: formato non conforme."], "cliente"),
    { email: ["Formato non conforme"] });
});

test("cliente: codice fiscale non valido e duplicato insieme danno due note, nell'ordine del backend", () => {
  const note = anomaliePerCampo([
    "Codice fiscale duplicato con: Mario Rossi",
    "Codice fiscale non valido: formato non conforme.",
  ], "cliente");
  assert.deepEqual(note, { codiceFiscale: ["Duplicato con un'altra anagrafica", "Formato non conforme"] });
});

test("frasi sconosciute, null, undefined e [] non producono note", () => {
  assert.deepEqual(anomaliePerCampo(["Qualcosa di nuovo", ""], "cliente"), {});
  assert.deepEqual(anomaliePerCampo(null, "cliente"), {});
  assert.deepEqual(anomaliePerCampo(undefined, "azienda"), {});
  assert.deepEqual(anomaliePerCampo([], "azienda"), {});
  assert.deepEqual(anomaliePerCampo(["Partita IVA mancante"], "altro"), {});
});

test("le frasi di un'entita' non valgono per l'altra", () => {
  assert.deepEqual(anomaliePerCampo([
    "Codice fiscale non valido: formato non conforme.",
    "Email duplicato con: Giulia Esempio",
  ], "azienda"), {});
  assert.deepEqual(anomaliePerCampo([
    "Codice Fiscale mancante",
    "Codice Fiscale duplicato con: ALFA SRL",
    "Partita IVA mancante",
    "Partita IVA non conforme (deve essere di 11 cifre numeriche)",
  ], "cliente"), {});
});

test("azienda: le quattro regole, con il duplicato singolo e multiplo", () => {
  assert.deepEqual(anomaliePerCampo(["Codice Fiscale mancante", "Partita IVA mancante"], "azienda"), {
    azienda_codiceFiscale: ["Da compilare"],
    azienda_partitaIVA: ["Da compilare"],
  });
  assert.deepEqual(anomaliePerCampo([
    "Codice Fiscale duplicato con: ALFA SRL",
    "Partita IVA non conforme (deve essere di 11 cifre numeriche)",
  ], "azienda"), {
    azienda_codiceFiscale: ["Duplicato con un'altra azienda"],
    azienda_partitaIVA: ["Deve contenere 11 cifre numeriche"],
  });
  assert.deepEqual(anomaliePerCampo(["Codice Fiscale duplicato con: ALFA SRL, BETA SPA"], "azienda"),
    { azienda_codiceFiscale: ["Duplicato con altre aziende"] });
});

test("noteVisibili: la nota sparisce appena il valore cambia; trim e campi assenti", () => {
  const note = { email: ["Duplicata con 2 anagrafiche"], cellulare: ["Duplicato con 6 anagrafiche"], pec: ["x"] };
  const salvati = { email: "m.rossi@esempio.it", cellulare: "3330000000" };
  assert.deepEqual(noteVisibili(note, { email: " m.rossi@esempio.it ", cellulare: "3330000001" }, salvati),
    { email: ["Duplicata con 2 anagrafiche"], pec: ["x"] });
  assert.deepEqual(noteVisibili(note, { email: "", cellulare: "3330000000", pec: "nuova@pec.it" }, salvati),
    { cellulare: ["Duplicato con 6 anagrafiche"] });
  assert.deepEqual(noteVisibili(undefined, {}, {}), {});
});

// Allineamento con il backend: se una frase cambia li', le note spariscono in
// silenzio. node --test non importa Python: si legge il sorgente.
const sorgente = (percorso) =>
  readFileSync(new URL(`../../backend/src/${percorso}`, import.meta.url), "utf8");

test("le frasi riconosciute esistono ancora nel backend", () => {
  const schemi = sorgente("clienti/schemas.py");
  for (const frase of [
    "Codice fiscale non valido: carattere di controllo errato.",
    "Codice fiscale non valido: deve essere lungo 16 caratteri.",
    "Codice fiscale non valido: formato non conforme.",
    "Email non valida: formato non conforme.",
  ]) assert.ok(schemi.includes(`"${frase}"`), frase);

  const duplicati = sorgente("clienti/anomalie.py");
  assert.ok(duplicati.includes("duplicato con: {', '.join(altri)}"), "formato dei duplicati dei clienti");
  for (const etichetta of Object.keys(DUPLICATI_CLIENTE)) {
    assert.ok(duplicati.includes(`: "${etichetta}"`), `etichetta ${etichetta}`);
  }

  const aziende = sorgente("aziende/routers.py");
  for (const frase of [
    '"Codice Fiscale mancante"',
    'f"Codice Fiscale duplicato con: {elenco}"',
    'elenco = ", ".join(omonime)',
    '"Partita IVA mancante"',
    '"Partita IVA non conforme',
  ]) assert.ok(aziende.includes(frase), frase);
});
