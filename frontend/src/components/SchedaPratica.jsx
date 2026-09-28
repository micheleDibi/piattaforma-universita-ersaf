import { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
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

import BarraSchede from "./shared/BarraSchede.jsx";
import FirmaPratica from "./pratiche/FirmaPratica.jsx";
import ChatPratica from "./pratiche/ChatPratica.jsx";
import { TESTI_CHAT as testi } from "../config/testi/chatPratica.js";

const SCHEDE = [{ id: "dati", label: testi.schedaDati }, { id: "messaggi", label: testi.titolo }, { id: "firma", label: testi.schedaFirma }];

export default function SchedaPratica() {
  const { praticaId } = useParams();
  const navigate = useNavigate();
  const [query, setQuery] = useSearchParams();
  const attiva = praticaId && SCHEDE.some(s => s.id === query.get("scheda")) ? query.get("scheda") : "dati";
  const [visitate, setVisitate] = useState(() => new Set([attiva]));
  const cambiaScheda = id => {
    setVisitate(v => new Set([...v, id]));
    setQuery(q => { q.set("scheda", id); return q; }, { replace: true });
  };
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
      : <>
        {praticaId && <BarraSchede id="pratica" etichetta="Sezioni della pratica" schede={SCHEDE} attiva={attiva} onChange={cambiaScheda} />}
        <div role={praticaId ? "tabpanel" : undefined} id="pratica-pannello-dati" aria-labelledby={praticaId ? "pratica-scheda-dati" : undefined} hidden={attiva !== "dati"}>
        <form className={stili.modulo} onSubmit={invia}>
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
