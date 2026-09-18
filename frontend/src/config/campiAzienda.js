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
