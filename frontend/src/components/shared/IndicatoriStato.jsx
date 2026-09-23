import { Check } from "../../config/icone.js";

/** Etichette di verifica di una riga: verde con la spunta se verificato,
 * neutra se no. Il testo nascosto, con l'`id` scelto dal chiamante, diventa
 * la descrizione accessibile della riga intera. */
export default function IndicatoriStato({ indicatori, id }) {
  if (!indicatori?.length) return null;
  return (
    <span className="indicatori-stato">
      {indicatori.map((indicatore) => (
        <span key={indicatore.id} className="indicatori-stato__etichetta"
          data-attivo={indicatore.attivo} title={indicatore.etichetta} aria-hidden="true">
          {indicatore.attivo && <Check className="indicatori-stato__spunta" />}
          {indicatore.voce}
        </span>
      ))}
      <span id={id} className="sr-only">
        {indicatori.map((indicatore) => indicatore.etichetta).join(", ")}
      </span>
    </span>
  );
}
