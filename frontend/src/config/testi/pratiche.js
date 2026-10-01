// Pagina Pratiche (/pratiche senza universita' scelta): striscia dei totali e
// una tabella per ateneo con le pratiche per tipologia di corso e stato.
export const TESTI_PANNELLO_PRATICHE = {
  titolo: "Pratiche",
  descrizione: "Numero di pratiche per ateneo, tipologia di corso e stato.",
  caricamento: "Caricamento pratiche…",
  erroreCaricamento: "Errore nel caricamento delle pratiche",
  senzaAbilitazione: "Non hai l'abilitazione generale alle pratiche universitarie.",
  totalePratiche: "Totale pratiche",
  tipologia: "Tipologia",
  totale: "Totale",
  totaleAteneo: "Totale ateneo",
  // Etichette brevi delle colonne, per chiave di STATI_PANNELLO.
  stati: {
    bozza: "Bozza",
    lavorazione: "In lavorazione",
    attesa: "In attesa di modifica",
    conclusa: "Conclusa",
    caricata: "Caricata",
    rifiutata: "Rifiutata",
  },
  riepilogoAteneo: (pratiche, tipologie) =>
    `${pratiche} ${pratiche === 1 ? "pratica" : "pratiche"} · ${tipologie} ${
      tipologie === 1 ? "tipologia" : "tipologie"
    }`,
  // Nome accessibile di una riga e del totale dell'ateneo: per chi usa un
  // lettore di schermo i numeri delle colonne non hanno intestazione.
  // `stati` e' il risultato di elencoStati: "Bozza 3, Conclusa 12, …".
  descriviTipologia: (tipologia, pratiche, stati) =>
    `${tipologia}: ${pratiche} ${pratiche === 1 ? "pratica" : "pratiche"} (${stati})`,
  elencoStati: (voci) => voci.map(([stato, n]) => `${stato} ${n}`).join(", "),
};

// Modale di selezione dello studente nella scheda pratica: stesse verifiche
// (email, cellulare, diploma) e stesso comportamento colonna Stato
// dell'elenco Sottoscrittori.
export const TESTI_MODALE_STUDENTE = {
  titolo: "Seleziona lo studente",
  segnaposto: "Cerca per nome e cognome",
  colonne: { codiceFiscale: "Codice fiscale", denominazione: "Denominazione", stato: "Stato", azioni: "Azioni" },
  modifica: "Modifica",
  confermaModifica: "Sei sicuro di voler procedere con la modifica del sottoscrittore? In questo modo le modifiche effettuate sulla pratica non salvate andranno perse.",
  conferma: "Conferma",
  annulla: "Annulla",
  caricamento: "Ricerca in corso…",
  vuoto: "Nessun sottoscrittore trovato.",
  mostraAltri: "Mostra altri",
  riprova: "Riprova",
  chiudi: "Chiudi",
  nonSelezionabile: "Non selezionabile: mancano una o più verifiche (email, cellulare o diploma).",
};

// Modale di selezione del percorso formativo nella scheda pratica: elenco
// filtrato per università e tipo di corso, solo prodotti attivi con un
// listino valido oggi. Singola per la maggior parte dei tipi di corso,
// multipla solo per Corsi Singoli (vedi ModaleSelezionePercorso.jsx).
export const TESTI_MODALE_PERCORSO = {
  titolo: "Seleziona il percorso formativo",
  titoloMultiplo: "Seleziona i corsi",
  segnaposto: "Cerca per titolo o codice",
  colonne: { codice: "Codice", denominazione: "Denominazione", prezzo: "Prezzo (€)", cfu: "CFU" },
  caricamento: "Ricerca in corso…",
  vuoto: "Nessun percorso formativo trovato.",
  mostraAltri: "Mostra altri",
  riprova: "Riprova",
  chiudi: "Chiudi",
  conferma: "Conferma",
  scelti: (n) => `${n} ${n === 1 ? "corso scelto" : "corsi scelti"}`,
  totale: (importo) => `Totale: ${importo} €`,
};
