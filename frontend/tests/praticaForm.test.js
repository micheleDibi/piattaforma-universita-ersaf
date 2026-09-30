import { test } from "node:test";
import assert from "node:assert/strict";
import { praticaVuota, payloadPratica, dettaglioAttuale, prezzoAttuale, prezzoPerInput, valoriRinnovo } from "../src/lib/praticaForm.js";
import { opzioneStudente, paginaStudenti, opzionePercorsoConDettaglio, paginaPercorsi } from "../src/lib/opzioniPratica.js";
import { creaPayloadProdotto, aggiungiDettaglio } from "../src/lib/prodottoPayload.js";
import { campiPercorsoVisibili, eContestoCorsiSingoli, eGruppoLauree, CAMPI_RINNOVO } from "../src/config/pratica.js";

const dati = { ...praticaVuota(), pratica_numero: " TEST-42 ", pratica_prezzo: "120.50", pratica_stato_id: "2" };
const scelta = { nuova: true, studente: { id: 17 }, percorso: { id: 42 },
  prodotto: { listTesta_id: 42, nome_universita_id: 8, listino_tipoCorso_id: 9 } };
test("creazione pratica collega cliente e prodotto, senza l'emittente deprecato e senza il codice (lo genera il server)", () => {
  const p = payloadPratica(dati, scelta);
  assert.equal(p.cliente_id, 17);
  assert.equal(p.cliente_emittente_aderente_id, undefined);
  assert.equal(p.listTesta_id, 42);
  assert.equal(p.nome_universita_id, 8);
  assert.equal(p.listino_tipo_corso_id, 9);
  assert.equal(p.pratica_numero, undefined);
  assert.equal(p.pratica_prezzo, "120.50");
  assert.equal(p.utente_id, undefined);
});
test("il campo stato viaggia sempre nel payload (anche in creazione), ma il server lo ignora li' e forza sempre Bozza", () => {
  const p = payloadPratica(dati, scelta);
  assert.equal(p.pratica_stato_id, 2); // valore di dati.pratica_stato_id, ininfluente lato server
});
test("la modifica invia soltanto i campi supportati e permette di svuotare le note; codice e prezzo restano di sola lettura, lo stato no (ma solo il Nazionale lo scrive davvero, vedi backend)", () => {
  const p = payloadPratica({ ...dati, cliente_id: 999, listTesta_id: 999, nome_universita_id: 999,
    pratica_created_by: 1, pratica_missFlag_firma: -1, pratica_note: "" }, { nuova: false });
  assert.deepEqual(Object.keys(p).sort(),
    ["pratica_annoAccademico", "pratica_note", "pratica_rinnPrimoAnno", "pratica_rinnSecondoAnno",
      "pratica_rinnTerzoAnno", "pratica_sedeErogazione", "pratica_stato_id"].sort());
  assert.equal(p.pratica_note, null);
  assert.equal(p.pratica_stato_id, 2);
  // I tre campi viaggiano sempre insieme (mai solo quello toccato): e' cosi'
  // che il server puo' verificare che sia selezionato al piu' un anno.
  assert.equal(p.pratica_rinnPrimoAnno, 0);
  assert.equal(p.pratica_rinnSecondoAnno, 0);
  assert.equal(p.pratica_rinnTerzoAnno, 0);
});
test("non si salva con selezioni mancanti o risposta del percorso precedente", () => {
  for (const variante of [{ studente: null }, { percorso: null },
    { prodotto: { listTesta_id: 99, nome_universita_id: 8 } }, { prodotto: { listTesta_id: 42, nome_universita_id: null } }]) {
    assert.throws(() => payloadPratica(dati, { ...scelta, ...variante }));
  }
});
test("prezzo invalido in creazione non produce scritture ambigue", () => {
  for (const prezzo of ["", "-10", "NaN", "1.234567891", "1,00", "Infinity"]) {
    assert.throws(() => payloadPratica({ ...dati, pratica_prezzo: prezzo }, scelta));
  }
  assert.equal(payloadPratica({ ...dati, pratica_prezzo: "0" }, scelta).pratica_prezzo, "0");
});
test("gli importi Decimal delle pratiche esistenti restano precisi, e validi nel payload di creazione", () => {
  assert.equal(prezzoPerInput("0E-8"), "0.00000000");
  assert.equal(prezzoPerInput("1.23E+2"), "123");
  assert.equal(prezzoPerInput("1E-8"), "0.00000001");
  assert.equal(prezzoPerInput("999999999999.12345678"), "999999999999.12345678");
  assert.equal(payloadPratica({ ...dati, pratica_prezzo: prezzoPerInput("0E-8") }, scelta).pratica_prezzo, "0.00000000");
});
test("prezzo attuale: sceglie il dettaglio valido oggi con la data di inizio piu' recente", () => {
  const oggi = "2026-06-15";
  assert.equal(prezzoAttuale([], oggi), null);
  assert.equal(prezzoAttuale(undefined, oggi), null);
  assert.equal(prezzoAttuale([
    { listDettaglio_dataInizioValidazione: null, listDettaglio_dataFineValidazionoe: "9999-12-31", listDettaglio_prezzo: "100" },
  ], oggi), "100");
  assert.equal(prezzoAttuale([
    { listDettaglio_dataInizioValidazione: "2025-01-01", listDettaglio_dataFineValidazionoe: "2025-12-31", listDettaglio_prezzo: "80" },
    { listDettaglio_dataInizioValidazione: "2026-01-01", listDettaglio_dataFineValidazionoe: "9999-12-31", listDettaglio_prezzo: "100" },
  ], oggi), "100");
  // Non ancora iniziato o gia' concluso: esclusi entrambi.
  assert.equal(prezzoAttuale([
    { listDettaglio_dataInizioValidazione: "2027-01-01", listDettaglio_dataFineValidazionoe: "9999-12-31", listDettaglio_prezzo: "120" },
    { listDettaglio_dataInizioValidazione: "2020-01-01", listDettaglio_dataFineValidazionoe: "2020-12-31", listDettaglio_prezzo: "50" },
  ], oggi), null);
});
test("dettaglio attuale espone anche CFU, tasse e durata, non solo il prezzo", () => {
  const oggi = "2026-06-15";
  const dettaglio = dettaglioAttuale([
    { listDettaglio_dataInizioValidazione: "2026-01-01", listDettaglio_dataFineValidazionoe: "9999-12-31",
      listDettaglio_prezzo: "100", listDettaglio_CFU: 60, listDettaglio_tasse: "16", listDettaglio_durata: 12 },
  ], oggi);
  assert.equal(dettaglio.listDettaglio_CFU, 60);
  assert.equal(dettaglio.listDettaglio_tasse, "16");
  assert.equal(dettaglio.listDettaglio_durata, 12);
  assert.equal(dettaglioAttuale([], oggi), null);
});
test("caratteristiche visibili per il tipo di percorso seguono la tassonomia dei blocchi pratiche", () => {
  assert.deepEqual(campiPercorsoVisibili(1), ["modalita", "durata", "cfu", "livello"]); // Master
  assert.deepEqual(campiPercorsoVisibili(3), ["modalita", "durata", "cfu", "livello"]); // Master classi di concorso
  assert.deepEqual(campiPercorsoVisibili(4), ["modalita", "cfu"]); // Corsi di perfezionamento
  assert.deepEqual(campiPercorsoVisibili(6), ["modalita", "durata", "cfu"]); // Formazione
  assert.deepEqual(campiPercorsoVisibili(7), ["modalita", "durata", "cfu"]); // Alta formazione
  assert.deepEqual(campiPercorsoVisibili(8), ["facolta", "tasse", "tipoLaurea"]); // Lauree
  assert.deepEqual(campiPercorsoVisibili(9), ["cfu", "corsoLaurea"]); // Corsi singoli
  // Percorso docenti e corsi speciali: nessuna caratteristica prevista.
  assert.deepEqual(campiPercorsoVisibili(5), []);
  assert.deepEqual(campiPercorsoVisibili(10), []);
  assert.deepEqual(campiPercorsoVisibili(undefined), []);
});
test("contesto Corsi Singoli: solo il gruppo 9 (Corsi singoli) permette la selezione multipla", () => {
  assert.equal(eContestoCorsiSingoli([9]), true);
  assert.equal(eContestoCorsiSingoli([6, 7]), false); // Formazione ed Alta formazione: gruppo diverso
  assert.equal(eContestoCorsiSingoli([1, 9]), true); // basta che uno dei tipi sia Corsi singoli
  assert.equal(eContestoCorsiSingoli([]), false);
});
test("il rinnovo si mostra solo per il gruppo Lauree", () => {
  assert.equal(eGruppoLauree(8), true); // Lauree
  assert.equal(eGruppoLauree(1), false); // Master
  assert.equal(eGruppoLauree(9), false); // Corsi singoli
  assert.equal(eGruppoLauree(undefined), false);
});
test("i tre campi di rinnovo hanno nome ed etichetta, nell'ordine primo/secondo/terzo anno", () => {
  assert.deepEqual(CAMPI_RINNOVO.map(({ nome }) => nome),
    ["pratica_rinnPrimoAnno", "pratica_rinnSecondoAnno", "pratica_rinnTerzoAnno"]);
});
test("selezionare un anno di rinnovo azzera gli altri due; nessuna selezione li azzera tutti", () => {
  assert.deepEqual(valoriRinnovo("pratica_rinnSecondoAnno"),
    { pratica_rinnPrimoAnno: 0, pratica_rinnSecondoAnno: -1, pratica_rinnTerzoAnno: 0 });
  assert.deepEqual(valoriRinnovo(null),
    { pratica_rinnPrimoAnno: 0, pratica_rinnSecondoAnno: 0, pratica_rinnTerzoAnno: 0 });
});
test("lookup nuovi usano clienti e prodotti completi, mai ID utente", () => {
  assert.deepEqual(opzioneStudente({ cliente_id: 17, utente_id: 999, cliente_nome: "Elena", cliente_cognome: "Bianchi" }), { id: 17, label: "Elena Bianchi", dettaglio: "" });
  assert.equal(paginaStudenti(Array.from({ length: 20 }, (_, cliente_id) => ({ cliente_id }))).altri, true);
});
test("percorso del modale: prezzo e CFU vengono dal dettaglio valido oggi, mai quello scaduto", () => {
  const oggi = "2026-06-15";
  const prodotto = { listTesta_id: 42, listTesta_descrizione: "Corso singolo", listTesta_codice: "CS42",
    dettagli: [
      { listDettaglio_dataInizioValidazione: "2020-01-01", listDettaglio_dataFineValidazionoe: "2020-12-31", listDettaglio_prezzo: "50", listDettaglio_CFU: 3 },
      { listDettaglio_dataInizioValidazione: "2026-01-01", listDettaglio_dataFineValidazionoe: "9999-12-31", listDettaglio_prezzo: "100", listDettaglio_CFU: 6 },
    ] };
  assert.deepEqual(opzionePercorsoConDettaglio(prodotto, oggi),
    { id: 42, codice: "CS42", label: "Corso singolo", prezzo: "100", cfu: 6 });
  assert.equal(opzionePercorsoConDettaglio({ listTesta_id: 1, listTesta_descrizione: "X", dettagli: [] }).prezzo, null);
});
test("paginaPercorsi (usata da Array.map nel modale) non riceve l'indice al posto della data di oggi", () => {
  // Regressione: dati.map(opzionePercorsoConDettaglio) passerebbe anche
  // l'indice di riga come secondo argomento (oggi), rompendo il confronto
  // fra date per ogni riga, non solo la prima. Tre righe, cosi' un indice
  // "innocuo" come 0 non nasconde il difetto.
  const dettaglioValido = (prezzo) => [{ listDettaglio_dataInizioValidazione: "2022-01-01",
    listDettaglio_dataFineValidazionoe: "9999-12-31", listDettaglio_prezzo: prezzo, listDettaglio_CFU: 9 }];
  const prodotti = ["100", "200", "300"].map((prezzo, i) =>
    ({ listTesta_id: i, listTesta_descrizione: `Corso ${i}`, dettagli: dettaglioValido(prezzo) }));
  assert.deepEqual(paginaPercorsi(prodotti).elementi.map((o) => o.prezzo), ["100", "200", "300"]);
});
test("payload Corsi Singoli: ogni corso scelto (compreso il primo) va in corsi_singoli", () => {
  const corsiSelezionati = [{ id: 42, prezzo: "100" }, { id: 43, prezzo: "50" }];
  const p = payloadPratica(dati, { ...scelta, percorso: { id: 42 }, corsiSingoli: true, corsiSelezionati });
  assert.deepEqual(p.corsi_singoli, [{ listTesta_id: 42, prezzo: "100" }, { listTesta_id: 43, prezzo: "50" }]);
  assert.equal(p.listTesta_id, 42); // resta il primo, come per ogni altra pratica
  // Fuori da Corsi Singoli non si invia affatto.
  assert.equal(payloadPratica(dati, scelta).corsi_singoli, undefined);
});
test("estrazione del mapping prodotti conserva null, numeri italiani e validita", () => {
  const campi = { listTesta_livello: "", listino_modalita_id: "", listino_tipoCorso_id: "8", listino_durataLaurea_id: "", listino_facolta_id: "", listino_corsoLaurea_id: "", nome_universita_id: "3" };
  const dettagli = [{ listDettaglio_prezzo: "12,50", listDettaglio_tasse: "0", listDettaglio_durata: "12", listDettaglio_CFU: "60", listDettaglio_dataInizioValidazione: "2026-01-01" }];
  const p = creaPayloadProdotto(campi, dettagli);
  assert.equal(p.listTesta_livello, null);
  assert.equal(p.nome_universita_id, 3);
  assert.equal(p.dettagli[0].listDettaglio_prezzo, 12.5);
  assert.equal(p.dettagli[0].listDettaglio_dataFineValidazionoe, "9999-12-31");
  const aggiunti = aggiungiDettaglio(dettagli, "2026-09-15", "2026-09-14");
  assert.equal(aggiunti[0].listDettaglio_dataFineValidazionoe, "2026-09-14");
  assert.equal(dettagli[0].listDettaglio_dataFineValidazionoe, undefined);
  assert.equal(aggiunti[1].isNew, true);
});
