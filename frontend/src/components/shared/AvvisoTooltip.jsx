import { useState } from "react";
import { createPortal } from "react-dom";
import { TriangleAlert, X } from "../../config/icone.js";
import { pulsanteIcona } from "../../config/styles/pulsante.js";
import { STILI_AVVISI } from "../../config/styles/feedback.js";
import { TESTI_ELENCO } from "../../config/testi/elenco.js";
import Dialogo from "./Dialogo.jsx";

/** Il comando non apre la riga; il dialogo nativo gestisce focus, Escape e mobile. */
export default function AvvisoTooltip({ messaggi }) {
  const [aperto, setAperto] = useState(false);
  if (!messaggi?.length) return null;
  const ferma = (evento) => evento.stopPropagation();
  return (
    <span className={STILI_AVVISI.comando} onClick={ferma} onKeyDown={ferma}>
      <button type="button" className={pulsanteIcona()} onClick={() => setAperto(true)}
        title={messaggi.join("\n")} aria-label={TESTI_ELENCO.apriAvvisi} aria-haspopup="dialog">
        <TriangleAlert className={STILI_AVVISI.icona} aria-hidden="true" />
      </button>
      {createPortal(
        <Dialogo aperto={aperto} onChiudi={() => setAperto(false)} etichetta={TESTI_ELENCO.avvisi}>
          <div className={STILI_AVVISI.contenuto}>
            <div className={STILI_AVVISI.intestazione}>
              <h2>{TESTI_ELENCO.avvisi}</h2>
              <button type="button" className={pulsanteIcona()} data-focus-iniziale
                onClick={() => setAperto(false)} aria-label={TESTI_ELENCO.chiudiAvvisi}>
                <X aria-hidden="true" />
              </button>
            </div>
            <ul className={STILI_AVVISI.elenco}>
              {messaggi.map((messaggio) => <li key={messaggio}>{messaggio}</li>)}
            </ul>
          </div>
        </Dialogo>, document.body,
      )}
    </span>
  );
}
