import { useState } from "react";
import { KeyRound, Mail, Smartphone } from "../../config/icone.js";
import { STILI_SICUREZZA as stili } from "../../config/styles/sicurezza.js";
import { TESTI_SICUREZZA as testi } from "../../config/testi/sicurezza.js";
import { useSicurezza } from "../../hooks/useSicurezza.js";
import { dataAttivazione } from "../../lib/sicurezza.js";
import AlertMessage from "../AlertMessage.jsx";
import IndicatoreCaricamento from "../shared/IndicatoreCaricamento.jsx";
import AggiuntaPasskey from "./AggiuntaPasskey.jsx";
import AttivazioneAuthenticator from "./AttivazioneAuthenticator.jsx";
import DisattivazioneAuthenticator from "./DisattivazioneAuthenticator.jsx";
import RimozionePasskey from "./RimozionePasskey.jsx";

function Metodo({ Icona, titolo, descrizione, stato, attivo, azioni, children }) {
  return (
    <li className={stili.riga}>
      <div className={stili.testata}>
        <Icona aria-hidden="true" className={stili.icona} />
        <div className="min-w-0 flex-1">
          <h3 className={stili.nome}>{titolo}</h3>
          <p className={stili.descrizione}>{descrizione}</p>
          {stato && <p className={attivo ? stili.statoAttivo : stili.stato}>{stato}</p>}
          {children}
        </div>
      </div>
      {azioni && <div className={stili.azioni}>{azioni}</div>}
    </li>
  );
}

/**
 * I metodi del secondo fattore del Nazionale: stato di ciascuno e azioni.
 * L'email non si attiva qui, si verifica al login; authenticator e passkey
 * si aggiungono e tolgono in finestre di dialogo, l'elenco resta com'e'.
 */
export default function SicurezzaProfilo() {
  const { stato, errore, caricamento, ricarica } = useSicurezza();
  const [modulo, setModulo] = useState(null);
  const [esito, setEsito] = useState("");

  if (caricamento) return <IndicatoreCaricamento dimensione="normale" messaggio={testi.caricamento} centrato />;
  if (errore) {
    return <>
      <AlertMessage message={{ type: "error", text: errore }} />
      <button type="button" onClick={ricarica} className={stili.azioneSecondaria}>{testi.riprova}</button>
    </>;
  }

  const chiudi = (messaggio) => { setModulo(null); if (messaggio) setEsito(messaggio); ricarica(); };
  const apri = (quale) => { setEsito(""); setModulo(quale); };
  const ta = testi.authenticator;
  const tp = testi.passkey;
  const statoEmail = !stato.email.destinatario ? testi.email.assente
    : stato.email.verificata ? testi.email.verificata(stato.email.destinatario) : testi.email.nonVerificata;
  const statoTotp = stato.totp.attivo ? ta.attivaDal(dataAttivazione(stato.totp.attivato_il))
    : stato.totp.pendente ? ta.pendente : ta.nonAttivo;

  return (
    <section className={stili.sezione} aria-labelledby="sicurezza-titolo">
      <div>
        <h2 id="sicurezza-titolo" className={stili.titoloSezione}>{testi.titolo}</h2>
        <p className={stili.introduzione}>{testi.introduzione}</p>
        <p className={stili.proposto}>
          {stato.proposto ? testi.proposto(testi.metodi[stato.proposto]) : testi.nessunMetodo}
        </p>
      </div>
      {esito && <AlertMessage message={{ type: "info", text: esito }} />}
      <ul className={stili.elenco}>
        <Metodo Icona={KeyRound} titolo={tp.titolo} descrizione={tp.descrizione}
          stato={stato.passkey.length === 0 ? tp.nessuna : null}
          azioni={<button type="button" className={stili.azionePrimaria} onClick={() => apri("passkey")}>{tp.aggiungi}</button>}>
          {stato.passkey.length > 0 && <ul className={stili.elencoPasskey}>
            {stato.passkey.map((p) => (
              <li key={p.id} className={stili.passkey}>
                <div>
                  <p className={stili.passkeyNome}>{p.nome}</p>
                  <p className={stili.passkeyDettagli}>
                    {[tp.aggiuntaIl(dataAttivazione(p.creata_il)), p.ultimo_uso ? tp.ultimoUso(dataAttivazione(p.ultimo_uso)) : tp.maiUsata,
                      p.sincronizzata ? tp.sincronizzata : null].filter(Boolean).join(" · ")}
                  </p>
                </div>
                <button type="button" className={stili.azioneDiscreta} onClick={() => apri(p)}>{tp.rimuovi}</button>
              </li>
            ))}
          </ul>}
        </Metodo>
        <Metodo Icona={Smartphone} titolo={ta.titolo} descrizione={ta.descrizione} stato={statoTotp} attivo={stato.totp.attivo}
          azioni={stato.totp.attivo
            ? <button type="button" className={stili.azioneSecondaria} onClick={() => apri("disattiva")}>{ta.disattiva}</button>
            : <button type="button" className={stili.azionePrimaria} onClick={() => apri("attiva")}>{ta.attiva}</button>} />
        <Metodo Icona={Mail} titolo={testi.email.titolo} descrizione={testi.email.descrizione}
          stato={statoEmail} attivo={stato.email.verificata} />
      </ul>
      {modulo === "passkey" && <AggiuntaPasskey onFatto={chiudi} onAnnulla={() => setModulo(null)} />}
      {modulo === "attiva" && <AttivazioneAuthenticator onFatto={chiudi} onAnnulla={() => setModulo(null)} />}
      {modulo === "disattiva" && <DisattivazioneAuthenticator onFatto={chiudi} onAnnulla={() => setModulo(null)} />}
      {modulo && typeof modulo === "object" && <RimozionePasskey passkey={modulo} onFatto={chiudi} onAnnulla={() => setModulo(null)} />}
    </section>
  );
}
