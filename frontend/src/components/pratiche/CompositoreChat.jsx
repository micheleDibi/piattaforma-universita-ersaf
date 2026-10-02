import { useRef, useState } from "react";
import { Send } from "../../config/icone.js";
import { STILI_CHAT as stili } from "../../config/styles/chatPratica.js";
import { TESTI_CHAT as testi } from "../../config/testi/chatPratica.js";
import { useCampoCrescente } from "../../hooks/useCampoCrescente.js";
import { invioDaTastiera } from "../../lib/compositoreChat.js";
import { leggiSchermoCompatto } from "../../lib/schermo.js";

/** Bozza, tastiera e invio compongono un unico controllo nativo. */
export default function CompositoreChat({ id, invia, occupato, connesso }) {
  const [testo, setTesto] = useState("");
  const [errore, setErrore] = useState("");
  const campo = useCampoCrescente(testo);
  const preparazione = useRef(false);
  const disabilitato = !testo.trim() || occupato || !connesso;
  const spedisci = async () => {
    if (disabilitato || preparazione.current) return;
    preparazione.current = true;
    setErrore("");
    try {
      if (await invia(testo)) {
        // Non cancellare una nuova bozza scritta durante la preparazione.
        setTesto(attuale => attuale === testo ? "" : attuale);
        campo.current?.focus({ preventScroll: true });
      }
    } catch (e) { setErrore(e.message); }
    finally { preparazione.current = false; }
  };
  return <form className={stili.compositore} onSubmit={e => { e.preventDefault(); spedisci(); }}>
    <label htmlFor={id} className={stili.etichettaCampo}>{testi.campo}</label>
    <textarea ref={campo} id={id} className={stili.campo} placeholder={testi.campo}
      value={testo} maxLength={1000} rows={1} aria-describedby={errore ? `${id}-errore` : undefined}
      onChange={e => setTesto(e.target.value)}
      onKeyDown={e => invioDaTastiera(e, { compatto: leggiSchermoCompatto(), disabilitato }, spedisci)} />
    <button type="submit" className={stili.invia} disabled={disabilitato} aria-label={testi.invia} title={testi.invia}>
      <Send aria-hidden="true" className={stili.icona} />
    </button>
    {errore && <p id={`${id}-errore`} className={stili.erroreCompositore} role="alert">{errore}</p>}
  </form>;
}
