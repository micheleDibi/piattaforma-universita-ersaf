import { useState } from "react";
import { useFirmaPratica } from "../../hooks/useFirmaPratica.js";
import { TESTI_FIRMA as testi } from "../../config/testi/firma.js";
import { STILI_FIRMA as stili } from "../../config/styles/firma.js";
import { pulsante } from "../../config/styles/pulsante.js";
import AlertMessage from "../AlertMessage.jsx";
import Dialogo from "../shared/Dialogo.jsx";
import DisegnoFirma from "./DisegnoFirma.jsx";

export default function FirmaPratica({ praticaId }) {
  const firma = useFirmaPratica(praticaId);
  const [aperto, setAperto] = useState(false);
  const chiudi = () => { if (!firma.occupato) setAperto(false); };
  const salva = async png => { if (await firma.salva(png)) setAperto(false); };
  const errore = firma.errore ? { type: "error", text: firma.errore } : null;
  return <section className={stili.sezione} aria-label={testi.titolo}>
    <h2 className={stili.titolo}>{testi.titolo}</h2>
    {!aperto && <AlertMessage message={errore || (firma.messaggio ? { type: "success", text: firma.messaggio } : null)} />}
    {firma.dati?.immagine ? <img src={firma.dati.immagine} alt={testi.anteprima} className={stili.anteprima} />
      : <p className={stili.nota}>{firma.dati ? testi.assente : firma.errore ? "" : testi.caricamento}</p>}
    <div className={stili.azioni}>
      {firma.errore && <button type="button" className={pulsante("secondario")} onClick={firma.ricarica}>{testi.riprova}</button>}
      <button type="button" className={pulsante("secondario")} disabled={!firma.dati} onClick={() => setAperto(true)}>{firma.dati?.presente ? testi.sostituisci : testi.acquisisci}</button>
    </div>
    <Dialogo aperto={aperto} onChiudi={chiudi} etichetta={testi.titolo}>
      {aperto && <div className={stili.dialogo}>
        <h2 className={stili.titolo}>{testi.titolo}</h2>
        {firma.dati?.presente && <p className={stili.nota}>{testi.avviso}</p>}
        <AlertMessage message={errore} />
        {firma.errore && <button type="button" disabled={firma.occupato} className={pulsante("secondario")} onClick={firma.ricarica}>{testi.riprova}</button>}
        <DisegnoFirma occupato={firma.occupato || !firma.dati} onSalva={salva} onAnnulla={chiudi} />
      </div>}
    </Dialogo>
  </section>;
}
