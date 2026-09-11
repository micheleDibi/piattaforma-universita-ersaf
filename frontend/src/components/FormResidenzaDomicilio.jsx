import { campo, etichetta } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { titoloSezione } from "../config/styles/superficie";

export default function FormResidenzaDomicilio({
  formData,
  handleChange,
  handleCopyResidenza,
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Residenza */}
      <div className="space-y-4">
        <h3 className={titoloSezione()}>Residenza</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className={etichetta()}>
              Indirizzo
            </label>
            <input
              type="text"
              name="residenzaIndirizzo"
              value={formData.residenzaIndirizzo}
              onChange={handleChange}
              className={`${campo("comodo")} transition`}
            />
          </div>
          <div>
            <label className={etichetta()}>
              Civico
            </label>
            <input
              type="text"
              name="residenzaCivico"
              value={formData.residenzaCivico}
              onChange={handleChange}
              className={`${campo("comodo")} transition`}
            />
          </div>
        </div>
        <div>
          <label className={etichetta()}>
            Comune
          </label>
          <input
            type="text"
            name="residenzaComune"
            value={formData.residenzaComune}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={etichetta()}>
              CAP
            </label>
            <input
              type="text"
              name="residenzaCap"
              value={formData.residenzaCap}
              onChange={handleChange}
              className={`${campo("comodo")} transition`}
            />
          </div>
          <div>
            <label className={etichetta()}>
              Provincia
            </label>
            <input
              type="text"
              name="residenzaProvincia"
              value={formData.residenzaProvincia}
              onChange={handleChange}
              className={`${campo("comodo")} transition`}
            />
          </div>
        </div>
        <div className="pt-2">
          <button
            type="button"
            onClick={handleCopyResidenza}
            className={pulsante("secondario", "normale", { larghezzaPiena: true })}
          >
            Copia Residenza in Domicilio
          </button>
        </div>
      </div>

      {/* Domicilio */}
      <div className="space-y-4">
        <h3 className={titoloSezione()}>Domicilio</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className={etichetta()}>
              Indirizzo Domicilio
            </label>
            <input
              type="text"
              name="domicilioIndirizzo"
              value={formData.domicilioIndirizzo}
              onChange={handleChange}
              className={`${campo("comodo")} transition`}
            />
          </div>
          <div>
            <label className={etichetta()}>
              Civico
            </label>
            <input
              type="text"
              name="domicilioCivico"
              value={formData.domicilioCivico}
              onChange={handleChange}
              className={`${campo("comodo")} transition`}
            />
          </div>
        </div>
        <div>
          <label className={etichetta()}>
            Comune
          </label>
          <input
            type="text"
            name="domicilioComune"
            value={formData.domicilioComune}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={etichetta()}>
              CAP
            </label>
            <input
              type="text"
              name="domicilioCap"
              value={formData.domicilioCap}
              onChange={handleChange}
              className={`${campo("comodo")} transition`}
            />
          </div>
          <div>
            <label className={etichetta()}>
              Provincia
            </label>
            <input
              type="text"
              name="domicilioProvincia"
              value={formData.domicilioProvincia}
              onChange={handleChange}
              className={`${campo("comodo")} transition`}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
