import { campo, etichetta } from "../config/styles/campo";
import { titoloSezione } from "../config/styles/superficie";

import CampoContatto from "./contatti/CampoContatto.jsx";
import DialogoVerifica from "./contatti/DialogoVerifica.jsx";
import AlertMessage from "./AlertMessage.jsx";
import { useContattiVerificati } from "../hooks/useContattiVerificati.js";

export default function FormContatti({ formData, handleChange, clienteId }) {
  const contatti = useContattiVerificati(clienteId);
  const verifica = (tipo) => ({ disponibile: Boolean(clienteId), stato: contatti.stato?.[tipo],
    apri: () => contatti.setSelezionato({ tipo, valore: formData[tipo] }) });
  return (
    <div className="space-y-4">
      <h3 className={titoloSezione()}>Contatti</h3>
      <AlertMessage message={contatti.messaggio} separato={false} />
      {contatti.stato?.attivazione === "in_attesa" && <p className="text-sm text-testo-tenue">Verifica email e cellulare per attivare l’account. Le credenziali saranno inviate via email.</p>}
      {contatti.selezionato && <DialogoVerifica clienteId={clienteId} contatto={contatti.selezionato}
        onVerificato={contatti.completato} onChiudi={() => contatti.setSelezionato(null)} />}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <CampoContatto tipo="email" valore={formData.email} onChange={handleChange} verifica={verifica("email")} />
        <div>
          <label className={etichetta()}>
            PEC
          </label>
          <input
            type="email"
            name="pec"
            value={formData.pec}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
        <CampoContatto tipo="cellulare" valore={formData.cellulare} onChange={handleChange} verifica={verifica("cellulare")} />
        <div>
          <label className={etichetta()}>
            Telefono
          </label>
          <input
            type="text"
            name="telefono"
            value={formData.telefono}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
      </div>
    </div>
  );
}
