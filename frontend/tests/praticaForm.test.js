import { test } from "node:test";
import assert from "node:assert/strict";
import { praticaVuota, payloadPratica, prezzoPerInput } from "../src/lib/praticaForm.js";
import { opzioneStudente, paginaStudenti, paginaPercorsi } from "../src/lib/opzioniPratica.js";
import { creaPayloadProdotto, aggiungiDettaglio } from "../src/lib/prodottoPayload.js";

const dati = { ...praticaVuota(), pratica_numero: " TEST-42 ", pratica_prezzo: "120.50", pratica_stato_id: "2" };
const scelta = { nuova: true, studente: { id: 17 }, emittente: { id: 23 }, percorso: { id: 42 },
  prodotto: { listTesta_id: 42, nome_universita_id: 8, listino_tipoCorso_id: 9 } };
test("creazione pratica collega cliente, emittente e prodotto senza ID predefiniti", () => {
  const p = payloadPratica(dati, scelta);
  assert.equal(p.cliente_id, 17);
  assert.equal(p.cliente_emittente_aderente_id, 23);
  assert.equal(p.listTesta_id, 42);
  assert.equal(p.nome_universita_id, 8);
  assert.equal(p.listino_tipo_corso_id, 9);
  assert.equal(p.pratica_numero, "TEST-42");
  assert.equal(p.pratica_prezzo, "120.50");
  assert.equal(p.utente_id, undefined);
});
test("la modifica invia soltanto i campi supportati e permette di svuotare le note", () => {
  const p = payloadPratica({ ...dati, cliente_id: 999, listTesta_id: 999, nome_universita_id: 999,
    pratica_created_by: 1, pratica_missFlag_firma: -1, pratica_note: "" }, { nuova: false });
  assert.deepEqual(Object.keys(p).sort(), ["pratica_annoAccademico", "pratica_note", "pratica_numero", "pratica_prezzo", "pratica_sedeErogazione", "pratica_stato_id"].sort());
  assert.equal(p.pratica_note, null);
});
test("non si salva con selezioni mancanti o risposta del percorso precedente", () => {
  for (const variante of [{ studente: null }, { emittente: null }, { percorso: null },
    { prodotto: { listTesta_id: 99, nome_universita_id: 8 } }, { prodotto: { listTesta_id: 42, nome_universita_id: null } }]) {
    assert.throws(() => payloadPratica(dati, { ...scelta, ...variante }));
  }
});
test("prezzo e stato invalidi non producono scritture ambigue", () => {
  for (const prezzo of ["", "-10", "NaN", "1.234567891", "1,00", "Infinity"]) {
    assert.throws(() => payloadPratica({ ...dati, pratica_prezzo: prezzo }, scelta));
  }
  assert.throws(() => payloadPratica({ ...dati, pratica_stato_id: "" }, scelta));
  assert.equal(payloadPratica({ ...dati, pratica_prezzo: "0" }, scelta).pratica_prezzo, "0");
});
test("gli importi Decimal delle pratiche esistenti restano precisi e salvabili", () => {
  assert.equal(prezzoPerInput("0E-8"), "0.00000000");
  assert.equal(prezzoPerInput("1.23E+2"), "123");
  assert.equal(prezzoPerInput("1E-8"), "0.00000001");
  assert.equal(prezzoPerInput("999999999999.12345678"), "999999999999.12345678");
  assert.equal(payloadPratica({ ...dati, pratica_prezzo: prezzoPerInput("0E-8") }, { nuova: false }).pratica_prezzo, "0.00000000");
});
test("lookup nuovi usano clienti e prodotti completi, mai ID utente", () => {
  assert.deepEqual(opzioneStudente({ cliente_id: 17, utente_id: 999, cliente_nome: "Elena", cliente_cognome: "Bianchi" }), { id: 17, label: "Elena Bianchi", dettaglio: "" });
  assert.equal(paginaStudenti(Array.from({ length: 20 }, (_, cliente_id) => ({ cliente_id }))).altri, true);
  assert.deepEqual(paginaPercorsi([{ listTesta_id: 42, listTesta_descrizione: "Master", listTesta_codice: "M42" }]),
    { elementi: [{ id: 42, label: "Master", dettaglio: "M42" }], altri: false });
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
