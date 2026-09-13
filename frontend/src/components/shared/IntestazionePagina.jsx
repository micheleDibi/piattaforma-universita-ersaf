import { Link } from "react-router";
import { ArrowLeft } from "lucide-react";
import {
  collegamentoIndietro,
  descrizionePagina,
  intestazionePagina,
  titoloPagina,
} from "../../config/styles/pagina";

/**
 * Intestazione di pagina: titolo, descrizione facoltativa, azioni a destra e,
 * nelle pagine di dettaglio, il collegamento di ritorno all'elenco.
 *
 * @param {{
 *   titolo: string,
 *   descrizione?: string,
 *   azioni?: import("react").ReactNode,
 *   indietro?: { rotta: string, etichetta: string },
 * }} props
 */
export default function IntestazionePagina({
  titolo,
  descrizione,
  azioni,
  indietro,
}) {
  return (
    <div className={intestazionePagina()}>
      <div className="min-w-0">
        {indietro && (
          <Link to={indietro.rotta} className={collegamentoIndietro()}>
            <ArrowLeft aria-hidden="true" className="size-icona-piccola" />
            {indietro.etichetta}
          </Link>
        )}
        <h1 className={titoloPagina()}>{titolo}</h1>
        {descrizione && <p className={descrizionePagina()}>{descrizione}</p>}
      </div>

      {azioni && (
        <div className="flex shrink-0 flex-wrap items-center gap-2">{azioni}</div>
      )}
    </div>
  );
}
