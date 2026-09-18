import { FileDown, LoaderCircle } from "../../config/icone.js";
import { STILI_PRATICA as stili } from "../../config/styles/pratica.js";
import { TESTI_DOCUMENTO as testi } from "../../config/testi/documento.js";

/** Pulsante di download del PDF nell'intestazione della scheda pratica. */
export default function AzioneDocumento({ documento, numero }) {
  if (!documento.disponibile) return null;
  const Icona = documento.inCorso ? LoaderCircle : FileDown;
  return (
    <button type="button" className={stili.azioneDocumento} onClick={() => void documento.scarica()}
      disabled={documento.inCorso} aria-busy={documento.inCorso} aria-label={testi.etichetta(numero)}>
      <Icona aria-hidden="true" className={documento.inCorso ? stili.iconaAttesa : stili.iconaAzione} />
      {documento.inCorso ? testi.inCorso : testi.scarica}
    </button>
  );
}
