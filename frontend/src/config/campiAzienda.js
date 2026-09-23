// Campi del modulo azienda, condivisi dalla scheda e dal modale di creazione
// rapida. Stanno fuori da CampiAzienda.jsx perche' un file di componente deve
// esportare solo componenti, o il fast refresh di Vite ricarica l'intera pagina.
// Qui c'e' solo la struttura: etichette e segnaposti stanno in
// config/testi/azienda.js.
export const OBBLIGATORI = [
  "azienda_ragione_sociale",
  "azienda_partitaIVA",
  "azienda_codiceFiscale",
  "azienda_via",
  "azienda_citta",
  "azienda_CAP",
  "azienda_provincia",
];

export const FACOLTATIVI = [
  "azienda_civico",
  "azienda_fatturazioneSDI",
  "azienda_email",
  "azienda_pec",
  "azienda_telefono",
  "azienda_sitoWeb",
  "azienda_iban",
  "azienda_codice_bic",
  "azienda_codice_nazionale",
];

export const VUOTO_AZIENDA = Object.fromEntries(
  [...OBBLIGATORI, ...FACOLTATIVI].map((campo) => [campo, ""]),
);

/**
 * Attributi dei campi che non sono semplice testo libero:
 * - input: attributi nativi dell'<input> (la partita IVA accetta solo cifre,
 *   al massimo 11; la provincia e' la sigla di 2 lettere);
 * - solaLettura: il valore lo genera il server (codice nazionale);
 * - monospazio: codici da leggere carattere per carattere;
 * - colonneFinestra: colonne su 6 nella finestra di creazione rapida, dove
 *   gli altri campi ne occupano 3. IBAN e BIC hanno le colonne della sezione
 *   "Coordinate bancarie": su 3 il segnaposto dell'IBAN resta tagliato.
 */
export const PROPRIETA_CAMPI = {
  azienda_partitaIVA: {
    input: { maxLength: 11, inputMode: "numeric", pattern: "[0-9]*" },
  },
  azienda_provincia: { input: { maxLength: 2 } },
  azienda_codice_nazionale: { solaLettura: true, monospazio: true },
  azienda_iban: { monospazio: true, colonneFinestra: 4 },
  azienda_codice_bic: { monospazio: true, colonneFinestra: 2 },
};

// Sezioni della scheda azienda: [campo, colonne occupate su 6]. Titolo e
// descrizione in TESTI_AZIENDA.sezioni[chiave].
export const SEZIONI_AZIENDA = [
  {
    chiave: "anagrafici",
    campi: [
      ["azienda_ragione_sociale", 6],
      ["azienda_partitaIVA", 3],
      ["azienda_codiceFiscale", 3],
      ["azienda_fatturazioneSDI", 3],
      ["azienda_codice_nazionale", 3],
    ],
  },
  {
    chiave: "sede",
    campi: [
      ["azienda_via", 5],
      ["azienda_civico", 1],
      ["azienda_CAP", 2],
      ["azienda_citta", 3],
      ["azienda_provincia", 1],
    ],
  },
  {
    chiave: "contatti",
    campi: [
      ["azienda_email", 3],
      ["azienda_pec", 3],
      ["azienda_telefono", 3],
      ["azienda_sitoWeb", 3],
    ],
  },
  {
    chiave: "bancari",
    campi: [
      ["azienda_iban", 4],
      ["azienda_codice_bic", 2],
    ],
  },
];
