/**
 * Timbro pieno della voce principale di Interpelli e Selezione nel modulo:
 * etichetta ("Scade il", "Pubblicato il"), data corta e anno. Verticale nel
 * modulo dai 38rem, su una riga sotto. La forma breve e' nascosta ai lettori
 * di schermo, che leggono `sr` ("Scadenza: 15 ottobre 2026").
 */
export default function Timbro({ etichetta, cifra, anno, sr }) {
  return (
    <span className="edunews24-timbro">
      <span className="edunews24-timbro__corpo" aria-hidden={sr ? "true" : undefined}>
        {etichetta && <span className="edunews24-timbro__etichetta">{etichetta}</span>}
        {cifra && <span className="edunews24-timbro__cifra">{cifra}</span>}
        {anno && <span className="edunews24-timbro__anno">{anno}</span>}
      </span>
      {sr && <span className="sr-only">{sr}</span>}
    </span>
  );
}
