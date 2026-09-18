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
import PannelloPratiche from "./PannelloPratiche";

function costruisciTitolo(filtri) {
  const blocco = BLOCCHI_PRATICHE.find(
    (b) => String(b.nomeUniversitaId) === String(filtri.universita),
  );
  if (!blocco) return "Elenco Pratiche";

  if (filtri.tipoSelezionato) {
    const scelto = filtri.tipiCorso.find(
      (t) => String(t.listino_tipoCorso_id) === String(filtri.tipoSelezionato),
    );
    if (scelto)
      return `Elenco Pratiche - ${blocco.titolo} - ${scelto.listino_tipoCorso_descrizione}`;
  }

  if (filtri.labelTipo) {
    return `Elenco Pratiche - ${blocco.titolo} - ${filtri.labelTipo}`;
  }

  const idsTipoCorso = filtri.tipoCorso;
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
  // Chiamato sempre, indipendentemente da cosa si renderizza sotto: mai
  // condizionare la chiamata di un hook, altrimenti React perde la
  // corrispondenza tra hook e render e il componente si rompe silenziosamente
  // (esattamente il sintomo del bug: lista che smette di caricare dopo il click).
  const mostraPannello = !filtri.universita;
  const pagina = usePagineRemote(filtri.query, paginaPratiche, !mostraPannello);

  if (mostraPannello) {
    return (
      <div className={contenutoPagina()}>
        <IntestazioneElenco titolo="Pratiche" />
        <PannelloPratiche />
      </div>
    );
  }

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
