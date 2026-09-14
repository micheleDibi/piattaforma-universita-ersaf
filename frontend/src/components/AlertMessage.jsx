import { CircleAlert, CircleCheck, Info, TriangleAlert } from "../config/icone.js";
import { feedback, STILI_FEEDBACK as stili } from "../config/styles/feedback.js";
import { useIngresso } from "../hooks/useIngresso.js";

const ICONE = { error: CircleAlert, success: CircleCheck, info: Info, warning: TriangleAlert };

export default function AlertMessage({ message, separato = true, id }) {
  const riferimento = useIngresso(message?.type);
  if (!message) return null;
  const Icona = ICONE[message.type] ?? CircleAlert;
  return (
    <div ref={riferimento} id={id} role={message.type === "error" ? "alert" : "status"}
      className={feedback(message.type, { separato })}>
      <Icona aria-hidden="true" className={stili.icona} />
      <span className={stili.testo}>{message.text}</span>
    </div>
  );
}
