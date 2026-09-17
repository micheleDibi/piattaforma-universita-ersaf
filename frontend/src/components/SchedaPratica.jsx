import { useNavigate, useParams } from "react-router";
import { PERCORSI } from "../config/routes/percorsi.js";
import { contenutoPagina } from "../config/styles/pagina.js";
import { pulsante } from "../config/styles/pulsante.js";
import { STILI_PRATICA as stili } from "../config/styles/pratica.js";
import useSchedaPratica from "../hooks/useSchedaPratica.js";
import { useDocumentoPratica } from "../hooks/useDocumentoPratica.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import IntestazionePagina from "./shared/IntestazionePagina.jsx";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import AlertMessage from "./AlertMessage.jsx";
import PaginaNonTrovata from "./PaginaNonTrovata.jsx";
import RelazioniPratica from "./pratiche/RelazioniPratica.jsx";
import DatiPratica from "./pratiche/DatiPratica.jsx";
import AzioneDocumento from "./pratiche/AzioneDocumento.jsx";

export default function SchedaPratica() {
  const { praticaId } = useParams();
  const navigate = useNavigate();
  const form = useSchedaPratica(praticaId);
  const documento = useDocumentoPratica(praticaId);
  const { ritorno } = useNavigazioneElenco(PERCORSI.pratiche.elenco);
  const invia = async evento => {
    evento.preventDefault();
    const salvata = await form.salva();
    if (salvata && !praticaId) navigate(PERCORSI.pratiche.dettaglio(salvata.pratica_id),
      { replace: true, state: { elenco: ritorno } });
  };
  if (form.status === 404) return <PaginaNonTrovata />;
  return <div className={contenutoPagina("modulo")}>
    <IntestazionePagina titolo={praticaId ? `Pratica ${form.dati.pratica_numero || ""}` : "Nuova pratica"}
      indietro={{ rotta: ritorno, etichetta: "Pratiche" }}
      azioni={<AzioneDocumento documento={documento} numero={form.dati.pratica_numero} />} />
    <AlertMessage message={documento.errore ? { type: "error", text: documento.errore } : null} />
    {form.loading ? <IndicatoreCaricamento messaggio="Caricamento della pratica…" centrato />
      : form.errore ? <><AlertMessage message={{ type: "error", text: form.errore }} /><button className={pulsante("secondario")} onClick={form.riprova}>Riprova</button></>
      : <form className={stili.modulo} onSubmit={invia}>
        <AlertMessage message={form.messaggio} />
        <fieldset disabled={form.salvataggio} className={stili.sezione}>
          <RelazioniPratica form={form} nuova={!praticaId} />
          <hr className={stili.separatore} />
          <DatiPratica form={form} nuova={!praticaId} />
          <div className={stili.azioni}>
            <button type="button" className={pulsante("secondario", "grande")} onClick={() => navigate(ritorno)}>Annulla</button>
            <button type="submit" className={pulsante("primario", "grande")}>{form.salvataggio ? "Salvataggio…" : "Salva pratica"}</button>
          </div>
        </fieldset>
      </form>}
  </div>;
}
