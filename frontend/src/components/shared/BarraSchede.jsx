import { useLayoutEffect, useRef } from "react";

/**
 * Selezione, tastiera e visibilita della scheda attiva condivise dai dettagli.
 * `variante`: "sottolineata" (predefinita, schede principali) o "segmentata"
 * (sotto-schede, gruppo di pulsanti su fondo grigio). Cambia solo l'aspetto.
 */
export default function BarraSchede({ id, etichetta, schede, attiva, onChange, variante = "sottolineata" }) {
  const barra = useRef(null);
  useLayoutEffect(() => {
    const elemento = barra.current;
    const mostraAttiva = () => {
      const selezionata = elemento.querySelector('[aria-selected="true"]');
      if (!selezionata) return;
      const spazio = elemento.getBoundingClientRect();
      const posizione = selezionata.getBoundingClientRect();
      if (posizione.right > spazio.right) elemento.scrollLeft += posizione.right - spazio.right;
      if (posizione.left < spazio.left) elemento.scrollLeft += posizione.left - spazio.left;
    };
    mostraAttiva();
    const osservatore = new ResizeObserver(mostraAttiva);
    osservatore.observe(elemento);
    return () => osservatore.disconnect();
  }, [attiva]);

  const cambiaConTastiera = (evento) => {
    const indice = schede.findIndex((scheda) => scheda.id === attiva);
    const ultimo = schede.length - 1;
    const destinazioni = { ArrowRight: indice === ultimo ? 0 : indice + 1, ArrowLeft: indice === 0 ? ultimo : indice - 1, Home: 0, End: ultimo };
    const prossima = destinazioni[evento.key];
    if (prossima === undefined) return;
    evento.preventDefault();
    onChange(schede[prossima].id);
    barra.current.querySelectorAll('[role="tab"]')[prossima]?.focus({ preventScroll: true });
  };

  return (
    <div ref={barra} role="tablist" aria-label={etichetta}
      className={variante === "segmentata" ? "schede__barra schede__barra--segmentata" : "schede__barra"}>
      {schede.map(({ id: chiave, label }) => (
        <button key={chiave} type="button" role="tab" id={`${id}-scheda-${chiave}`}
          aria-controls={`${id}-pannello-${chiave}`} aria-selected={attiva === chiave}
          tabIndex={attiva === chiave ? 0 : -1} title={label}
          onClick={() => onChange(chiave)} onKeyDown={cambiaConTastiera} className="schede__linguetta">
          <span className="schede__etichetta">{label}</span>
        </button>
      ))}
    </div>
  );
}
