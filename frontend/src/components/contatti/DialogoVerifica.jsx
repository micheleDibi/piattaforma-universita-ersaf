import { createPortal } from "react-dom";
import Dialogo from "../shared/Dialogo.jsx";
import ModuloOtp from "../accesso/ModuloOtp.jsx";
import { operazioniContattoOtp } from "../../lib/otp.js";
import { STILI_ACCESSO as stili } from "../../config/styles/accesso.js";

export default function DialogoVerifica({ clienteId, contatto, onVerificato, onChiudi }) {
  const operazioni = operazioniContattoOtp(clienteId, contatto.tipo, contatto.valore);
  return createPortal(<Dialogo aperto onChiudi={onChiudi} etichetta="Verifica contatto" variante="otp">
    <div className="dialogo__contenuto overflow-y-auto">
      <header className={stili.intestazione}>
        <h2 className={stili.titolo}>Verifica {contatto.tipo === "email" ? "email" : "cellulare"}</h2>
        <p className={stili.descrizione}>Invieremo un codice a {contatto.valore}.</p>
      </header>
      <ModuloOtp operazioni={operazioni} onVerificato={onVerificato} onAnnulla={onChiudi} />
    </div>
  </Dialogo>, document.body);
}
