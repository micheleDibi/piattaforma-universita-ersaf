import { eVero } from "../lib/flagLegacy";
import { TESTI_ABILITAZIONI as testi } from "../config/testi/anagrafica.js";
import { campo, spunta } from "../config/styles/campo";
import { campoDataStretta, STILI_ANAGRAFICA as stili } from "../config/styles/anagrafica.js";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

// Colonne delle esperienze da convalidare; le etichette stanno in config/testi.
const ESPERIENZE = [
  "universita_attivita_professionalizzanti",
  "universita_corsi_di_formazione",
  "universita_altre_attivita_certificate",
];

export default function AbilitazioniProfessionali({ formData, handleChange }) {
  // Le date stanno in una colonna sola: rientro e testo ridotti.
  const testo = (nome, etichetta, colonne, tipo = "text") => (
    <CampoModulo per={nome} etichetta={etichetta} colonne={colonne}>
      <input
        id={nome}
        type={tipo}
        name={nome}
        value={formData[nome] || ""}
        onChange={handleChange}
        className={tipo === "date" ? campoDataStretta() : campo("comodo")}
      />
    </CampoModulo>
  );

  return (
    <div>
      <SezioneModulo titolo={testi.abilitazione.titolo} descrizione={testi.abilitazione.descrizione}>
        {testo("universita_professione", testi.professione, 3)}
        {testo("universita_data_professione", testi.data, 1, "date")}
        {testo("universita_luogo_professione", testi.luogo, 2)}
        {testo("universita_qualifica_professionale", testi.qualifica, 3)}
        {testo("universita_data_qualifica", testi.data, 1, "date")}
        {testo("universita_luogo", testi.luogo, 2)}
      </SezioneModulo>

      <SezioneModulo titolo={testi.albo.titolo}>
        {testo("universita_albo", testi.alboElenco, 3)}
        {testo("universita_forzeDellOrdine", testi.forzeOrdine, 3)}
      </SezioneModulo>

      <SezioneModulo
        titolo={testi.convalida.titolo}
        descrizione={testi.convalida.descrizione}
        griglia={false}
      >
        <div className={stili.grigliaConvalida}>
          {ESPERIENZE.map((nome) => (
            <label key={nome} className={stili.sceltaConvalida}>
              {/* handleChange salva 1 o 0 per queste tre caselle. */}
              <input
                type="checkbox"
                name={nome}
                checked={eVero(formData[nome])}
                onChange={handleChange}
                className={spunta()}
              />
              {testi.esperienze[nome]}
            </label>
          ))}
        </div>
      </SezioneModulo>
    </div>
  );
}
