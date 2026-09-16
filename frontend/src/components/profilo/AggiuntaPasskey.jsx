import { useId, useState } from "react";
import { STILI_SICUREZZA as stili } from "../../config/styles/sicurezza.js";
import { TESTI_SICUREZZA as testi } from "../../config/testi/sicurezza.js";
import { creaPasskey, messaggioErrorePasskey, passkeySupportate } from "../../lib/passkey.js";
import { confermaPasskey, opzioniPasskey } from "../../lib/sicurezza.js";
import AlertMessage from "../AlertMessage.jsx";

/**
 * Aggiunta in tre passi: password (il server apre la sfida e prepara le
 * opzioni), telefono (il browser crea la passkey), nome (si salva).
 */
export default function AggiuntaPasskey({ onFatto, onAnnulla }) {
  const t = testi.passkey;
  const id = useId();
  const [passo, setPasso] = useState("password");
  const [password, setPassword] = useState("");
  const [nome, setNome] = useState(t.nomeSuggerito);
  const [avvio, setAvvio] = useState(null);
  const [credenziale, setCredenziale] = useState(null);
  const [errore, setErrore] = useState(passkeySupportate() ? "" : t.nonSupportata);
  const [occupato, setOccupato] = useState(false);

  const invia = async (evento) => {
    evento.preventDefault();
    if (occupato) return;
    setOccupato(true);
    setErrore("");
    try {
      if (passo === "password") {
        setAvvio(await opzioniPasskey(password));
        setPassword("");
        setPasso("telefono");
      } else if (passo === "telefono") {
        setCredenziale(await creaPasskey(avvio.opzioni));
        setPasso("nome");
      } else {
        await confermaPasskey(avvio.sfida, credenziale, nome);
        onFatto(t.aggiunta);
      }
    } catch (erroreOperazione) {
      setErrore(erroreOperazione.attesaSecondi !== undefined || passo !== "telefono"
        ? erroreOperazione.message : messaggioErrorePasskey(erroreOperazione));
    } finally {
      setOccupato(false);
    }
  };

  const etichettaAzione = passo === "password" ? testi.continua : passo === "telefono" ? t.avvia : t.salva;
  return (
    <form onSubmit={invia} className={stili.modulo} aria-busy={occupato}>
      <AlertMessage message={errore ? { type: "error", text: errore } : null} separato={false} />
      {passo === "password" && <>
        <p className={stili.passi}>{t.passoPassword}</p>
        <div>
          <label htmlFor={`${id}-password`} className={stili.etichetta}>{testi.password}</label>
          <input id={`${id}-password`} type="password" autoComplete="current-password" required
            value={password} onChange={(e) => setPassword(e.target.value)} className={stili.campo} />
        </div>
      </>}
      {passo === "telefono" && <p className={stili.passi}>{t.passoTelefono}</p>}
      {passo === "nome" && <>
        <p className={stili.passi}>{t.passoNome}</p>
        <div>
          <label htmlFor={`${id}-nome`} className={stili.etichetta}>{t.nome}</label>
          <input id={`${id}-nome`} type="text" required maxLength={80} autoFocus
            value={nome} onChange={(e) => setNome(e.target.value)} className={stili.campo} />
        </div>
      </>}
      <div className={stili.azioni}>
        <button type="submit" className={stili.azionePrimaria}
          disabled={occupato || !passkeySupportate() || (passo === "nome" && !nome.trim())}>
          {occupato ? testi.inCorso : etichettaAzione}
        </button>
        <button type="button" className={stili.azioneDiscreta} onClick={onAnnulla} disabled={occupato}>{testi.annulla}</button>
      </div>
    </form>
  );
}
