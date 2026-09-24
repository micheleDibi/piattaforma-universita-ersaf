import { Search } from "../../config/icone.js";
import { campo } from "../../config/styles/campo";

/**
 * Campo di ricerca con icona. Compone l'icona e il campo nativo, e da' al
 * campo un nome accessibile anche quando non c'e' un'etichetta visibile.
 *
 * @param {{
 *   valore: string,
 *   onCambia: (valore: string) => void,
 *   segnaposto?: string,
 *   etichetta?: string,
 * }} props
 */
export default function CampoRicerca({
  valore,
  onCambia,
  segnaposto,
  etichetta = "Cerca",
}) {
  return (
    <div className="relative w-full">
      <Search
        aria-hidden="true"
        className="pointer-events-none absolute left-3 top-1/2 size-icona-piccola -translate-y-1/2 text-testo-attenuato"
      />
      <input
        type="search"
        value={valore}
        onChange={(evento) => onCambia(evento.target.value)}
        placeholder={segnaposto}
        aria-label={etichetta}
        className={`${campo("compatto")} pl-8`}
      />
    </div>
  );
}
