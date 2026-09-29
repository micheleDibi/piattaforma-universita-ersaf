import { useEffect, useRef, useState } from "react";
import { leggiFirma, salvaFirma } from "../lib/firmaPratica.js";
import { TESTI_FIRMA as testi } from "../config/testi/firma.js";

export function useFirmaPratica(id) {
  const [stato, setStato] = useState(null);
  const [errore, setErrore] = useState("");
  const [messaggio, setMessaggio] = useState("");
  const [occupato, setOccupato] = useState(false);
  const [revisione, setRevisione] = useState(0);
  const generazione = useRef(null);
  const invio = useRef(false);
  useEffect(() => {
    const controllo = new AbortController();
    generazione.current = controllo;
    leggiFirma(id, controllo.signal).then(dati => {
      if (!controllo.signal.aborted) setStato({ id, dati });
    }).catch(e => { if (!controllo.signal.aborted) setErrore(e.message); });
    return () => controllo.abort();
  }, [id, revisione]);
  const salva = async immagine => {
    if (invio.current || stato?.id !== id) return false;
    const corrente = generazione.current;
    invio.current = true; setOccupato(true); setErrore(""); setMessaggio("");
    try {
      const dati = await salvaFirma(id, immagine, stato.dati.versione);
      if (corrente.signal.aborted || corrente !== generazione.current) return false;
      setStato({ id, dati }); setMessaggio(testi.salvata);
      return true;
    } catch (e) {
      if (!corrente.signal.aborted && corrente === generazione.current) setErrore(e.message);
      return false;
    } finally { invio.current = false; setOccupato(false); }
  };
  return { dati: stato?.id === id ? stato.dati : null, errore, messaggio, occupato, salva,
    ricarica: () => { setErrore(""); setMessaggio(""); setStato(null); setRevisione(r => r + 1); } };
}
