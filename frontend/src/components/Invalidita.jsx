import { campo, suffissoCampo } from "../config/styles/campo";
import { campoConSuffisso, STILI_ANAGRAFICA as stili } from "../config/styles/anagrafica.js";
import { TESTI_INVALIDITA as testi } from "../config/testi/anagrafica.js";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

export default function Invalidita({ formData, handleChange }) {
  return (
    <SezioneModulo titolo={testi.titolo} descrizione={testi.descrizione}>
      <CampoModulo per="universita_percentualeInvalidita" etichetta={testi.percentuale} colonne={2}>
        <div className={stili.conSuffisso}>
          {/* La colonna e' un int. Era type="text" con placeholder "Es. 75%":
              scrivendo davvero "75%" l'intera creazione del cliente falliva
              con un 422, per un campo secondario in fondo al form. Il "%"
              ora e' un suffisso fuori dal valore. */}
          <input
            id="universita_percentualeInvalidita"
            type="number"
            min="0"
            max="100"
            name="universita_percentualeInvalidita"
            value={formData.universita_percentualeInvalidita ?? ""}
            onChange={handleChange}
            placeholder={testi.segnapostoPercentuale}
            className={campoConSuffisso()}
          />
          <span aria-hidden="true" className={suffissoCampo()}>{testi.unita}</span>
        </div>
      </CampoModulo>
      <CampoModulo per="universita_tipoInvalidita" etichetta={testi.tipo} colonne={4}>
        <input
          id="universita_tipoInvalidita"
          type="text"
          name="universita_tipoInvalidita"
          value={formData.universita_tipoInvalidita || ""}
          onChange={handleChange}
          className={campo("comodo")}
        />
      </CampoModulo>
    </SezioneModulo>
  );
}
