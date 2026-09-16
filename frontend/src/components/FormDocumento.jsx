import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { campo, etichetta } from "../config/styles/campo";
import { titoloSezione } from "../config/styles/superficie";

export default function FormDocumento({ formData, handleChange }) {
  return (
    <div className="space-y-4">
      <h3 className={titoloSezione()}>Documento</h3>

      <div>
        <label className={etichetta()}>Tipo Documento</label>
        <select
          name="tipoDocumento"
          value={formData.tipoDocumento}
          onChange={handleChange}
          className={`${campo("comodo")} transition`}
        >
          <option value="" data-segnaposto>
            {SEGNAPOSTI_SELEZIONE.documento}
          </option>
          <option value="Carta d'identità">Carta d'identità</option>
          <option value="Passaporto">Passaporto</option>
          <option value="Patente">Patente</option>
        </select>
      </div>

      <div>
        <label className={etichetta()}>
          N° Documento <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          name="nDocumento"
          value={formData.nDocumento}
          onChange={handleChange}
          className={`${campo("comodo")} transition`}
          required
        />
      </div>

      <div>
        <label className={etichetta()}>
          Comune di Rilascio <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          name="comuneDiRilascio"
          value={formData.comuneDiRilascio}
          onChange={handleChange}
          className={`${campo("comodo")} transition`}
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={etichetta()}>
            Data Rilascio <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            name="dataInizioRilascio"
            value={formData.dataInizioRilascio}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
            required
          />
        </div>
        <div>
          <label className={etichetta()}>
            Data Scadenza <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            name="dataScadenza"
            value={formData.dataScadenza}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
            required
          />
        </div>
      </div>
    </div>
  );
}
