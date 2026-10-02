import { TESTI_CHAT as testi } from "../../config/testi/chatPratica.js";
import { STILI_CHAT as stili } from "../../config/styles/chatPratica.js";

const dataMessaggio = value => {
  if (!value) return "";
  const data = new Date(value);
  return Number.isNaN(data.getTime()) ? "" : new Intl.DateTimeFormat("it-IT", { dateStyle: "short", timeStyle: "short" }).format(data);
};

export default function MessaggioChat({ messaggio: m, online }) {
  return <li className={m.mio ? stili.mio : stili.messaggio}>
    <div className={stili.metadati}>
      <span className={stili.autore}>
        {online && !m.mio && <span className={stili.presenza} role="img" aria-label={testi.online} title={testi.online} />}
        {m.mio ? testi.tu : m.autore}
      </span>
      <time dateTime={m.data}>{dataMessaggio(m.data)}</time>
    </div>
    <p className={stili.testo}>{m.testo}</p>
  </li>;
}
