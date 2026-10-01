import { useState } from "react";
import { Navigate, useNavigate, useParams, useSearchParams } from "react-router";
import { PERCORSI } from "../config/routes/percorsi.js";
import { contenutoPagina } from "../config/styles/pagina.js";
import { pulsante } from "../config/styles/pulsante.js";
import { STILI_PRATICA as stili } from "../config/styles/pratica.js";
import { eContestoCorsiSingoli, eGruppoCorsiSingoli } from "../config/pratica.js";
import useSchedaPratica from "../hooks/useSchedaPratica.js";
import { useDocumentoPratica } from "../hooks/useDocumentoPratica.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import { leggiContestoUrl } from "../lib/schedaPratica.js";
import ConRuoloVerificato from "./shared/ConRuoloVerificato.jsx";
import IntestazionePagina from "./shared/IntestazionePagina.jsx";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import AlertMessage from "./AlertMessage.jsx";
import PaginaNonTrovata from "./PaginaNonTrovata.jsx";
import RelazioniPratica from "./pratiche/RelazioniPratica.jsx";
import CaratteristichePercorso from "./pratiche/CaratteristichePercorso.jsx";
import ElencoCorsiPratica from "./pratiche/ElencoCorsiPratica.jsx";
import DatiPratica from "./pratiche/DatiPratica.jsx";
import AzioneDocumento from "./pratiche/AzioneDocumento.jsx";

import BarraSchede from "./shared/BarraSchede.jsx";
import FirmaPratica from "./pratiche/FirmaPratica.jsx";
import ChatPratica from "./pratiche/ChatPratica.jsx";
import { TESTI_CHAT as testi } from "../config/testi/chatPratica.js";

const SCHEDE = [{ id: "dati", label: testi.schedaDati }, { id: "messaggi", label: testi.titolo }, { id: "firma", label: testi.schedaFirma }];

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
  // Il Nazionale gestisce le pratiche ma non le crea: il suo elenco non ha il
  // tasto Nuova, e l'indirizzo di creazione aperto a mano riporta all'elenco.
  // Il ruolo si rilegge dal server prima: anche il campo Codice ASG della
  // scheda (DatiPratica.jsx) dipende da quello attuale.
  return (
    <ConRuoloVerificato>
      {(ruolo) => (!praticaId && ruolo === "nazionale"
        ? <Navigate to={PERCORSI.pratiche.elenco} replace />
        : <ModuloPratica />)}
    </ConRuoloVerificato>
  );
}

function ModuloPratica() {
  const { praticaId } = useParams();
  const navigate = useNavigate();
  const [query, setQuery] = useSearchParams();
  const attiva = praticaId && SCHEDE.some(s => s.id === query.get("scheda")) ? query.get("scheda") : "dati";
  const [visitate, setVisitate] = useState(() => new Set([attiva]));
  const cambiaScheda = id => {
    setVisitate(v => new Set([...v, id]));
    setQuery(q => { q.set("scheda", id); return q; }, { replace: true });
  };
  const documento = useDocumentoPratica(praticaId);
  const { ritorno } = useNavigazioneElenco(PERCORSI.pratiche.elenco);
  // Serve prima di useSchedaPratica: il prezzo di una pratica Corsi Singoli
  // si calcola diversamente (somma dei corsi scelti, vedi
  // useSchedaPratica.js), e la scheda deve saperlo fin da subito.
  const contestoUrl = leggiContestoUrl(ritorno);
  const corsiSingoli = eContestoCorsiSingoli(contestoUrl.tipoCorsoIds);
  const form = useSchedaPratica(praticaId, { corsiSingoli });
  // Per mostrare la scheda conta anche il tipo di corso della pratica
  // salvata: aprendola da un elenco senza ?tipoCorso= il contesto manca.
  const mostraCorsiSingoli = corsiSingoli || (Boolean(praticaId) && eGruppoCorsiSingoli(form.dati.listino_tipo_corso_id));
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
      : <>
        {praticaId && <BarraSchede id="pratica" etichetta="Sezioni della pratica" schede={SCHEDE} attiva={attiva} onChange={cambiaScheda} />}
        <div role={praticaId ? "tabpanel" : undefined} id="pratica-pannello-dati" aria-labelledby={praticaId ? "pratica-scheda-dati" : undefined} hidden={attiva !== "dati"}>
        <form className={stili.modulo} onSubmit={invia}>
        <AlertMessage message={form.messaggio} />
        <fieldset disabled={form.salvataggio} className={stili.sezione}>
          <RelazioniPratica form={form} nuova={!praticaId} universitaId={contestoUrl.universitaId}
            tipoCorsoIds={contestoUrl.tipoCorsoIds} corsiSingoli={mostraCorsiSingoli} />
          {/* Corsi Singoli: l'elenco dei corsi al posto delle caratteristiche
              del percorso, che mostravano solo quelle del primo corso. */}
          {mostraCorsiSingoli
            ? <ElencoCorsiPratica corsi={form.corsiPratica}
              onRimuovi={praticaId ? undefined : (corso) => form.setPercorsi(form.corsiSelezionati.filter((c) => c.id !== corso.id))} />
            : <CaratteristichePercorso prodotto={form.prodotto} />}
          <hr className={stili.separatore} />
          <DatiPratica form={form} nuova={!praticaId} prodotto={form.prodotto} />
          <div className={stili.azioni}>
            <button type="button" className={pulsante("secondario", "grande")} onClick={() => navigate(ritorno)}>Annulla</button>
            <button type="submit" className={pulsante("primario", "grande")}>{form.salvataggio ? "Salvataggio…" : "Salva pratica"}</button>
          </div>
        </fieldset>
      </form></div>
      {praticaId && <>
        <div role="tabpanel" id="pratica-pannello-messaggi" aria-labelledby="pratica-scheda-messaggi" hidden={attiva !== "messaggi"}>
          {(attiva === "messaggi" || visitate.has("messaggi")) && <div className={stili.modulo}><ChatPratica key={praticaId} praticaId={praticaId} /></div>}
        </div>
        <div role="tabpanel" id="pratica-pannello-firma" aria-labelledby="pratica-scheda-firma" hidden={attiva !== "firma"}>
          {(attiva === "firma" || visitate.has("firma")) && <div className={stili.modulo}><FirmaPratica key={praticaId} praticaId={praticaId} /></div>}
        </div>
      </>}
      </>}
  </div>;
}
