import { pulsante } from "../../config/styles/pulsante.js";
import IndicatoreCaricamento from "./IndicatoreCaricamento.jsx";

export default function StatoPagineElenco({ pagina }) {
  return <div className="stato-pagine-elenco">
    {pagina.loading ? <IndicatoreCaricamento dimensione="compatto" messaggio="Caricamento…" />
      : !pagina.altri && pagina.elementi.length > 0 ? <p role="status">Hai raggiunto la fine dell’elenco</p> : null}
    {pagina.errore && <p role="alert">{pagina.errore}</p>}
    {(pagina.altri || pagina.errore) && <button type="button" className={pulsante("secondario")}
      onClick={pagina.carica} disabled={pagina.loading}>{pagina.errore ? "Riprova" : "Carica altri elementi"}</button>}
  </div>;
}
