import { useEffect, useState } from "react";
import { caricaPadreAzienda } from "../lib/schedaAzienda.js";

/**
 * Azienda padre di `aziendaId`: la scheda la usa per il sottotitolo e la
 * passa alla sezione Gerarchia. Senza `aziendaId` (nuova azienda) non legge
 * niente.
 *
 * padre: undefined in caricamento, null se l'azienda e' radice, altrimenti
 * l'azienda padre. ricarica: la rilegge, per esempio dopo "Cambia padre";
 * intanto resta visibile il padre precedente.
 *
 * @param {string|number|undefined} aziendaId
 * @returns {{ padre: object|null|undefined, errore: string, ricarica: () => void }}
 */
export default function usePadreAzienda(aziendaId) {
  const [stato, setStato] = useState({ aziendaId, padre: undefined, errore: "" });
  const [tentativo, setTentativo] = useState(0);

  // Un'altra azienda riparte da capo, senza l'errore della precedente: si
  // azzera durante il render, non nell'effetto che legge il padre.
  if (stato.aziendaId !== aziendaId) {
    setStato({ aziendaId, padre: undefined, errore: "" });
  }

  useEffect(() => {
    if (!aziendaId) return;
    const controller = new AbortController();
    caricaPadreAzienda(aziendaId, controller.signal)
      .then((padre) => {
        if (!controller.signal.aborted) setStato({ aziendaId, padre, errore: "" });
      })
      .catch((errore) => {
        if (!controller.signal.aborted)
          setStato((prec) => ({ ...prec, errore: errore.message }));
      });
    return () => controller.abort();
  }, [aziendaId, tentativo]);

  return {
    padre: stato.padre,
    errore: stato.errore,
    ricarica: () => setTentativo((n) => n + 1),
  };
}
