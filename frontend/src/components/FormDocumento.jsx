import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { campo } from "../config/styles/campo";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

export default function FormDocumento({ formData, handleChange }) {
  const testo = (nome, etichetta, colonne, tipo = "text") => (
    <CampoModulo
      key={nome}
      per={nome}
      etichetta={etichetta}
      obbligatorio
      colonne={colonne}
    >
      <input
        id={nome}
        type={tipo}
        name={nome}
        value={formData[nome]}
        onChange={handleChange}
        className={`${campo("comodo")} transition`}
        required
      />
    </CampoModulo>
  );

  return (
    <SezioneModulo
      titolo="Documento"
      descrizione="Documento di riconoscimento in corso di validità."
    >
      <CampoModulo per="tipoDocumento" etichetta="Tipo documento" colonne={3}>
        <select
          id="tipoDocumento"
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
      </CampoModulo>
      {testo("nDocumento", "N° documento", 3)}
      {testo("comuneDiRilascio", "Comune di rilascio", 2)}
      {testo("dataInizioRilascio", "Data rilascio", 2, "date")}
      {testo("dataScadenza", "Data scadenza", 2, "date")}
    </SezioneModulo>
  );
}
