import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  costruisciPannello,
  ORDINE_TIPOLOGIE,
  percorsoTipologia,
  STATI_PANNELLO,
} from "../src/lib/pannelloPratiche.js";
import { TESTI_PANNELLO_PRATICHE as testi } from "../src/config/testi/pratiche.js";

// configPratiche.js importa i loghi, che Node non sa caricare: si leggono i
// blocchi veri sostituendo ogni import di un'immagine con il suo nome.
const sorgente = readFileSync(new URL("../src/lib/configPratiche.js", import.meta.url), "utf8")
  .replace(/^import (\w+) from "[^"]+\.png";$/gm, 'const $1 = "$1";');
const { BLOCCHI_PRATICHE } = await import(
  `data:text/javascript,${encodeURIComponent(sorgente)}`
);

const TUTTI = { abilPraticheUniv: true, ecampus: true, link_campus: true, corsi_speciali: true, a4u: true };
const ID_STATO = Object.fromEntries(STATI_PANNELLO.map((s) => [s.chiave, s.id]));

function gruppo(universita, tipoCorso, stato, totale) {
  return { nome_universita_id: universita, listino_tipo_corso_id: tipoCorso,
    pratica_stato_id: ID_STATO[stato], totale };
}

function ateneo(pannello, chiave) {
  return pannello.atenei.find((a) => a.chiave === chiave);
}

function riga(pannello, chiaveAteneo, chiaveRiga) {
  return ateneo(pannello, chiaveAteneo).righe.find((r) => r.chiave === chiaveRiga);
}

test("le colonne sono i sei stati del design, nel suo ordine e con le sue etichette", () => {
  assert.deepEqual(STATI_PANNELLO.map((s) => s.id), [6, 4, 2, 3, 1, 5]);
  assert.deepEqual(STATI_PANNELLO.map((s) => testi.stati[s.chiave]),
    ["Bozza", "In lavorazione", "In attesa di modifica", "Conclusa", "Caricata", "Rifiutata"]);
});

test("gli atenei e le righe seguono l'ordine del design", () => {
  const pannello = costruisciPannello(BLOCCHI_PRATICHE, [], TUTTI);
  assert.deepEqual(pannello.atenei.map((a) => a.titolo), [
    "Università Telematica eCampus", "Link Campus University", "SSML Lamezia Terme", "Avatar4University",
  ]);
  assert.deepEqual(pannello.atenei.map((a) => a.righe.map((r) => r.label)), [
    ["Prevalutazione", "Corso di Laurea", "Master", "Corsi di Perfezionamento",
      "Formazione ed Alta Formazione", "Corsi Singoli"],
    ["Corsi di Perfezionamento", "Corsi Singoli"],
    ["Prevalutazione", "Corso di Laurea", "Master", "Corsi di Perfezionamento",
      "Alta Formazione per Lauree", "Corsi Singoli", "Corsi Speciali"],
    ["Master", "Corsi di Perfezionamento"],
  ]);
  // Ogni pulsante ha il suo posto nell'ordine: un pulsante nuovo va aggiunto.
  for (const blocco of BLOCCHI_PRATICHE) {
    for (const pulsante of blocco.pulsanti) assert.ok(ORDINE_TIPOLOGIE.includes(pulsante.chiave), pulsante.chiave);
  }
});

test("una riga somma i tipi di corso del suo pulsante, per ateneo e per stato", () => {
  const pannello = costruisciPannello(BLOCCHI_PRATICHE, [
    gruppo(1, 1, "conclusa", 10), gruppo(1, 2, "conclusa", 3), gruppo(1, 3, "rifiutata", 2),
    gruppo(1, 6, "bozza", 4), gruppo(1, 7, "bozza", 1),
    gruppo(3, 6, "conclusa", 50), gruppo(3, 7, "conclusa", 7),
    gruppo(2, 8, "conclusa", 99),
  ], TUTTI);
  assert.deepEqual(riga(pannello, "ecampus", "master").celle, [0, 0, 0, 13, 0, 2]);
  assert.deepEqual(riga(pannello, "ecampus", "formazione_alta_formazione").celle, [5, 0, 0, 0, 0, 0]);
  // SSML: "Alta Formazione per Lauree" e' solo il tipo 7; il 6 non ha riga.
  assert.deepEqual(riga(pannello, "ssml", "alta_formazione_lauree").celle, [0, 0, 0, 7, 0, 0]);
  // Link Campus non ha il Corso di Laurea: le sue lauree non compaiono.
  assert.equal(ateneo(pannello, "link_campus").totale, 0);
});

test("la Prevalutazione resta a zero anche se ci sono pratiche senza tipo di corso", () => {
  const pannello = costruisciPannello(BLOCCHI_PRATICHE, [gruppo(1, null, "bozza", 8)], TUTTI);
  assert.deepEqual(riga(pannello, "ecampus", "prevalutazione").celle, [0, 0, 0, 0, 0, 0]);
  assert.equal(pannello.totale, 0);
});

test("i totali sono la somma delle righe e ignorano tipi e stati senza colonna", () => {
  const pannello = costruisciPannello(BLOCCHI_PRATICHE, [
    gruppo(1, 8, "bozza", 2), gruppo(1, 8, "conclusa", 5), gruppo(1, 9, "caricata", 1),
    gruppo(4, 4, "lavorazione", 3), gruppo(3, 10, "rifiutata", 4),
    gruppo(1, 5, "conclusa", 116), gruppo(1, 10, "bozza", 1),
    { nome_universita_id: 1, listino_tipo_corso_id: 8, pratica_stato_id: 99, totale: 40 },
  ], TUTTI);
  const ecampus = ateneo(pannello, "ecampus");
  assert.equal(riga(pannello, "ecampus", "corso_laurea").totale, 7);
  assert.deepEqual(ecampus.somme, [2, 0, 0, 5, 1, 0]);
  assert.equal(ecampus.totale, 8);
  assert.deepEqual(pannello.totaliStati, [2, 3, 0, 5, 1, 4]);
  assert.equal(pannello.totale, 15);
  assert.equal(pannello.totale, pannello.atenei.reduce((t, a) => t + a.totale, 0));
});

test("le righe sono attive solo con l'abilitazione generale e quella dell'ateneo", () => {
  const parziali = costruisciPannello(BLOCCHI_PRATICHE, [], { ...TUTTI, link_campus: false, corsi_speciali: false });
  assert.deepEqual(parziali.atenei.map((a) => a.abilitato), [true, false, false, true]);
  assert.equal(parziali.senzaAbilitazione, false);

  const senza = costruisciPannello(BLOCCHI_PRATICHE, [], { ...TUTTI, abilPraticheUniv: false });
  assert.deepEqual(senza.atenei.map((a) => a.abilitato), [false, false, false, false]);
  assert.equal(senza.senzaAbilitazione, true);
});

test("ogni riga porta all'elenco filtrato, la Prevalutazione alla sua pagina", () => {
  const ecampus = BLOCCHI_PRATICHE[0];
  const pulsante = (chiave) => ecampus.pulsanti.find((p) => p.chiave === chiave);
  assert.equal(percorsoTipologia(ecampus, pulsante("master")),
    "/pratiche?universita=1&tipoCorso=1&tipoCorso=2&tipoCorso=3");
  assert.equal(percorsoTipologia(ecampus, pulsante("prevalutazione")), "/prevalutazioni?universita=1");
  assert.equal(percorsoTipologia(ecampus, { tipo: "pratica", listinoTipoCorsoIds: [4], haFiltroInterno: true }),
    "/pratiche?universita=1&tipoCorso=4&filtroInterno=1");
});

test("il riepilogo dell'ateneo e il nome delle righe accordano singolare e plurale", () => {
  assert.equal(testi.riepilogoAteneo(12, 6), "12 pratiche · 6 tipologie");
  assert.equal(testi.riepilogoAteneo(1, 1), "1 pratica · 1 tipologia");
  assert.equal(testi.riepilogoAteneo(0, 2), "0 pratiche · 2 tipologie");
  assert.equal(testi.descriviTipologia("Master", 1, "Bozza 1"), "Master: 1 pratica (Bozza 1)");
});
