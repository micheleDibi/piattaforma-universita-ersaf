import { useEffect, useState } from "react";
import { documentoDisponibile, scaricaDocumento } from "../lib/documentoPratica.js";

/**
 * Disponibilita' e download del PDF di una pratica. Una pratica nuova (senza id)
 * non ha documento; un errore nella verifica nasconde il pulsante senza bloccare
 * la scheda.
 */
export function useDocumentoPratica(praticaId) {
  const [esito, setEsito] = useState(null);
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState("");

  useEffect(() => {
    if (!praticaId) return undefined;
    const controllo = new AbortController();
    documentoDisponibile(praticaId, controllo.signal).then(
      (dati) => { if (!controllo.signal.aborted) setEsito({ praticaId, disponibile: dati.disponibile }); },
      () => { if (!controllo.signal.aborted) setEsito({ praticaId, disponibile: false }); },
    );
    return () => controllo.abort();
  }, [praticaId]);

  const scarica = async () => {
    if (inCorso) return;
    setInCorso(true);
    setErrore("");
    try {
      await scaricaDocumento(praticaId);
    } catch (erroreDownload) {
      setErrore(erroreDownload.message);
    } finally {
      setInCorso(false);
    }
  };

  return {
    disponibile: Boolean(praticaId) && esito?.praticaId === praticaId && esito.disponibile,
    inCorso,
    errore,
    scarica,
  };
}
