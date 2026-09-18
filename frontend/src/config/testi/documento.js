// Documento PDF della pratica: pulsante nella scheda e messaggi.
export const TESTI_DOCUMENTO = {
  scarica: "Scarica PDF",
  inCorso: "Preparazione del PDF…",
  etichetta: (numero) => (numero ? `Scarica il PDF della pratica ${numero}` : "Scarica il PDF della pratica"),
  erroreVerifica: "Non è stato possibile verificare se il documento della pratica è disponibile.",
  erroreDownload: "Download del documento non riuscito. Riprova.",
};
