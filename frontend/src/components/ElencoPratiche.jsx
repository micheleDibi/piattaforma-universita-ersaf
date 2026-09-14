import { useNavigate } from "react-router";
import IntestazioneElenco from "./shared/IntestazioneElenco";
import AzioneCrea from "./shared/AzioneCrea";
import RigheElenco from "./shared/RigheElenco.jsx";
import CampoRicerca from "./shared/CampoRicerca";
import FiltriPratiche from "./FiltriPratiche";
import { MODELLO_PRATICHE } from "../config/elenchi.js";
import { rigaPratica } from "../lib/righeElenco.js";
import { paginaPratiche } from "../lib/pratiche";
import useFiltriPratiche from "../hooks/useFiltriPratiche";
import usePagineRemote from "../hooks/usePagineRemote";
import { contenutoPagina } from "../config/styles/pagina";
import { schedaElenco } from "../config/styles/tabella";
import { pulsante } from "../config/styles/pulsante";

export default function ElencoPratiche() {
  const navigate = useNavigate();
  const filtri = useFiltriPratiche();
  const pagina = usePagineRemote(filtri.query, paginaPratiche, true);
  return <div className={contenutoPagina()}>
    <IntestazioneElenco titolo="Pratiche"
      azioni={<AzioneCrea onClick={() => navigate("/nuova-pratica")} etichetta="Nuova" etichettaEstesa="Nuova pratica" />}
      ricerca={<CampoRicerca valore={filtri.ricerca} onCambia={filtri.setRicerca} segnaposto="Cerca per numero pratica" />}
      filtri={{ contenuto: <FiltriPratiche filtri={filtri} />, attivi: filtri.attivi, onAzzera: filtri.azzera }} />
    <div className={schedaElenco("corpo")} aria-busy={pagina.loading}>
      <RigheElenco dati={pagina.elementi.map(rigaPratica)} modello={MODELLO_PRATICHE}
        onApri={id => navigate(`/modifica-pratica/${id}`)}
        vuoto={!pagina.loading && !pagina.errore && "Nessuna pratica trovata."} />
      <div className="stato-pagine-elenco">
        <p role="status">{pagina.loading ? "Caricamento…" : !pagina.altri && pagina.elementi.length ? "Hai raggiunto la fine dell’elenco" : ""}</p>
        {pagina.errore && <p role="alert">{pagina.errore}</p>}
        {(pagina.altri || pagina.errore) && <button type="button" className={pulsante("secondario")}
          onClick={pagina.carica} disabled={pagina.loading}>{pagina.errore ? "Riprova" : "Carica altre pratiche"}</button>}
      </div>
    </div>
  </div>;
}
