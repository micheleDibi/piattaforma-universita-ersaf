import { useEffect, useState } from "react";
import { useSessione } from "../../hooks/useSessione.js";
import { ricaricaSessione } from "../../lib/api.js";
import { contenutoPagina } from "../../config/styles/pagina.js";
import { pulsante } from "../../config/styles/pulsante.js";
import AlertMessage from "../AlertMessage.jsx";
import IndicatoreCaricamento from "./IndicatoreCaricamento.jsx";

/** Mostra `children(ruolo)` solo dopo aver riletto il ruolo dal server.
 *
 * Il ruolo della sessione in memoria e' quello dell'accesso: se nel frattempo
 * e' cambiato (per esempio dalla scheda Utente), la pagina lo crederebbe
 * ancora quello vecchio fino a una ricarica. Le pagine che cambiano aspetto
 * per ruolo (elenco e scheda pratica del Nazionale) passano di qui, cosi'
 * decidono sempre sul ruolo attuale; la rilettura aggiorna anche il menu. */
export default function ConRuoloVerificato({ children }) {
  const sessione = useSessione();
  const [stato, setStato] = useState({ verificato: false, errore: null });
  const [tentativo, setTentativo] = useState(0);
  useEffect(() => {
    let attivo = true;
    ricaricaSessione()
      .then(() => attivo && setStato({ verificato: true, errore: null }))
      .catch((errore) => attivo && setStato({ verificato: false, errore: errore.message }));
    return () => {
      attivo = false;
    };
  }, [tentativo]);

  if (stato.errore) {
    return (
      <div className={contenutoPagina()}>
        <AlertMessage message={{ type: "error", text: stato.errore }} />
        <button
          type="button"
          className={pulsante("secondario")}
          onClick={() => {
            setStato({ verificato: false, errore: null });
            setTentativo((n) => n + 1);
          }}
        >
          Riprova
        </button>
      </div>
    );
  }
  if (!stato.verificato) return <IndicatoreCaricamento messaggio="Caricamento…" centrato />;
  return children(sessione?.ruoloCodice ?? "");
}
