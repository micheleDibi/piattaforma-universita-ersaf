import { useEffect, useState } from "react";
import { richiestaOtp } from "../lib/otp.js";

export function useContattiVerificati(clienteId) {
  const [stato, setStato] = useState(null);
  const [messaggio, setMessaggio] = useState(null);
  const [selezionato, setSelezionato] = useState(null);
  useEffect(() => {
    let corrente = true;
    if (!clienteId) return undefined;
    richiestaOtp(`/clienti/${clienteId}/contatti`).then((dati) => {
      if (corrente) setStato(dati);
    }).catch((errore) => {
      if (corrente) setMessaggio({ type: "error", text: errore.message });
    });
    return () => { corrente = false; };
  }, [clienteId]);
  const completato = (dati) => {
    setStato(dati);
    setMessaggio({ type: dati.credenziali_inviate === false ? "warning" : "success", text: dati.message });
    setSelezionato(null);
  };
  return { stato, messaggio, selezionato, setSelezionato, completato };
}
