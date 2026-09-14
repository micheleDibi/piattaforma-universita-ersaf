import { Pencil } from "../../config/icone.js";
import { pulsanteAzioneRiga } from "../../config/styles/pulsante";

/**
 * Azione di modifica in fondo a una riga di tabella: sola icona, elevata.
 *
 * La riga intera porta al dettaglio, quindi questo pulsante e' una scorciatoia
 * esplicita, non l'unico modo per arrivarci: ferma la propagazione del clic per
 * non far scattare due volte la stessa navigazione. Resta un <button> vero, con
 * nome accessibile, perche' la riga cliccabile non e' raggiungibile da tastiera.
 *
 * @param {{ onClick: () => void, etichetta?: string, dimensione?: "normale"|"grande" }} props
 */
export default function AzioneModificaRiga({ onClick, etichetta = "Modifica", dimensione = "normale" }) {
  return (
    <button
      type="button"
      onClick={(evento) => {
        evento.stopPropagation();
        onClick();
      }}
      className={pulsanteAzioneRiga(dimensione)}
      aria-label={etichetta}
      title={etichetta}
    >
      <Pencil aria-hidden="true" className="size-icona-piccola" />
    </button>
  );
}
