import { idValido } from "./percorsi.js";
const testo = (predefinito = "") => ({ predefinito });
const scelta = (valori, predefinito = "") => ({
  predefinito,
  leggi: ([valore]) => (valori.includes(valore) ? valore : predefinito),
});
const id = {
  predefinito: "",
  leggi: ([valore]) => (idValido(valore) ? valore : ""),
};
export const QUERY_CLIENTI = {
  ricerca: testo(),
  ruolo: scelta(["Aderente", "Regionale", "Provinciale", "Nazionale", "Operatore"]),
};
export const QUERY_AZIENDE = { ricerca: testo() };
export const QUERY_PRODOTTI = {
  ricerca: testo(),
  universita: testo("Tutte le università"),
  tipo: testo("Tutti i tipi"),
  attivo: scelta(["Sì", "No"], "Tutti"),
};
export const QUERY_PRATICHE = {
  ricerca: testo(),
  numeroPratica: testo(),
  stato: id,
  studenti: {
    predefinito: [],
    leggi: (valori) =>
      [...new Set(valori.filter(idValido))].slice(0, 100).map(Number),
  },
  universita: id,
  tipoCorso: {
    predefinito: [],
    leggi: (valori) => [...new Set(valori.filter(idValido))].map(Number),
  },
  filtroInterno: scelta(["1"], ""),
  tipoSelezionato: id,
};
export const QUERY_ANAGRAFICA = {
  scheda: scelta(
    [
      "dati-principali",
      "curriculum",
      "azienda",
      "utente",
      "esami",
      "prevalutazioni",
      "abilitazioni", // NUOVO
    ],
    "dati-principali",
  ),
};
export const QUERY_PROFILO = {
  scheda: scelta(["dati-principali", "utente", "sicurezza"], "dati-principali"),
};
