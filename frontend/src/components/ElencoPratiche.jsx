import { PERCORSI } from "../config/routes/percorsi.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
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
import StatoPagineElenco from "./shared/StatoPagineElenco.jsx";
import { BLOCCHI_PRATICHE } from "../lib/configPratiche.js";

function costruisciTitolo(filtri) {
  const blocco = BLOCCHI_PRATICHE.find(
    (b) => String(b.nomeUniversitaId) === String(filtri.universita),
  );
  if (!blocco) return "Elenco Pratiche";

  const idsTipoCorso = filtri.tipoSelezionato
    ? [filtri.tipoSelezionato]
    : filtri.tipoCorso;
  const descrizioniTipoCorso = filtri.tipiCorso
    .filter((t) =>
      idsTipoCorso.map(String).includes(String(t.listino_tipoCorso_id)),
    )
    .map((t) => t.listino_tipoCorso_descrizione)
    .join(" / ");

  return descrizioniTipoCorso
    ? `Elenco Pratiche - ${blocco.titolo} - ${descrizioniTipoCorso}`
    : `Elenco Pratiche - ${blocco.titolo}`;
}

export default function ElencoPratiche() {
  const risorsa = PERCORSI.pratiche;
  const { apri } = useNavigazioneElenco(risorsa.elenco);
  const filtri = useFiltriPratiche();
  const pagina = usePagineRemote(filtri.query, paginaPratiche, true);
  return (
    <div className={contenutoPagina()}>
      <IntestazioneElenco
        titolo={costruisciTitolo(filtri)}
        azioni={
          <AzioneCrea
            onClick={() => apri(risorsa.nuovo)}
            etichetta="Nuova"
            etichettaEstesa="Nuova pratica"
          />
        }
        ricerca={
          <CampoRicerca
            valore={filtri.ricerca}
            onCambia={filtri.setRicerca}
            segnaposto="Cerca per sottoscrittore"
          />
        }
        filtri={{
          contenuto: <FiltriPratiche filtri={filtri} />,
          attivi: filtri.attivi,
          onAzzera: filtri.azzera,
        }}
      />
      <div className={schedaElenco("corpo")} aria-busy={pagina.loading}>
        <RigheElenco
          dati={pagina.elementi.map(rigaPratica)}
          modello={MODELLO_PRATICHE}
          onApri={(id) => apri(risorsa.dettaglio(id))}
          vuoto={
            !pagina.loading && !pagina.errore && "Nessuna pratica trovata."
          }
        />
        <StatoPagineElenco pagina={pagina} />
      </div>
    </div>
  );
}
