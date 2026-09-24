// Scheda di sottoscrittori e attuatori, in modifica e in creazione. I testi
// dei titoli di studio stanno in titoli.js, i segnaposti dei select in
// selezioni.js. Le opzioni dei select sono coppie [valore, etichetta]: il
// valore e' quello salvato nel database e non cambia.

const NOMI = { sottoscrittore: "sottoscrittore", attuatore: "attuatore" };
const nome = (tipoUtente) => NOMI[tipoUtente] ?? NOMI.sottoscrittore;

export const TESTI_ANAGRAFICA = {
  /** "Modifica sottoscrittore", "Nuovo attuatore". */
  titolo: (tipoUtente, modifica) => `${modifica ? "Modifica" : "Nuovo"} ${nome(tipoUtente)}`,
  ritorno: (tipoUtente) => (tipoUtente === "attuatore" ? "Attuatori" : "Sottoscrittori"),
  /** Stato dell'account, nella testata e nella scheda Utente. */
  stato: (attivo) => (attivo ? "Attivo" : "Disattivo"),
  erroreCaricamento: "Impossibile caricare l’anagrafica.",
  sessioneScaduta: "Sessione scaduta. Rifai il login prima di salvare.",
  salvataggioRiuscito: "Modifiche salvate con successo!",
  // Schede: le chiavi sono gli id della query ?scheda=.
  etichettaSchede: "Schede anagrafica",
  schede: {
    "dati-principali": "Dati principali",
    curriculum: "Curriculum formativo",
    utente: "Utente",
    azienda: "Azienda",
    esami: "Esami",
    abilitazioni: "Abilitazioni",
  },
  esamiVuoto: "Nessun esame registrato.",
  inSviluppo: "Sezione in fase di sviluppo",
  schedaCorrente: "Stai visualizzando la scheda:",
  // Barra delle azioni in fondo alla scheda.
  annulla: "Annulla",
  salva: "Salva modifiche",
  crea: (tipoUtente) => `Crea ${nome(tipoUtente)}`,
  // Sezione Ruolo, solo per gli attuatori.
  ruolo: {
    titolo: "Ruolo",
    descrizione: "Livello dell'attuatore nella rete.",
    etichetta: "Ruolo attuatore",
    predefinito: "Aderente (default)",
  },
};

export const TESTI_INFORMAZIONI = {
  titolo: "Informazioni personali",
  descrizione: (tipoUtente) =>
    `Dati anagrafici ${tipoUtente === "attuatore" ? "dell'attuatore" : "del sottoscrittore"}.`,
  nome: "Nome",
  cognome: "Cognome",
  codiceFiscale: "Codice fiscale",
  genere: "Genere",
  generi: [
    ["uomo", "Uomo"],
    ["donna", "Donna"],
  ],
  dataDiNascita: "Data di nascita",
  luogoDiNascita: "Luogo di nascita",
  provDiNascita: "Prov.",
  cittadinanza: "Cittadinanza",
};

export const TESTI_CONTATTI = {
  titolo: "Contatti",
  descrizione: "Email e cellulare sono i recapiti usati per accesso e comunicazioni.",
  attivazione:
    "Verifica email e cellulare per attivare l’account. Le credenziali saranno inviate via email.",
  email: "Email",
  cellulare: "Cellulare",
  /** Pillola del recapito verificato: "Verificata" per l'email. */
  verificato: (tipo) => (tipo === "email" ? "Verificata" : "Verificato"),
  verifica: "Verifica",
  verificatoIl: (data) => `Verificato il ${data}`,
  daSalvare: "Salva le modifiche per verificare questo contatto.",
  altriRecapiti: "Altri recapiti",
  pec: "PEC",
  telefono: "Telefono",
};

export const TESTI_DOCUMENTO = {
  titolo: "Documento",
  descrizione: "Documento di riconoscimento in corso di validità.",
  tipoDocumento: "Tipo documento",
  tipi: [
    ["Carta d'identità", "Carta d'identità"],
    ["Passaporto", "Passaporto"],
    ["Patente", "Patente"],
  ],
  nDocumento: "N° documento",
  comuneDiRilascio: "Comune di rilascio",
  dataInizioRilascio: "Data rilascio",
  dataScadenza: "Data scadenza",
};

export const TESTI_RESIDENZA = {
  residenza: "Residenza",
  domicilio: "Domicilio",
  descrizioneDomicilio: "Solo se diverso dalla residenza.",
  copia: "Copia da residenza",
  // Etichette per suffisso del nome del campo (residenzaIndirizzo, ...).
  campi: {
    Indirizzo: "Indirizzo",
    Civico: "Civico",
    Comune: "Comune",
    Cap: "CAP",
    Provincia: "Prov.",
  },
};

export const TESTI_CURRICULUM = {
  etichetta: "Curriculum formativo",
  schede: {
    titoli: "Titoli",
    immatricolazioni: "Immatricolazioni ed iscrizioni",
    abilitazioni: "Abilitazioni professionali",
    invalidita: "Invalidità",
  },
};

export const TESTI_IMMATRICOLAZIONI = {
  anagrafe: {
    titolo: "Anagrafe Nazionale Studenti",
    descrizione: "Situazione accademica attuale.",
  },
  status: "Status accademico attuale",
  stati: [
    [0, "Non immatricolato"],
    [1, "Immatricolato"],
  ],
  tipoCorso: "Tipo di corso",
  riforme: [
    ["pre_riforma_dm_509_99", "PRE riforma D.M. 509/99"],
    ["post_riforma_dm_509_99", "POST riforma D.M. 509/99"],
  ],
  ateneo: "Ateneo di iscrizione",
  dataImmatricolazione: "Data immatricolazione",
  universita: "Università",
  citta: "Città",
  provincia: "Prov.",
  conclusione: "Conclusione carriera con",
  conclusioni: [
    ["conseguimento_titolo_finale", "conseguimento titolo finale"],
    ["rinuncia", "rinuncia"],
    ["decadenza", "decadenza"],
    ["trasferimento", "Trasferimento"],
  ],
  dataConclusione: "Data conclusione",
  iscrizione: {
    titolo: "Iscrizione in corso",
    descrizione: "Corso a cui è attualmente iscritto.",
  },
  altraUniversita: "Iscritto ad altro corso di studi di altre Università",
  tipo: "Tipo",
  tipi: [
    ["laurea_i_livello", "Laurea I Livello"],
    ["laurea_ii_livello", "Laurea II Livello"],
    ["laurea_ciclo_unico", "Laurea Ciclo Unico"],
    ["master_i_livello", "Master I Livello"],
    ["master_ii_livello", "Master II Livello"],
    ["altro", "Altro"],
  ],
  altro: "In caso di \"Altro\"",
  classeLaurea: "Classe di laurea",
  denominazione: "Denominazione",
  anno: "Anno",
  modalita: "Modalità",
  // Come nel design: nella griglia a 2 colonne basta l'invito breve.
  segnapostoModalita: "Seleziona",
  modalitaCorso: [
    ["full_time", "Full-Time"],
    ["part_time", "Part-Time"],
  ],
};

export const TESTI_ABILITAZIONI = {
  abilitazione: {
    titolo: "Abilitazione e qualifica",
    descrizione: "Titoli professionali conseguiti.",
  },
  professione: "Abilitazione professionale",
  qualifica: "Qualifica professionale",
  data: "Data",
  luogo: "Luogo",
  albo: { titolo: "Albo o elenco" },
  alboElenco: "Albo / elenco",
  forzeOrdine: "Forze dell'ordine",
  convalida: {
    titolo: "Convalida esperienze",
    descrizione: "Esperienze per cui si richiede la convalida.",
  },
  esperienze: {
    universita_attivita_professionalizzanti: "Attività professionalizzanti",
    universita_corsi_di_formazione: "Corsi di formazione",
    universita_altre_attivita_certificate: "Altre attività certificate",
  },
};

export const TESTI_INVALIDITA = {
  titolo: "Dati invalidità",
  descrizione: "Compilare solo se applicabile.",
  percentuale: "Percentuale",
  segnapostoPercentuale: "Es. 75",
  unita: "%",
  tipo: "Tipo di invalidità",
};

export const TESTI_UTENTE = {
  account: {
    titolo: "Account e ruolo",
    descrizione: "Credenziali di accesso e gerarchia.",
  },
  username: "Username",
  stato: "Stato",
  cambiaStato: "Clicca per cambiare stato",
  ruolo: "Ruolo",
  ruoli: [
    ["0", "Utente"],
    ["1", "Aderente"],
    ["2", "Regionale"],
    ["3", "Provinciale"],
    ["4", "Consulente"],
    ["5", "Nazionale"],
    ["6", "Operatore"],
  ],
  padre: "Utente padre",
  cambiaPadre: "Cambia padre",
  accedi: "Accedi con questo utente",
  salva: "Salva utente",
  salvataggio: "Salvataggio...",
  cronologia: "Cronologia",
  creato: "Creato il",
  aggiornato: "Ultimo aggiornamento",
  aggiornatoDa: "Aggiornato da",
  vuoto: "-",
  nessuno: "Nessuno",
  /** Utente senza nome ne' username: resta l'identificativo. */
  identificativo: (id) => `ID: ${id}`,
  nessunUtente: "Nessun utente selezionato.",
  caricamento: "Caricamento in corso...",
  errore: (messaggio) => `Errore: ${messaggio}`,
  padreSenzaUtente: "L'attuatore selezionato non ha un utente associato.",
  ruoloMancante: "Seleziona un ruolo prima di salvare.",
  salvataggioRiuscito: "Modifiche salvate con successo!",
};

// Scheda Abilitazioni dell'attuatore: etichetta per colonna dei flag. L'elenco
// delle colonne sta in SchedaAbilitazioniPratiche.
export const TESTI_ABILITAZIONI_PRATICHE = {
  cliente_abilPraticheUniv: "Abilitazione generale pratiche universitarie",
  cliente_abilitazione_ecampus: "Università Telematica eCampus",
  cliente_abilitazione_link_campus: "Link Campus University",
  cliente_abilitazione_corsi_speciali: "SSML Lamezia Terme",
  cliente_abilitazione_a4u: "Avatar4University",
};
