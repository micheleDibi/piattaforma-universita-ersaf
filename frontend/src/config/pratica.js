// pratica_numero, pratica_prezzo, pratica_stato_id e pratica_dataCreazione
// non sono qui: sono sempre di sola lettura (pratica_numero in attesa di una
// logica che lo compili, gli altri tre per le ragioni spiegate dove sono
// definiti), quindi la scheda li tratta a parte in DatiPratica.jsx.
export const CAMPI_PRATICA = [
  { nome: "pratica_annoAccademico", label: "Anno accademico", maxLength: 45 },
  { nome: "pratica_sedeErogazione", label: "Sede di erogazione", maxLength: 255 },
];

// Caratteristiche del percorso formativo mostrate in sola lettura nella
// scheda pratica (CaratteristichePercorso.jsx): quali dipende dal gruppo del
// percorso scelto. listino_tipoCorso_id -> gruppo, stessa tassonomia di
// lib/configPratiche.js (1,2,3 Master; 4 Corsi di perfezionamento; 6,7
// Formazione ed Alta formazione; 8 Lauree; 9 Corsi singoli). I gruppi 5
// (Percorso docenti) e 10 (Corsi speciali) non hanno caratteristiche da
// mostrare qui.
const GRUPPO_PER_TIPO_CORSO = {
  1: "master", 2: "master", 3: "master",
  4: "perfezionamento",
  6: "formazione", 7: "formazione",
  8: "lauree",
  9: "corsiSingoli",
};

const CAMPI_PERCORSO_PER_GRUPPO = {
  master: ["modalita", "durata", "cfu", "livello"],
  perfezionamento: ["modalita", "cfu"],
  formazione: ["modalita", "durata", "cfu"],
  lauree: ["facolta", "tasse", "tipoLaurea"],
  corsiSingoli: ["cfu", "corsoLaurea"],
};

/** Le chiavi dei campi da mostrare per questo listino_tipoCorso_id, nello
 * stesso ordine di CAMPI_PERCORSO_PER_GRUPPO; un array vuoto se il gruppo non
 * ha caratteristiche da mostrare o non e' riconosciuto. */
export function campiPercorsoVisibili(listinoTipoCorsoId) {
  const gruppo = GRUPPO_PER_TIPO_CORSO[listinoTipoCorsoId];
  return gruppo ? CAMPI_PERCORSO_PER_GRUPPO[gruppo] : [];
}

/** Vero se uno dei tipi di corso del contesto di creazione (vedi
 * leggiContestoUrl in lib/schedaPratica.js) è Corsi singoli: l'unico gruppo
 * per cui la selezione del percorso formativo permette più di una scelta
 * (vedi ModaleSelezionePercorso.jsx). */
export function eContestoCorsiSingoli(tipoCorsoIds) {
  return tipoCorsoIds.some((id) => GRUPPO_PER_TIPO_CORSO[id] === "corsiSingoli");
}

/** Vero se il percorso scelto (prodotto.listino_tipoCorso_id) è di tipo
 * Lauree: l'unico gruppo per cui la scheda mostra il rinnovo (vedi
 * DatiPratica.jsx). */
export function eGruppoLauree(listinoTipoCorsoId) {
  return GRUPPO_PER_TIPO_CORSO[listinoTipoCorsoId] === "lauree";
}

// I tre campi si escludono a vicenda: un solo anno di rinnovo alla volta, o
// nessuno (vedi impostaRinnovo in hooks/useSchedaPratica.js e il validatore
// gemello in backend/src/pratiche/rinnovi.py, CAMPI_RINNOVO).
export const CAMPI_RINNOVO = [
  { nome: "pratica_rinnPrimoAnno", label: "Rinnovo primo anno" },
  { nome: "pratica_rinnSecondoAnno", label: "Rinnovo secondo anno" },
  { nome: "pratica_rinnTerzoAnno", label: "Rinnovo terzo anno" },
];

export const ETICHETTE_CAMPI_PERCORSO = {
  modalita: "Modalità di erogazione",
  facolta: "Facoltà",
  durata: "Durata",
  cfu: "CFU",
  tasse: "Tasse (€)",
  livello: "Livello",
  tipoLaurea: "Tipo di Laurea",
  corsoLaurea: "Corso di Laurea",
};
