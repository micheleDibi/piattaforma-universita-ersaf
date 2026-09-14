import { useEffect, useRef, useState } from "react";
import { DURATA_CONFERMA_AZIONE_MS } from "../config/interazioni.js";

/** Conferma soltanto il successo reale; una nuova richiesta invalida quella vecchia. */
export function useConfermaAzione(azione) {
  const [stato, setStato] = useState("pronto");
  const sequenza = useRef(0);
  const timer = useRef(null);
  useEffect(() => () => { clearTimeout(timer.current); sequenza.current += 1; }, []);
  const esegui = async () => {
    const richiesta = ++sequenza.current;
    clearTimeout(timer.current);
    setStato("attesa");
    try {
      await azione();
      if (richiesta !== sequenza.current) return;
      setStato("eseguita");
      timer.current = setTimeout(() => setStato("pronto"), DURATA_CONFERMA_AZIONE_MS);
    } catch {
      if (richiesta === sequenza.current) setStato("errore");
    }
  };
  return { esegui, stato };
}
