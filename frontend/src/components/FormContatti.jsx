import { campo, etichetta } from "../config/styles/campo";
import { titoloSezione } from "../config/styles/superficie";

export default function FormContatti({ formData, handleChange }) {
  return (
    <div className="space-y-4">
      <h3 className={titoloSezione()}>Contatti</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className={etichetta()}>
            Email
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
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
        <div>
          <label className={etichetta()}>
            Cellulare
          </label>
          <input
            type="text"
            name="cellulare"
            value={formData.cellulare}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
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
