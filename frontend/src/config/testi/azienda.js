/**
 * Scheda dell'azienda ("Modifica azienda", "Nuova azienda"), finestra "cambia
 * padre" e scheda Azienda di un attuatore con la creazione rapida.
 */
export const TESTI_AZIENDA = {
  titoloNuova: "Nuova azienda",
  titoloModifica: "Modifica azienda",
  ritorno: "Aziende",
  caricamento: "Caricamento in corso...",
  // Sottotitolo in modifica: "Ragione sociale · Figlia di Padre".
  separatoreSottotitolo: " · ",
  figliaDi: (padre) => `Figlia di ${padre}`,
  // Azienda di cui il server non restituisce la ragione sociale.
  senzaNome: (id) => `Azienda #${id}`,
  annulla: "Annulla",
  salva: "Salva",
  salvaModifiche: "Salva modifiche",
  salvataggio: "Salvataggio...",
  // Valore assente in sola lettura e combinazione non prevista.
  trattino: "—",

  campi: {
    azienda_ragione_sociale: "Ragione sociale",
    azienda_partitaIVA: "Partita IVA",
    azienda_codiceFiscale: "Codice fiscale",
    azienda_fatturazioneSDI: "Codice SDI",
    azienda_codice_nazionale: "Codice nazionale",
    azienda_via: "Via",
    azienda_civico: "Civico",
    azienda_CAP: "CAP",
    azienda_citta: "Città",
    azienda_provincia: "Prov.",
    azienda_email: "Email",
    azienda_pec: "PEC",
    azienda_telefono: "Telefono",
    azienda_sitoWeb: "Sito web",
    azienda_iban: "IBAN",
    azienda_codice_bic: "Codice BIC",
  },

  segnaposti: {
    azienda_fatturazioneSDI: "7 caratteri",
    azienda_pec: "nome@pec.it",
    azienda_iban: "IT00 X000 0000 0000 0000 0000 000",
    azienda_codice_bic: "XXXXITXX",
  },

  sezioni: {
    anagrafici: {
      titolo: "Dati anagrafici",
      descrizione: "Identificazione fiscale e codici dell'azienda.",
    },
    sede: { titolo: "Sede legale", descrizione: "Indirizzo completo della sede." },
    contatti: {
      titolo: "Contatti",
      descrizione: "Recapiti per comunicazioni e fatturazione.",
    },
    bancari: {
      titolo: "Coordinate bancarie",
      descrizione: "Conto per accrediti e pagamenti.",
    },
    gerarchia: {
      titolo: "Gerarchia",
      descrizione: "Azienda a cui questa è collegata.",
    },
    convenzioni: {
      titolo: "Convenzioni universitarie",
      descrizione: "Percentuali applicate per ateneo e tipologia di corso.",
    },
  },

  gerarchia: {
    etichetta: "Azienda padre",
    caricamento: "Caricamento...",
    radice: "Nessuna (azienda radice)",
    cambia: "Cambia padre",
  },

  convenzioni: {
    // Titolo nella scheda Azienda di un attuatore, dove sono in sola lettura.
    titoloAttuatore: "Dettaglio convenzioni universitarie",
    etichettaTabella: "Percentuali delle convenzioni universitarie",
    ateneo: "Ateneo",
    tipologie: ["Lauree", "Master", "Perfezionamenti"],
    nonPrevista: "Non prevista",
    // Unita' di misura accanto ai valori.
    percento: "%",
    etichettaCampo: (ateneo, tipologia) => `${ateneo} - ${tipologia}`,
    salva: "Salva percentuali",
  },

  // Conferma chiesta dal server (409) prima di azzerare delle percentuali.
  azzeramento: {
    messaggio: "Alcune percentuali verranno azzerate. Continuare?",
    conferma: "Conferma",
    annulla: "Annulla",
  },

  finestraPadre: {
    titolo: "Seleziona Nuova Azienda Padre",
    chiudi: "Chiudi selezione azienda padre",
    chiudiBreve: "Chiudi",
    cerca: "Cerca per ragione sociale...",
    rendiRadice: "Rendi radice (nessun padre)",
    colonne: ["Ragione sociale", "Partita IVA", "Città", "Azione"],
    seleziona: "Seleziona",
    nessuna: "Nessuna azienda trovata.",
    aggiornamento: "Aggiornamento in corso...",
    erroreRecupero: "Errore nel recupero delle aziende",
  },

  attuatore: {
    etichettaRicerca: "Partita IVA",
    segnapostoRicerca: "11 cifre",
    pivaIncompleta: "Inserisci 11 cifre.",
    ricercaInCorso: "Ricerca in corso...",
    cerca: "Cerca azienda",
    cambia: "Cambia azienda",
    rimuovi: "Rimuovi associazione",
    confermaRimozione: "Rimuovere l'azienda associata a questo attuatore?",
    titoloCreazione: "Nessuna azienda trovata con questa Partita IVA",
    descrizioneCreazione:
      "Compila i dati per crearla: verrà associata automaticamente a questo attuatore.",
    creazione: "Creazione...",
    crea: "Crea e associa",
  },
};
