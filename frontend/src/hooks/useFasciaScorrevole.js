import { useEffect, useState } from "react";

const INIZIALI = { inizio: true, fine: false };

/**
 * Estremi della fascia delle miniature (`binario` e' il ref della ul che
 * scorre) e scorrimento di una pagina visibile con le frecce. `chiave` cambia
 * quando cambiano le voci: gli estremi si ricalcolano.
 * La preferenza per il movimento ridotto la rispetta il CSS
 * (scroll-behavior: smooth solo senza riduzione).
 */
export function useFasciaScorrevole(binario, chiave) {
  const [estremi, setEstremi] = useState(null);
  useEffect(() => {
    const elenco = binario.current;
    if (!elenco || typeof IntersectionObserver === "undefined") return undefined;
    const primo = elenco.firstElementChild;
    const ultimo = elenco.lastElementChild;
    if (!primo || !ultimo) return undefined;
    const visibili = new Map();
    const osservatore = new IntersectionObserver((voci) => {
      for (const voce of voci) visibili.set(voce.target, voce.intersectionRatio >= 0.98);
      setEstremi({ chiave, inizio: visibili.get(primo) ?? true, fine: visibili.get(ultimo) ?? false });
    }, { root: elenco, threshold: [0, 0.98, 1] });
    osservatore.observe(primo);
    if (ultimo !== primo) osservatore.observe(ultimo);
    return () => osservatore.disconnect();
  }, [binario, chiave]);

  // Per i gestori delle frecce: legge il ref solo quando e' chiamata.
  function scorri(verso) {
    const elenco = binario.current;
    if (!elenco) return;
    const stile = getComputedStyle(elenco);
    const rientro = (Number.parseFloat(stile.paddingLeft) || 0) + (Number.parseFloat(stile.paddingRight) || 0);
    elenco.scrollBy({ left: Math.sign(verso) * Math.max(elenco.clientWidth - rientro, 0) });
  }

  const correnti = estremi?.chiave === chiave ? estremi : INIZIALI;
  return {
    allInizio: correnti.inizio,
    allaFine: correnti.fine,
    scorrevole: !(correnti.inizio && correnti.fine),
    scorri,
  };
}
