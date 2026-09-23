// Campi del modulo azienda, condivisi dalla scheda e dal modale di creazione
// rapida. Stanno fuori da CampiAzienda.jsx perche' un file di componente deve
// esportare solo componenti, o il fast refresh di Vite ricarica l'intera pagina.
export const OBBLIGATORI = [
  ["azienda_ragione_sociale", "Ragione sociale"],
  ["azienda_partitaIVA", "Partita IVA"],
  ["azienda_codiceFiscale", "Codice fiscale"],
  ["azienda_via", "Via"],
  ["azienda_citta", "Città"],
  ["azienda_CAP", "CAP"],
  ["azienda_provincia", "Provincia"],
];

export const FACOLTATIVI = [
  ["azienda_civico", "Civico"],
  ["azienda_fatturazioneSDI", "Codice SDI"],
  ["azienda_email", "Email"],
  ["azienda_pec", "PEC"],
  ["azienda_telefono", "Telefono"],
  ["azienda_sitoWeb", "Sito web"],
  ["azienda_iban", "IBAN"],
  ["azienda_codice_bic", "Codice BIC"],
  ["azienda_codice_nazionale", "Codice nazionale"],
];

export const VUOTO_AZIENDA = Object.fromEntries(
  [...OBBLIGATORI, ...FACOLTATIVI].map(([campo]) => [campo, ""]),
);

// Sezioni della scheda azienda: [campo, colonne occupate su 6].
export const SEZIONI_AZIENDA = [
  {
    titolo: "Dati anagrafici",
    descrizione: "Identificazione fiscale e codici dell'azienda.",
    campi: [
      ["azienda_ragione_sociale", 6],
      ["azienda_partitaIVA", 3],
      ["azienda_codiceFiscale", 3],
      ["azienda_fatturazioneSDI", 3],
      ["azienda_codice_nazionale", 3],
    ],
  },
  {
    titolo: "Sede legale",
    descrizione: "Indirizzo completo della sede.",
    campi: [
      ["azienda_via", 5],
      ["azienda_civico", 1],
      ["azienda_CAP", 2],
      ["azienda_citta", 3],
      ["azienda_provincia", 1],
    ],
  },
  {
    titolo: "Contatti",
    descrizione: "Recapiti per comunicazioni e fatturazione.",
    campi: [
      ["azienda_email", 3],
      ["azienda_pec", 3],
      ["azienda_telefono", 3],
      ["azienda_sitoWeb", 3],
    ],
  },
  {
    titolo: "Coordinate bancarie",
    descrizione: "Conto per accrediti e pagamenti.",
    campi: [
      ["azienda_iban", 4],
      ["azienda_codice_bic", 2],
    ],
  },
];
