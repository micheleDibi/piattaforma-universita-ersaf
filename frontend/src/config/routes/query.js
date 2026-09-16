import { idValido } from "./percorsi.js";
const testo = (predefinito = "") => ({ predefinito });
const scelta = (valori, predefinito = "") => ({ predefinito,
  leggi: ([valore]) => valori.includes(valore) ? valore : predefinito });
const id = { predefinito: "", leggi: ([valore]) => idValido(valore) ? valore : "" };
export const QUERY_CLIENTI = { ricerca: testo(), ruolo: scelta(["Aderente", "Regionale", "Provinciale", "Nazionale"]) };
export const QUERY_AZIENDE = { ricerca: testo() };
export const QUERY_PRODOTTI = { ricerca: testo(), universita: testo("Tutte le università"),
  tipo: testo("Tutti i tipi"), attivo: scelta(["Sì", "No"], "Tutti") };
export const QUERY_PRATICHE = { ricerca: testo(), stato: id, percorso: id,
  studenti: { predefinito: [], leggi: valori => [...new Set(valori.filter(idValido))].slice(0, 100).map(Number) } };
export const QUERY_ANAGRAFICA = { scheda: scelta(["dati-principali", "curriculum", "utente", "esami", "prevalutazioni"], "dati-principali") };
export const QUERY_PROFILO = { scheda: scelta(["dati-principali", "utente", "sicurezza"], "dati-principali") };
