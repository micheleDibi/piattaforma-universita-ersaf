import { useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { TriangleAlert } from "../../config/icone.js";
import { pulsanteIcona } from "../../config/styles/pulsante.js";
import { TESTI_ELENCO } from "../../config/testi/elenco.js";
import { usePopoverAncorato } from "../../hooks/usePopoverAncorato.js";

/**
 * Segnale delle anomalie in una riga di elenco: al clic apre, sotto di se',
 * un popover nativo con il numero di errori e l'elenco. Escape e il clic fuori
 * lo chiudono (light dismiss del browser).
 *
 * Il pannello e' un portale su document.body: dentro la riga cliccabile
 * (role="button") i lettori di schermo lo tratterebbero come contenuto
 * presentazionale, e un clic sul suo testo darebbe il fuoco alla riga. Gli
 * eventi del portale risalgono comunque l'albero di React fino al contenitore,
 * che ferma clic e tasti: la riga non si apre.
 *
 * Nel design il pannello sta dentro la riga, che resta evidenziata finche' il
 * puntatore e' sul pannello. Il portale non passa :hover alla riga: il
 * contenitore segnala il puntatore sul pannello con data-puntatore e
 * righeElenco.css evidenzia la riga che lo contiene.
 */
export default function AvvisoTooltip({ messaggi }) {
  if (!messaggi?.length) return null;
  return <PopoverAvvisi messaggi={messaggi} />;
}

function PopoverAvvisi({ messaggi }) {
  const id = useId();
  const comando = useRef(null);
  const pannello = useRef(null);
  const [sulPannello, setSulPannello] = useState(false);
  usePopoverAncorato(pannello, comando);
  const titolo = TESTI_ELENCO.errori(messaggi.length);
  const ferma = (evento) => evento.stopPropagation();
  // Chiuso con Escape sotto il puntatore, il pannello sparisce senza pointerleave.
  const aggiornaApertura = (evento) => {
    if (evento.nativeEvent.newState === "closed") setSulPannello(false);
  };
  return (
    <span className="avvisi" data-puntatore={sulPannello ? "pannello" : undefined}
      onClick={ferma} onKeyDown={ferma}>
      <button ref={comando} type="button" className={pulsanteIcona("avviso", "minima")}
        popoverTarget={id} aria-haspopup="dialog" aria-controls={id}
        title={titolo} aria-label={TESTI_ELENCO.apriAvvisi}>
        <TriangleAlert aria-hidden="true" />
      </button>
      {createPortal(
        <div ref={pannello} id={id} popover="auto" role="dialog"
          aria-labelledby={`${id}-titolo`} data-allinea="inizio" className="avvisi__pannello"
          onPointerEnter={() => setSulPannello(true)} onPointerLeave={() => setSulPannello(false)}
          onToggle={aggiornaApertura}>
          <p id={`${id}-titolo`} className="avvisi__titolo">{titolo}</p>
          <ul className="avvisi__elenco">
            {messaggi.map((messaggio, indice) => <li key={`${indice}-${messaggio}`}>{messaggio}</li>)}
          </ul>
        </div>,
        document.body,
      )}
    </span>
  );
}
