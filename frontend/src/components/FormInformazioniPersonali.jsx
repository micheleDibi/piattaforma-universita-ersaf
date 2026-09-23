import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { campo } from "../config/styles/campo";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

export default function FormInformazioniPersonali({ formData, handleChange }) {
  const testo = (nome, etichetta, colonne, { obbligatorio, tipo = "text" } = {}) => (
    <CampoModulo
      key={nome}
      per={nome}
      etichetta={etichetta}
      obbligatorio={obbligatorio}
      colonne={colonne}
    >
      <input
        id={nome}
        type={tipo}
        name={nome}
        value={formData[nome]}
        onChange={handleChange}
        className={`${campo("comodo")} transition`}
        required={obbligatorio && nome !== "codiceFiscale"}
      />
    </CampoModulo>
  );

  return (
    <SezioneModulo
      titolo="Informazioni personali"
      descrizione="Dati anagrafici della persona."
    >
      {testo("nome", "Nome", 3, { obbligatorio: true })}
      {testo("cognome", "Cognome", 3, { obbligatorio: true })}
      {testo("codiceFiscale", "Codice fiscale", 4, { obbligatorio: true })}
      <CampoModulo per="genere" etichetta="Genere" colonne={2}>
        <select
          id="genere"
          name="genere"
          value={formData.genere}
          onChange={handleChange}
          className={`${campo("comodo")} transition`}
        >
          <option value="" data-segnaposto>
            {SEGNAPOSTI_SELEZIONE.genere}
          </option>
          <option value="uomo">uomo</option>
          <option value="donna">donna</option>
        </select>
      </CampoModulo>
      {testo("dataDiNascita", "Data di nascita", 2, {
        obbligatorio: true,
        tipo: "date",
      })}
      {testo("luogoDiNascita", "Luogo di nascita", 3, { obbligatorio: true })}
      {testo("provDiNascita", "Prov.", 1)}
      {testo("cittadinanza", "Cittadinanza", 3, { obbligatorio: true })}
    </SezioneModulo>
  );
}
