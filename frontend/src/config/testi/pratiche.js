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
