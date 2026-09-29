import { useLayoutEffect, useRef, useState } from "react";
import { useChatPratica } from "../../hooks/useChatPratica.js";
import { TESTI_CHAT as testi } from "../../config/testi/chatPratica.js";
import { STILI_CHAT as stili } from "../../config/styles/chatPratica.js";
import { pulsante } from "../../config/styles/pulsante.js";
import { Send } from "../../config/icone.js";
import AlertMessage from "../AlertMessage.jsx";

const dataMessaggio = value => {
  if (!value) return "";
  const data = new Date(value);
  return Number.isNaN(data.getTime()) ? "" : new Intl.DateTimeFormat("it-IT", { dateStyle: "short", timeStyle: "short" }).format(data);
};

export default function ChatPratica({ praticaId }) {
  const { chat, ...stato } = useChatPratica(praticaId);
  const [testo, setTesto] = useState("");
  const [errore, setErrore] = useState("");
  const lista = useRef(null);
  const posizione = useRef({ vicino: true, altezza: 0, precedenti: false });
  const ultimo = stato.elementi.at(-1)?.id;
  const primo = stato.elementi[0]?.id;
  useLayoutEffect(() => {
    const el = lista.current;
    if (!el) return;
    if (posizione.current.precedenti) {
      el.scrollTop += el.scrollHeight - posizione.current.altezza;
      posizione.current.precedenti = false;
    } else if (posizione.current.vicino) el.scrollTop = el.scrollHeight;
  }, [primo, ultimo]);
  const precedenti = () => {
    posizione.current = { ...posizione.current, altezza: lista.current.scrollHeight, precedenti: true };
    chat.aggiorna(true);
  };
  const invia = async evento => {
    evento.preventDefault(); setErrore("");
    try { if (await chat.invia(testo)) { setTesto(""); posizione.current.vicino = true; } }
    catch (e) { setErrore(e.message); }
  };
  return <section className={stili.sezione} aria-label={testi.titolo}>
    <div className={stili.testata}>
      <div><h2 className={stili.titolo}>{testi.titolo}</h2><p className={stili.nota}>{testi.descrizione}</p></div>
      <p className={stili.nota} role="status">{testi[stato.connessione]}</p>
    </div>
    <AlertMessage message={stato.errore ? { type: "error", text: stato.errore } : null} />
    {stato.errore && <button type="button" className={pulsante("secondario")} onClick={() => { chat.stop(); chat.start(); }}>{testi.riprova}</button>}
    <div ref={lista} className={stili.storico} tabIndex={0} aria-label={testi.storico}
      onScroll={evento => { const el = evento.currentTarget; posizione.current.vicino = el.scrollHeight - el.scrollTop - el.clientHeight < 60; }}>
      {stato.altri && <button type="button" className={pulsante("secondario")} disabled={stato.precedente} onClick={precedenti}>{stato.precedente ? testi.caricamento : testi.precedenti}</button>}
      {stato.caricamento ? <p className={stili.nota}>{testi.caricamento}</p> : !stato.errore && !stato.elementi.length && <p className={stili.nota}>{testi.vuota}</p>}
      <ol className={stili.elenco}>
        {stato.elementi.map(m => <li key={m.id} className={m.mio ? stili.mio : stili.messaggio}>
          <div className={stili.metadati}><span className={stili.autore}>{m.mio ? testi.tu : m.autore}</span><time dateTime={m.data}>{dataMessaggio(m.data)}</time></div>
          <p className={stili.testo}>{m.testo}</p>
        </li>)}
      </ol>
    </div>
    {stato.invio && <div className={stili.pendente} aria-live="polite">
      <p className={stili.testo}>{stato.invio.testo}</p>
      <p className={stato.invio.errore ? stili.errore : stili.nota}>{stato.invio.errore || testi.attesa}</p>
      {stato.invio.errore && <button type="button" className={pulsante("secondario")} disabled={stato.connessione !== "connesso"} onClick={() => chat.riprovaInvio()}>{testi.riprova}</button>}
    </div>}
    <form onSubmit={invia} className={stili.compositore}>
      <label htmlFor={`messaggio-${praticaId}`} className={stili.nota}>{testi.campo}</label>
      <textarea id={`messaggio-${praticaId}`} className={stili.campo} value={testo} maxLength={1000} rows={3}
        disabled={!!stato.invio} onChange={e => setTesto(e.target.value)} />
      <div className={stili.azioni}>
        <p className={stili.errore} role="alert">{errore}</p>
        <button type="submit" className={pulsante("primario")} disabled={!testo.trim() || !!stato.invio || stato.connessione !== "connesso"}>
          <Send aria-hidden="true" className={stili.icona} />{testi.invia}
        </button>
      </div>
    </form>
  </section>;
}
