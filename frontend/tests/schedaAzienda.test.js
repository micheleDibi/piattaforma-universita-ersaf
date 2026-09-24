import { afterEach, test } from "node:test";
import assert from "node:assert/strict";
import {
  caricaPadreAzienda,
  nomeAzienda,
  noteCampiAzienda,
  pivaNonConforme,
  sottotitoloAzienda,
} from "../src/lib/schedaAzienda.js";
import { PROPRIETA_CAMPI, SEZIONI_AZIENDA } from "../src/config/campiAzienda.js";
import { STILI_AZIENDA } from "../src/config/styles/azienda.js";

const PADRE = { azienda_id: 7, azienda_ragione_sociale: "BETA SPA" };

test("sottotitolo: ragione sociale e padre, come nel design", () => {
  assert.equal(
    sottotitoloAzienda("ALFA SRL", PADRE),
    "ALFA SRL · Figlia di BETA SPA",
  );
});

test("sottotitolo: azienda radice o padre in caricamento, solo la ragione sociale", () => {
  assert.equal(sottotitoloAzienda("ALFA SRL", null), "ALFA SRL");
  assert.equal(sottotitoloAzienda("ALFA SRL", undefined), "ALFA SRL");
});

test("sottotitolo: padre senza ragione sociale mostra l'id; niente da mostrare da undefined", () => {
  assert.equal(
    sottotitoloAzienda("ALFA", { azienda_id: 12, azienda_ragione_sociale: null }),
    "ALFA · Figlia di Azienda #12",
  );
  assert.equal(sottotitoloAzienda("", null), undefined);
  assert.equal(sottotitoloAzienda(null, undefined), undefined);
  assert.equal(sottotitoloAzienda("", PADRE), "Figlia di BETA SPA");
});

test("nomeAzienda: ragione sociale oppure Azienda #id", () => {
  assert.equal(nomeAzienda(PADRE), "BETA SPA");
  assert.equal(nomeAzienda({ azienda_id: 3, azienda_ragione_sociale: "" }), "Azienda #3");
});

test("pivaNonConforme: vuota e 11 cifre vanno bene, 10 cifre e lettere no", () => {
  assert.equal(pivaNonConforme(""), false);
  assert.equal(pivaNonConforme(undefined), false);
  assert.equal(pivaNonConforme("12345678901"), false);
  assert.equal(pivaNonConforme("1234567890"), true);
  assert.equal(pivaNonConforme("1234567890A"), true);
  assert.equal(pivaNonConforme("123456789012"), true);
});

test("note: la partita IVA non conforme ha una nota sola, dal server o dal controllo in tempo reale", () => {
  const anomalie = ["Partita IVA non conforme (deve essere di 11 cifre numeriche)"];
  const salvati = { azienda_partitaIVA: "1234567890" };
  assert.deepEqual(noteCampiAzienda(anomalie, salvati, salvati), {
    azienda_partitaIVA: ["Deve contenere 11 cifre numeriche"],
  });
  // Mentre si scrive resta la nota del controllo in tempo reale...
  assert.deepEqual(noteCampiAzienda(anomalie, { azienda_partitaIVA: "123456789" }, salvati), {
    azienda_partitaIVA: ["Deve contenere 11 cifre numeriche"],
  });
  // ...e sparisce appena il valore arriva a 11 cifre.
  assert.deepEqual(noteCampiAzienda(anomalie, { azienda_partitaIVA: "12345678902" }, salvati), {});
});

test("note: senza anomalie (creazione rapida) resta solo il controllo in tempo reale", () => {
  assert.deepEqual(noteCampiAzienda(undefined, { azienda_partitaIVA: "123" }, { azienda_partitaIVA: "123" }), {
    azienda_partitaIVA: ["Deve contenere 11 cifre numeriche"],
  });
  assert.deepEqual(noteCampiAzienda(null, { azienda_partitaIVA: "" }, {}), {});
});

test("note: codice fiscale duplicato visibile finche' il campo non cambia", () => {
  const anomalie = ["Codice Fiscale duplicato con: ALFA SRL"];
  const salvati = { azienda_codiceFiscale: "90000000001" };
  assert.deepEqual(noteCampiAzienda(anomalie, salvati, salvati), {
    azienda_codiceFiscale: ["Duplicato con un'altra azienda"],
  });
  assert.deepEqual(noteCampiAzienda(anomalie, { azienda_codiceFiscale: "90000000002" }, salvati), {});
});

const fetchOriginale = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = fetchOriginale;
});

function rispondi(...risposte) {
  const richieste = [];
  globalThis.fetch = async (url) => {
    richieste.push(String(url));
    return risposte.shift();
  };
  return richieste;
}

const json = (corpo, status = 200) =>
  new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });

test("caricaPadreAzienda: azienda radice", async () => {
  const richieste = rispondi(json({ azienda_id: 5, azienda_padre_id: null }));
  assert.equal(await caricaPadreAzienda(5), null);
  assert.match(richieste[0], /\/aziende-xcod\/5\/padre$/);
  assert.equal(richieste.length, 1);
});

test("caricaPadreAzienda: legge la scheda del padre", async () => {
  const richieste = rispondi(json({ azienda_id: 5, azienda_padre_id: 7 }), json(PADRE));
  assert.deepEqual(await caricaPadreAzienda(5), PADRE);
  assert.match(richieste[1], /\/aziende\/7$/);
});

test("caricaPadreAzienda: padre non leggibile, resta l'id", async () => {
  rispondi(json({ azienda_id: 5, azienda_padre_id: 7 }), json({ detail: "Azienda non trovata." }, 404));
  assert.deepEqual(await caricaPadreAzienda(5), { azienda_id: 7, azienda_ragione_sociale: null });
});

test("caricaPadreAzienda: errore del server sull'arco", async () => {
  rispondi(json({ detail: "Errore interno." }, 500));
  await assert.rejects(caricaPadreAzienda(5));
});

test("finestra di creazione rapida: IBAN e BIC con le colonne di Coordinate bancarie", () => {
  const bancari = Object.fromEntries(
    SEZIONI_AZIENDA.find(({ chiave }) => chiave === "bancari").campi,
  );
  for (const [nome, colonne] of Object.entries(bancari))
    assert.equal(PROPRIETA_CAMPI[nome].colonneFinestra, colonne, nome);
});

test("asterisco degli obbligatori a 600 nella scheda e nella finestra di creazione rapida", () => {
  for (const chiave of ["schedaModulo", "grigliaFinestra"])
    assert.match(STILI_AZIENDA[chiave], /(^|\s)\[&_label>b\]:font-semibold(\s|$)/, chiave);
});

test("convenzioni: la cella non prevista e' posizionata, il testo sr-only non esce dalla tabella", () => {
  assert.match(STILI_AZIENDA.cellaNonPrevista, /(^|\s)relative(\s|$)/);
  assert.match(STILI_AZIENDA.cellaPercentuale, /(^|\s)relative(\s|$)/);
});
