export const TESTI_ELENCO = {
  avvisi: "Avvisi anagrafica",
  apriAvvisi: "Mostra gli avvisi dell’anagrafica",
  chiudiAvvisi: "Chiudi avvisi",
  errori: (n) => (n === 1 ? "1 errore" : `${n} errori`),
  risultati: (n) => (n === 1 ? "1 risultato" : `${n} risultati`),
  gruppoFiltri: "Filtri dell'elenco",
  nomeFiltri: "Filtri",
  chiudiFiltri: "Chiudi filtri",
  azzeraFiltri: "Azzera filtri",
  filtri: (attivi) => attivi ? `Filtri (${attivi})` : "Filtri",
  ruolo: "Ruolo",
  universita: "Università",
  tipoCorso: "Tipo di corso",
  statoProdotto: "Stato del prodotto",
  // Etichette della colonna "Verifiche" dei clienti: `voce` e' il testo
  // visibile, `si` e `no` il tooltip e il testo per i lettori di schermo.
  indicatori: {
    email: { voce: "Email", si: "Email verificata", no: "Email non verificata" },
    cellulare: { voce: "Cellulare", si: "Cellulare verificato", no: "Cellulare non verificato" },
    diploma: { voce: "Diploma", si: "Dati diploma completi", no: "Dati diploma incompleti" },
  },
};
