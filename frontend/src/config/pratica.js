import { paginaStudenti, paginaPercorsi } from "../lib/opzioniPratica.js";

export const SELEZIONE_STUDENTE = { titolo: "Studente", endpoint: "/clienti/?solo_utenti=true",
  multipla: false, segnaposto: "Cerca per nome, cognome o codice", estrai: paginaStudenti };
export const SELEZIONE_EMITTENTE = { titolo: "Aderente emittente", endpoint: "/clienti/?ruolo_codice=Aderente",
  multipla: false, segnaposto: "Cerca l’aderente", estrai: paginaStudenti };
export const SELEZIONE_PERCORSO = { titolo: "Percorso formativo", endpoint: "/listini-testa/",
  multipla: false, segnaposto: "Cerca per titolo o codice", estrai: paginaPercorsi };

export const CAMPI_PRATICA = [
  { nome: "pratica_numero", label: "Numero pratica", maxLength: 45, required: true },
  { nome: "pratica_annoAccademico", label: "Anno accademico", maxLength: 45 },
  { nome: "pratica_sedeErogazione", label: "Sede di erogazione", maxLength: 255 },
  { nome: "pratica_prezzo", label: "Prezzo (€)", type: "number", min: 0, step: "any", required: true },
];
