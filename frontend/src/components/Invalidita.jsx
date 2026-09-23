import { campo, etichetta } from "../config/styles/campo";
import SezioneModulo from "./shared/SezioneModulo.jsx";

export default function Invalidita({ formData, handleChange }) {
  return (
    <SezioneModulo
      titolo="Dati invalidità"
      descrizione="Compilare solo se applicabile."
      griglia={false}
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
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
    </SezioneModulo>
  );
}
