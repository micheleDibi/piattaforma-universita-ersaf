import { useState } from "react";
import { LoaderCircle } from "../../config/icone.js";
import { STILI_ACCESSO as stili } from "../../config/styles/accesso.js";
import { TESTI_ACCESSO as testi } from "../../config/testi/accesso.js";
import { messaggioErrorePasskey, passkeySupportate, usaPasskey } from "../../lib/passkey.js";
import { verificaPasskey } from "../../lib/secondoFattore.js";
import AlertMessage from "../AlertMessage.jsx";

/**
 * Passo passkey al login: un pulsante apre la finestra del browser (QR per il
 * telefono o notifica), la risposta firmata torna al server che emette la sessione.
 */
export default function ModuloPasskey({ sfida, onVerificato, onAnnulla }) {
  const t = testi.passkey;
  const [errore, setErrore] = useState(passkeySupportate() ? "" : t.nonSupportata);
  const [occupato, setOccupato] = useState(false);

  const avvia = async () => {
    if (occupato) return;
    setOccupato(true);
    setErrore("");
    try {
      const credenziale = await usaPasskey(sfida.opzioni);
      onVerificato(await verificaPasskey(sfida, credenziale));
    } catch (erroreOperazione) {
      setErrore(erroreOperazione.attesaSecondi !== undefined ? erroreOperazione.message : messaggioErrorePasskey(erroreOperazione));
    } finally {
      setOccupato(false);
    }
  };

  return (
    <div className={stili.contenuto} aria-busy={occupato}>
      <AlertMessage message={errore ? { type: "error", text: errore } : null} separato={false} />
      <p className={stili.nota}>{t.istruzioni}</p>
      <button type="button" className={stili.azione} onClick={() => void avvia()} disabled={occupato || !passkeySupportate()}>
        {occupato && <LoaderCircle aria-hidden="true" className={stili.caricamento} />}
        {occupato ? t.inCorso : t.usa}
      </button>
      <button type="button" onClick={onAnnulla} disabled={occupato} className={stili.collegamento}>Indietro</button>
    </div>
  );
}
