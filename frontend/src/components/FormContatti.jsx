import { campo, etichetta, notaCampo } from "../config/styles/campo";
import { STILI_ANAGRAFICA as stili } from "../config/styles/anagrafica.js";
import { TESTI_CONTATTI as testi } from "../config/testi/anagrafica.js";

import CampoContatto from "./contatti/CampoContatto.jsx";
import DialogoVerifica from "./contatti/DialogoVerifica.jsx";
import AlertMessage from "./AlertMessage.jsx";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import { useContattiVerificati } from "../hooks/useContattiVerificati.js";

/**
 * Email e cellulare in due schede in evidenza, poi PEC e telefono come
 * recapiti secondari. `note`: note brevi per campo ricavate dalle anomalie.
 */
export default function FormContatti({ formData, handleChange, clienteId, note = {} }) {
  const contatti = useContattiVerificati(clienteId);
  const verifica = (tipo) => ({ disponibile: Boolean(clienteId), stato: contatti.stato?.[tipo],
    apri: () => contatti.setSelezionato({ tipo, valore: formData[tipo] }) });
  // Recapito secondario: fuori da CampoModulo perche' sta in una griglia
  // a colonne automatiche, non in quella di 6.
  const secondario = (nome, tipo) => {
    const noteCampo = note[nome] ?? [];
    const avviso = noteCampo.length > 0;
    return (
      <div className={stili.campoSecondario}>
        <label htmlFor={nome} className={etichetta("secondaria")}>
          {testi[nome]}
        </label>
        <input
          id={nome}
          type={tipo}
          name={nome}
          value={formData[nome]}
          onChange={handleChange}
          className={campo("secondario", { avviso })}
          aria-describedby={avviso ? `${nome}-nota` : undefined}
        />
        {avviso && (
          <p id={`${nome}-nota`} className={notaCampo("avviso")}>
            {noteCampo.map((testo, indice) => (
              <span key={`${indice}-${testo}`} className="block">{testo}</span>
            ))}
          </p>
        )}
      </div>
    );
  };
  return (
    <SezioneModulo titolo={testi.titolo} descrizione={testi.descrizione} griglia={false}>
      <div className={stili.colonnaContatti}>
        <div className={stili.messaggiContatti}>
          <AlertMessage message={contatti.messaggio} separato={false} />
          {contatti.stato?.attivazione === "in_attesa" && (
            <p className={stili.messaggioAttivazione}>{testi.attivazione}</p>
          )}
        </div>
        <div className={stili.grigliaRecapiti}>
          <CampoContatto tipo="email" valore={formData.email} onChange={handleChange}
            verifica={verifica("email")} nota={note.email} />
          <CampoContatto tipo="cellulare" valore={formData.cellulare} onChange={handleChange}
            verifica={verifica("cellulare")} nota={note.cellulare} />
        </div>
        <div className={stili.altriRecapiti}>
          <span className={stili.didascalia}>{testi.altriRecapiti}</span>
          <div className={stili.grigliaAltriRecapiti}>
            {secondario("pec", "email")}
            {secondario("telefono", "text")}
          </div>
        </div>
      </div>
      {contatti.selezionato && <DialogoVerifica clienteId={clienteId} contatto={contatti.selezionato}
        onVerificato={contatti.completato} onChiudi={() => contatti.setSelezionato(null)} />}
    </SezioneModulo>
  );
}
