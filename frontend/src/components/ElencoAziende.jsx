import useQueryPagina from "../hooks/useQueryPagina.js";
import { QUERY_AZIENDE } from "../config/routes/query.js";
import { PERCORSI } from "../config/routes/percorsi.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";


import IntestazioneElenco from "./shared/IntestazioneElenco";
import AzioneCrea from "./shared/AzioneCrea";
import RigheElenco from "./shared/RigheElenco.jsx";
import { MODELLO_AZIENDE } from "../config/elenchi.js";
import { rigaAzienda } from "../lib/righeElenco.js";
import CampoRicerca from "./shared/CampoRicerca";
import { contenutoPagina } from "../config/styles/pagina";
import { schedaElenco } from "../config/styles/tabella";
import StatoPagineElenco from "./shared/StatoPagineElenco.jsx";
import usePagineRemote from "../hooks/usePagineRemote.js";
import { paginaElenco, queryAziende } from "../lib/queryElenchi.js";

function ElencoAziende() {
  const [query, aggiornaQuery] = useQueryPagina(QUERY_AZIENDE);
  const searchTerm = query.ricerca;
  const setSearchTerm = ricerca => aggiornaQuery({ ricerca });
  const risorsa = PERCORSI.aziende;
  const { apri } = useNavigazioneElenco(risorsa.elenco);

  const pagina = usePagineRemote(queryAziende(query), paginaElenco, true);

  return (
    <div className={contenutoPagina()}>
      <IntestazioneElenco
        titolo="Aziende"
        azioni={
          <AzioneCrea
            onClick={() => apri(risorsa.nuovo)}
            etichetta="Nuova"
            etichettaEstesa="Nuova azienda"
          />
        }
        ricerca={
          <CampoRicerca
            valore={searchTerm}
            onCambia={setSearchTerm}
            segnaposto="Cerca per ragione sociale"
          />
        }
      />
      <div className={schedaElenco("corpo")}>
        <RigheElenco dati={pagina.elementi.map(rigaAzienda)} modello={MODELLO_AZIENDE}
          onApri={(id) => apri(risorsa.dettaglio(id))}
          vuoto={!pagina.loading && !pagina.errore && "Nessuna azienda trovata."} />

        <StatoPagineElenco pagina={pagina} />
      </div>
    </div>
  );
}

export default ElencoAziende;
