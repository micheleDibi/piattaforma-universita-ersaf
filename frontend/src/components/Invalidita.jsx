import { campo, etichetta } from "../config/styles/campo";
import { titoloSezione } from "../config/styles/superficie";

export default function Invalidita({ formData, handleChange }) {
  return (
    <div className="space-y-6 text-testo max-w-2xl">
      <h3 className={titoloSezione("separato")}>
        Dati Invalidità
      </h3>

      <div className="space-y-4">
        <div>
          <label className={etichetta()}>
            Percentuale
          </label>
          {/* La colonna e' un int. Era type="text" con placeholder "Es. 75%":
              scrivendo davvero "75%" l'intera creazione del cliente falliva
              con un 422, per un campo secondario in fondo al form. */}
          <input
            type="number"
            min="0"
            max="100"
            name="universita_percentualeInvalidita"
            value={formData.universita_percentualeInvalidita ?? ""}
            onChange={handleChange}
            placeholder="Es. 75"
            className={campo()}
          />
        </div>

        <div>
          <label className={etichetta()}>
            Tipo di Invalidità
          </label>
          <input
            type="text"
            name="universita_tipoInvalidita"
            value={formData.universita_tipoInvalidita || ""}
            onChange={handleChange}
            className={campo()}
          />
        </div>
      </div>
    </div>
  );
}
