import { useId } from "react";
import { CloudOff } from "../../config/icone.js";
import { STILI_EDUNEWS24, azioneRiprova } from "../../config/styles/edunews24.js";
import { TESTI_EDUNEWS24 as testi } from "../../config/testi/edunews24.js";
import ScheletroEduNews24 from "./ScheletroEduNews24.jsx";
import Sigillo from "./Sigillo.jsx";

/**
 * Stati del corpo del modulo, alla stessa altezza minima del contenuto:
 * - "scheletro": il menabo' statico della sezione;
 * - "errore": tono neutro (niente rosso: il resto della piattaforma
 *   funziona), "Riprova" con aria-disabled finche' `bloccato` (Retry-After) e
 *   la nota con i secondi iniziali collegata con aria-describedby;
 * - "vuoto": sigillo, titolo e riga della sezione; l'azione e' il link del
 *   piede ("Tutte le ...").
 * `errore` e' quello composto da useModuloEduNews24: { titolo, dettaglio, nota }.
 */
export default function StatoModuloEduNews24({ stato, sezione, errore, bloccato = false, onRiprova }) {
  const idNota = useId();

  if (stato === "scheletro") return <ScheletroEduNews24 contesto="modulo" sezione={sezione} />;

  if (stato === "errore" && errore) {
    return (
      <div className="edunews24-stato" data-tipo="errore" role="status">
        <CloudOff aria-hidden="true" className="edunews24-stato__icona" />
        <p className={STILI_EDUNEWS24.titoloStato}>{errore.titolo}</p>
        <p className={STILI_EDUNEWS24.rigaStato}>{errore.dettaglio}</p>
        <div className="edunews24-azioni">
          <button type="button" className={azioneRiprova()} aria-disabled={bloccato}
            aria-describedby={errore.nota ? idNota : undefined}
            onClick={() => {
              if (!bloccato) onRiprova();
            }}>
            {testi.riprova}
          </button>
          {errore.nota && <p id={idNota} className={STILI_EDUNEWS24.notaStato}>{errore.nota}</p>}
        </div>
      </div>
    );
  }

  if (stato === "vuoto") {
    const vuoto = testi.vuotiModulo[sezione] ?? testi.vuotiModulo.notizie;
    return (
      <div className="edunews24-stato" data-tipo="vuoto">
        <Sigillo />
        <p className={STILI_EDUNEWS24.titoloStato}>{vuoto.titolo}</p>
        <p className={STILI_EDUNEWS24.rigaStato}>{vuoto.riga}</p>
      </div>
    );
  }

  return null;
}
