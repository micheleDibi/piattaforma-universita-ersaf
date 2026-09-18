export const TESTI_ELENCO = {
  avvisi: "Avvisi anagrafica",
  apriAvvisi: "Mostra gli avvisi dell’anagrafica",
  chiudiAvvisi: "Chiudi avvisi",
  gruppoFiltri: "Filtri dell'elenco",
  nomeFiltri: "Filtri",
  chiudiFiltri: "Chiudi filtri",
  azzeraFiltri: "Azzera filtri",
  filtri: (attivi) => attivi ? `Filtri (${attivi})` : "Filtri",
  ruolo: "Ruolo",
  universita: "Università",
  tipoCorso: "Tipo di corso",
  statoProdotto: "Stato del prodotto",
  // Pallini della colonna "Stato" dei clienti: `si` e `no` sono il tooltip e
  // il testo per i lettori di schermo, `voce` il nome nella legenda.
  indicatori: {
    email: { voce: "Email", si: "Email verificata", no: "Email non verificata" },
    cellulare: { voce: "Cellulare", si: "Cellulare verificato", no: "Cellulare non verificato" },
    diploma: { voce: "Diploma", si: "Dati diploma completi", no: "Dati diploma incompleti" },
  },
  legendaIndicatori: {
    ordine: (voci) => `Stato, nell'ordine: ${voci.join(", ")}`,
    si: "Verde: sì",
    no: "Grigio: no",
  },
};
