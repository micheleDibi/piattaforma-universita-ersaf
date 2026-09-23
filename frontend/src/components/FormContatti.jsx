import { campo } from "../config/styles/campo";

import CampoContatto from "./contatti/CampoContatto.jsx";
import DialogoVerifica from "./contatti/DialogoVerifica.jsx";
import AlertMessage from "./AlertMessage.jsx";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";
import { useContattiVerificati } from "../hooks/useContattiVerificati.js";

export default function FormContatti({ formData, handleChange, clienteId }) {
  const contatti = useContattiVerificati(clienteId);
  const verifica = (tipo) => ({ disponibile: Boolean(clienteId), stato: contatti.stato?.[tipo],
    apri: () => contatti.setSelezionato({ tipo, valore: formData[tipo] }) });
  const testo = (nome, etichetta, tipo) => (
    <CampoModulo per={nome} etichetta={etichetta} colonne={3}>
      <input
        id={nome}
        type={tipo}
        name={nome}
        value={formData[nome]}
        onChange={handleChange}
        className={`${campo("comodo")} transition`}
      />
    </CampoModulo>
  );
  return (
    <SezioneModulo
      titolo="Contatti"
      descrizione="Email e cellulare sono i recapiti usati per l'accesso e le comunicazioni."
    >
      <div className="col-span-6 flex flex-col gap-3 empty:hidden">
        <AlertMessage message={contatti.messaggio} separato={false} />
        {contatti.stato?.attivazione === "in_attesa" && <p className="text-sm text-testo-tenue">Verifica email e cellulare per attivare l’account. Le credenziali saranno inviate via email.</p>}
      </div>
      {contatti.selezionato && <DialogoVerifica clienteId={clienteId} contatto={contatti.selezionato}
        onVerificato={contatti.completato} onChiudi={() => contatti.setSelezionato(null)} />}
      <div className="col-span-6 sm:col-span-3">
        <CampoContatto tipo="email" valore={formData.email} onChange={handleChange} verifica={verifica("email")} />
      </div>
      <div className="col-span-6 sm:col-span-3">
        <CampoContatto tipo="cellulare" valore={formData.cellulare} onChange={handleChange} verifica={verifica("cellulare")} />
      </div>
      {testo("pec", "PEC", "email")}
      {testo("telefono", "Telefono", "text")}
    </SezioneModulo>
  );
}
