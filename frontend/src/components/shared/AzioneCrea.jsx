import { Plus } from "lucide-react";
import { pulsante } from "../../config/styles/pulsante";

/**
 * Azione principale di una pagina di elenco: "Nuovo sottoscrittore",
 * "Nuova azienda".
 *
 * Da schermo stretto resta accanto al titolo e mostra la sola forma breve
 * ("Nuovo", "Nuova"): l'etichetta intera occuperebbe la riga da sola e
 * spingerebbe il pulsante sotto il titolo. Il nome accessibile resta quello
 * intero in entrambi i casi.
 *
 * @param {{
 *   onClick: () => void,
 *   etichetta: string,
 *   etichettaBreve: string,
 * }} props
 */
export default function AzioneCrea({ onClick, etichetta, etichettaBreve }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={pulsante()}
      aria-label={etichetta}
    >
      <Plus aria-hidden="true" className="size-icona-piccola" />
      <span className="hidden sm:inline">{etichetta}</span>
      <span className="sm:hidden">{etichettaBreve}</span>
    </button>
  );
}
