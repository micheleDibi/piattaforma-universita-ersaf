import { CircleAlert, CircleCheck, Info, TriangleAlert } from "../config/icone.js";
import {
  elencoFeedback,
  feedback,
  iconaFeedback,
  STILI_FEEDBACK as stili,
} from "../config/styles/feedback.js";
import { useIngresso } from "../hooks/useIngresso.js";

const ICONE = { error: CircleAlert, success: CircleCheck, info: Info, warning: TriangleAlert };

/**
 * Messaggio di esito o di avviso. `message.text` e' un testo oppure un elenco
 * di voci: con una voce sola resta testo semplice, con piu' voci diventa un
 * elenco puntato (per esempio le anomalie di un'anagrafica).
 */
export default function AlertMessage({ message, separato = true, id }) {
  const riferimento = useIngresso(message?.type);
  if (!message) return null;
  const Icona = ICONE[message.type] ?? CircleAlert;
  const voci = Array.isArray(message.text) ? message.text : null;
  const elenco = voci !== null && voci.length > 1;
  return (
    <div ref={riferimento} id={id} role={message.type === "error" ? "alert" : "status"}
      className={feedback(message.type, { separato, elenco })}>
      <Icona aria-hidden="true" className={iconaFeedback(message.type, { elenco })} />
      {elenco ? (
        <ul className={`${elencoFeedback()} ${stili.testo}`}>
          {voci.map((voce, indice) => <li key={`${indice}-${voce}`}>{voce}</li>)}
        </ul>
      ) : (
        <span className={stili.testo}>{voci ? voci[0] : message.text}</span>
      )}
    </div>
  );
}
