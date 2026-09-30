import { SEZIONI_EDUNEWS24 } from "../../config/edunews24.js";
import { TESTI_EDUNEWS24 as testi } from "../../config/testi/edunews24.js";

/**
 * Selettore della sezione del modulo in Dashboard: tre pulsanti aria-pressed
 * in un gruppo (non un tablist: il corpo non e' un tabpanel), sempre con le
 * etichette brevi. La linguetta attiva e' il pieno inclinato del logo.
 */
export default function SelettoreSezioneEduNews24({ sezione, onCambia }) {
  return (
    <div role="group" aria-label={testi.etichettaSezioni} className="edunews24-modulo__selettore">
      {SEZIONI_EDUNEWS24.map((voce) => (
        <button key={voce} type="button" className="edunews24-linguetta" aria-pressed={voce === sezione}
          aria-controls="edunews24-modulo-corpo" onClick={() => onCambia(voce)}>
          {testi.sezioniBrevi[voce]}
        </button>
      ))}
    </div>
  );
}
