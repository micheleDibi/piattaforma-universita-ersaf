import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { TESTI_DOCUMENTO as testi } from "../config/testi/anagrafica.js";
import { campo } from "../config/styles/campo";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

/**
 * @param {{ note?: Record<string, string[]> }} props
 *   note: note brevi per campo ricavate dalle anomalie (numero duplicato).
 */
export default function FormDocumento({ formData, handleChange, note = {} }) {
  const testo = (nome, colonne, tipo = "text") => {
    const notaCampo = note[nome];
    const avviso = Boolean(notaCampo);
    return (
      <CampoModulo
        key={nome}
        per={nome}
        etichetta={testi[nome]}
        obbligatorio
        colonne={colonne}
        nota={notaCampo}
        tonoNota="avviso"
      >
        <input
          id={nome}
          type={tipo}
          name={nome}
          value={formData[nome]}
          onChange={handleChange}
          className={campo("comodo", { avviso })}
          required
          aria-describedby={avviso ? `${nome}-nota` : undefined}
        />
      </CampoModulo>
    );
  };

  return (
    <SezioneModulo titolo={testi.titolo} descrizione={testi.descrizione}>
      <CampoModulo per="tipoDocumento" etichetta={testi.tipoDocumento} colonne={3}>
        <select
          id="tipoDocumento"
          name="tipoDocumento"
          value={formData.tipoDocumento}
          onChange={handleChange}
          className={campo("comodo")}
        >
          <option value="" data-segnaposto>
            {SEGNAPOSTI_SELEZIONE.documento}
          </option>
          {testi.tipi.map(([valore, etichetta]) => (
            <option key={valore} value={valore}>{etichetta}</option>
          ))}
        </select>
      </CampoModulo>
      {testo("nDocumento", 3)}
      {testo("comuneDiRilascio", 2)}
      {testo("dataInizioRilascio", 2, "date")}
      {testo("dataScadenza", 2, "date")}
    </SezioneModulo>
  );
}
