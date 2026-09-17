import { TESTI_ELENCO } from "../../config/testi/elenco.js";

/** Pieno se attivo, anello se no: la forma distingue gli stati anche senza colore. */
function Pallino({ attivo, etichetta }) {
  return (
    <span className="indicatori-stato__pallino" data-attivo={attivo}
      title={etichetta} aria-hidden="true" />
  );
}

/** Pallini di una riga. Il testo nascosto, con l'`id` scelto dal chiamante,
 * diventa la descrizione accessibile della riga intera. */
export default function IndicatoriStato({ indicatori, id }) {
  if (!indicatori?.length) return null;
  return (
    <span className="indicatori-stato">
      {indicatori.map((indicatore) => (
        <Pallino key={indicatore.id} attivo={indicatore.attivo} etichetta={indicatore.etichetta} />
      ))}
      <span id={id} className="sr-only">
        {indicatori.map((indicatore) => indicatore.etichetta).join(", ")}
      </span>
    </span>
  );
}

export function LegendaIndicatori({ voci }) {
  const testi = TESTI_ELENCO.legendaIndicatori;
  // Punteggiatura e spazi separano le parti nel testo letto; nel flex lo spazio
  // non occupa posto e la virgola nascosta e' fuori dal flusso.
  return (
    <p className="indicatori-legenda">
      <span>{testi.ordine(voci)}.</span>{" "}
      <span className="indicatori-legenda__chiave">
        <span className="indicatori-legenda__voce">
          <Pallino attivo />
          {testi.si}
        </span>
        <span className="sr-only">, </span>
        <span className="indicatori-legenda__voce">
          <Pallino attivo={false} />
          {testi.no}
        </span>
      </span>
    </p>
  );
}
