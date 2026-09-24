import { contenutoPagina, titoloPagina } from "../config/styles/pagina.js";
import { pulsante } from "../config/styles/pulsante.js";
import { scheda } from "../config/styles/superficie.js";
import { TESTI_COPIA } from "../config/testi/copia.js";
import { copiaTesto } from "../lib/copia.js";
import { useConfermaAzione } from "../hooks/useConfermaAzione.js";
import AlertMessage from "./AlertMessage.jsx";

/** Credenziali mostrate una sola volta, con conferma effettiva della copia. */
export default function CredenzialiCreate({ credenziali, titolo, onContinua }) {
  const { esegui, stato } = useConfermaAzione(() => copiaTesto(`${credenziali.username}\n${credenziali.password}`));
  return (
    <div className={contenutoPagina("modulo")}>
      <div className={`${scheda()} max-w-lg w-full p-8`}>
        <h2 className={`${titoloPagina()} mb-2`}>{titolo} creato</h2>
        <p className="text-sm text-testo-tenue mb-6">Annota queste credenziali e consegnale alla persona: la password non sarà più recuperabile.</p>
        <dl className="rounded-riquadro border border-attenzione-bordo bg-attenzione-tenue px-4.5 py-3.5 mb-6">
          <dt className="text-etichetta uppercase tracking-wider text-attenzione-forte">USERNAME</dt>
          <dd className="font-mono text-base text-testo-forte mb-4 select-all break-all">{credenziali.username}</dd>
          <dt className="text-etichetta uppercase tracking-wider text-attenzione-forte">PASSWORD</dt>
          <dd className="font-mono text-base text-testo-forte select-all break-all">{credenziali.password}</dd>
        </dl>
        {stato === "errore" && <AlertMessage message={{ type: "error", text: TESTI_COPIA.errore }} />}
        <div className="flex gap-3">
          <button type="button" onClick={esegui} disabled={stato === "attesa"} data-esito={stato}
            className={pulsante("ausiliario", "grande")}>{stato === "eseguita" ? TESTI_COPIA.conferma : TESTI_COPIA.comando}</button>
          <button type="button" onClick={onContinua} className={pulsante("primario", "grande")}>Le ho annotate, continua</button>
        </div>
        <span role="status" className="sr-only">{stato === "eseguita" ? TESTI_COPIA.conferma : ""}</span>
      </div>
    </div>
  );
}
