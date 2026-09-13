import { barraStrumenti } from "../../config/styles/tabella";

/**
 * Barra degli strumenti in testa a un elenco: a sinistra ricerca e filtri, a
 * destra un'informazione di servizio, per esempio il numero di risultati.
 *
 * @param {{ children: import("react").ReactNode, coda?: import("react").ReactNode }} props
 */
export default function BarraStrumenti({ children, coda }) {
  return (
    <div className={barraStrumenti()}>
      <div className="flex flex-1 flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
        {children}
      </div>
      {coda && <div className="shrink-0 text-nota text-testo-tenue">{coda}</div>}
    </div>
  );
}
