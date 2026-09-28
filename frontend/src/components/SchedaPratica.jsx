import { useNavigate, useParams } from "react-router";
import { PERCORSI } from "../config/routes/percorsi.js";
import { contenutoPagina } from "../config/styles/pagina.js";
import { pulsante } from "../config/styles/pulsante.js";
import { STILI_PRATICA as stili } from "../config/styles/pratica.js";
import { eContestoCorsiSingoli } from "../config/pratica.js";
import useSchedaPratica from "../hooks/useSchedaPratica.js";
import { useDocumentoPratica } from "../hooks/useDocumentoPratica.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import { leggiContestoUrl } from "../lib/schedaPratica.js";
import IntestazionePagina from "./shared/IntestazionePagina.jsx";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import AlertMessage from "./AlertMessage.jsx";
import PaginaNonTrovata from "./PaginaNonTrovata.jsx";
import RelazioniPratica from "./pratiche/RelazioniPratica.jsx";
import CaratteristichePercorso from "./pratiche/CaratteristichePercorso.jsx";
import DatiPratica from "./pratiche/DatiPratica.jsx";
import AzioneDocumento from "./pratiche/AzioneDocumento.jsx";

/** Le descrizioni (università, tipo/i di corso) del contesto di creazione
 * per il titolo della scheda: leggiContestoUrl da' solo gli id, qui si
 * traducono nei testi da mostrare con le liste gia' scaricate dalla scheda. */
function etichetteContesto({ universitaId, tipoCorsoIds }, universita, tipiCorso) {
  const nomeUniversita = universita.find((u) => u.id === universitaId)?.descrizione;
  const nomeTipo = tipoCorsoIds
    .map((id) => tipiCorso.find((t) => t.listino_tipoCorso_id === id)?.listino_tipoCorso_descrizione)
    .filter(Boolean)
    .join(" / ");
  return { nomeUniversita, nomeTipo };
}

function titoloCreazione({ nomeUniversita, nomeTipo }) {
  if (!nomeUniversita) return "Nuova pratica";
  return nomeTipo
    ? `Nuova Pratica - ${nomeUniversita} - ${nomeTipo}`
    : `Nuova Pratica - ${nomeUniversita}`;
}

export default function SchedaPratica() {
  const { praticaId } = useParams();
  const navigate = useNavigate();
  const documento = useDocumentoPratica(praticaId);
  const { ritorno } = useNavigazioneElenco(PERCORSI.pratiche.elenco);
  // Serve prima di useSchedaPratica: il prezzo di una pratica Corsi Singoli
  // si calcola diversamente (somma dei corsi scelti, vedi
  // useSchedaPratica.js), e la scheda deve saperlo fin da subito.
  const contestoUrl = leggiContestoUrl(ritorno);
  const corsiSingoli = eContestoCorsiSingoli(contestoUrl.tipoCorsoIds);
  const form = useSchedaPratica(praticaId, { corsiSingoli });
  const invia = async evento => {
    evento.preventDefault();
    const salvata = await form.salva();
    if (!salvata) return;
    // In creazione si va al dettaglio della pratica appena creata (serve
    // subito per il documento PDF, vedi AzioneDocumento). In modifica non
    // c'e' un dettaglio diverso da questa stessa pagina: si torna
    // all'elenco, come fa SchedaAzienda dopo ogni salvataggio riuscito.
    if (praticaId) navigate(ritorno);
    else navigate(PERCORSI.pratiche.dettaglio(salvata.pratica_id), { replace: true, state: { elenco: ritorno } });
  };
  if (form.status === 404) return <PaginaNonTrovata />;
  const etichette = etichetteContesto(contestoUrl, form.universita, form.tipiCorso);
  return <div className={contenutoPagina("modulo")}>
    <IntestazionePagina titolo={praticaId ? `Pratica ${form.dati.pratica_numero || ""}`
      : titoloCreazione(etichette)}
      indietro={{ rotta: ritorno, etichetta: "Pratiche" }}
      azioni={<AzioneDocumento documento={documento} numero={form.dati.pratica_numero} />} />
    <AlertMessage message={documento.errore ? { type: "error", text: documento.errore } : null} />
    {form.loading ? <IndicatoreCaricamento messaggio="Caricamento della pratica…" centrato />
      : form.errore ? <><AlertMessage message={{ type: "error", text: form.errore }} /><button className={pulsante("secondario")} onClick={form.riprova}>Riprova</button></>
      : <form className={stili.modulo} onSubmit={invia}>
        <AlertMessage message={form.messaggio} />
        <fieldset disabled={form.salvataggio} className={stili.sezione}>
          <RelazioniPratica form={form} nuova={!praticaId} universitaId={contestoUrl.universitaId}
            tipoCorsoIds={contestoUrl.tipoCorsoIds} corsiSingoli={corsiSingoli} />
          <CaratteristichePercorso prodotto={form.prodotto} />
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
