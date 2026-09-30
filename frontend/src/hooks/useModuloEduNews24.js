import { useEffect, useState } from "react";
import { TESTI_EDUNEWS24 as testi } from "../config/testi/edunews24.js";
import { caricaElencoEduNews24, leggiEsitoFunzione } from "../lib/edunews24Api.js";
import { percorsoSezione, vociModulo } from "../lib/edunews24.js";
import { useAttesaRiprova } from "./useAttesaRiprova.js";
import { useComparsaRitardata } from "./useComparsaRitardata.js";
import { useEsitoFunzioneEduNews24 } from "./useEsitoFunzioneEduNews24.js";

/**
 * Stato del modulo EduNews24 in Dashboard, una sezione alla volta, sempre
 * dalla prima pagina condivisa (mai il cursore).
 *
 * `stato`: "nascosto" (funzione spenta, oppure attesa di meno di 400 ms con
 * l'esito ancora ignoto), "scheletro", "pronto", "vuoto" o "errore".
 * Folio: `aggiornatoIl`, `stantio` e `adesso` per descriviAggiornamento.
 * `errore`: null oppure { titolo, dettaglio, nota }, composti per il modulo;
 * `nota` (se c'e') descrive "Riprova", che resta aria-disabled finche'
 * `bloccato` e' vero. Un 401 non mostra nulla: il login lo gestisce apiFetch.
 */
export function useModuloEduNews24(sezione) {
  const funzione = useEsitoFunzioneEduNews24();
  const [esitoIniziale] = useState(leggiEsitoFunzione);
  const [tentativo, setTentativo] = useState(0);
  const chiave = `${sezione}:${tentativo}`;
  const [chiaveIniziale] = useState(chiave);
  const [esito, setEsito] = useState(null);
  const { bloccato, iniziali, avvia: avviaAttesa } = useAttesaRiprova();
  const spenta = funzione === "disattivata";
  // Scheletro subito se la funzione era gia' attiva, dopo un cambio di
  // sezione o un nuovo tentativo, o se e' gia' arrivato un esito (anche
  // tornando alla prima sezione il modulo non sparisce). Il valore vivo dello
  // store non basta: il suo aggiornamento arriva prima del setState
  // dell'esito e lo scheletro comparirebbe per un fotogramma.
  const subito = esitoIniziale === "attiva" || chiave !== chiaveIniziale || esito !== null;
  const comparsa = useComparsaRitardata(chiave, subito);

  useEffect(() => {
    if (spenta) return undefined;
    const controller = new AbortController();
    caricaElencoEduNews24(percorsoSezione(sezione, {}), null, controller.signal).then(
      (dati) => {
        if (!controller.signal.aborted) setEsito({ chiave, dati });
      },
      (errore) => {
        if (controller.signal.aborted || errore?.stato === 401) return;
        const attesaSecondi = errore?.attesaSecondi ?? 0;
        setEsito({ chiave, errore: true, attesaSecondi, adesso: Date.now() });
        avviaAttesa(attesaSecondi);
      },
    );
    return () => controller.abort();
  }, [chiave, sezione, spenta, avviaAttesa]);

  const corrente = esito?.chiave === chiave ? esito : null;
  const dati = corrente?.dati ?? null;
  const voci = dati?.attiva ? vociModulo(sezione, dati.elementi, dati.ricevutoIl) : [];

  let stato = "nascosto";
  if (!spenta && dati?.attiva !== false) {
    if (dati) stato = voci.length > 0 ? "pronto" : "vuoto";
    else if (corrente?.errore) stato = "errore";
    else if (comparsa) stato = "scheletro";
  }

  let errore = null;
  if (stato === "errore") {
    const nota = corrente.attesaSecondi > 0
      ? (bloccato ? testi.riprovaTra(iniziali) : null)
      : testi.riprovaPresto;
    errore = { titolo: testi.erroreModulo, dettaglio: testi.erroreModuloDettaglio, nota };
  }

  return {
    stato,
    voci,
    adesso: dati?.ricevutoIl ?? corrente?.adesso ?? null,
    aggiornatoIl: dati?.aggiornatoIl ?? null,
    stantio: dati?.stantio === true,
    errore,
    bloccato: stato === "errore" && bloccato,
    riprova: () => {
      if (bloccato) return;
      setTentativo((n) => n + 1);
    },
  };
}
