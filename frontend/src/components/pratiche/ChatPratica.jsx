import { useLayoutEffect, useRef } from "react";
import { useChatPratica } from "../../hooks/useChatPratica.js";
import { TESTI_CHAT as testi } from "../../config/testi/chatPratica.js";
import { STILI_CHAT as stili } from "../../config/styles/chatPratica.js";
import { pulsante } from "../../config/styles/pulsante.js";
import AlertMessage from "../AlertMessage.jsx";
import MessaggioChat from "./MessaggioChat.jsx";
import CompositoreChat from "./CompositoreChat.jsx";

export default function ChatPratica({ praticaId }) {
  const { chat, ...stato } = useChatPratica(praticaId);
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
  const invia = async testo => {
    const accettato = await chat.invia(testo);
    if (accettato) posizione.current.vicino = true;
    return accettato;
  };
  return <section className={stili.sezione} aria-label={testi.titolo}>
    <h2 className={stili.titolo}>{testi.titolo}</h2>
    {stato.connessione === "disconnesso" && <p className={stili.nota} role="status">{testi.disconnesso}</p>}
    <AlertMessage message={stato.errore ? { type: "error", text: stato.errore } : null} />
    {stato.errore && <button type="button" className={pulsante("secondario")} onClick={() => { chat.stop(); chat.start(); }}>{testi.riprova}</button>}
    <div ref={lista} className={stili.storico} tabIndex={0} aria-label={testi.storico}
      onScroll={evento => { const el = evento.currentTarget; posizione.current.vicino = el.scrollHeight - el.scrollTop - el.clientHeight < 60; }}>
      {stato.altri && <button type="button" className={pulsante("secondario")} disabled={stato.precedente} onClick={precedenti}>{stato.precedente ? testi.caricamento : testi.precedenti}</button>}
      {stato.caricamento ? <p className={stili.nota}>{testi.caricamento}</p> : !stato.errore && !stato.elementi.length && <p className={stili.nota}>{testi.vuota}</p>}
      <ol className={stili.elenco}>
        {stato.elementi.map(m => <MessaggioChat key={m.id} messaggio={m} online={stato.online.includes(m.autoreId)} />)}
      </ol>
    </div>
    {stato.invio && <div className={stili.pendente} aria-live="polite">
      <p className={stili.testo}>{stato.invio.testo}</p>
      <p className={stato.invio.errore ? stili.errore : stili.nota}>{stato.invio.errore || testi.attesa}</p>
      {stato.invio.errore && <button type="button" className={pulsante("secondario")} disabled={stato.connessione !== "connesso"} onClick={() => chat.riprovaInvio()}>{testi.riprova}</button>}
    </div>}
    <CompositoreChat key={praticaId} id={`messaggio-${praticaId}`} invia={invia}
      occupato={!!stato.invio} connesso={stato.connessione === "connesso"} />
  </section>;
}
