import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { TESTI_INFORMAZIONI as testi } from "../config/testi/anagrafica.js";
import { campo } from "../config/styles/campo";
import { campoCodiceFiscale } from "../config/styles/anagrafica.js";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

/**
 * @param {{ note?: Record<string, string[]>, tipoUtente: "sottoscrittore"|"attuatore" }} props
 *   note: note brevi per campo ricavate dalle anomalie (qui il codice fiscale).
 */
export default function FormInformazioniPersonali({ formData, handleChange, note = {}, tipoUtente }) {
  const testo = (nome, colonne, { obbligatorio, tipo = "text" } = {}) => {
    const notaCampo = note[nome];
    const avviso = Boolean(notaCampo);
    const codice = nome === "codiceFiscale";
    return (
      <CampoModulo
        key={nome}
        per={nome}
        etichetta={testi[nome]}
        obbligatorio={obbligatorio}
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
          className={codice ? campoCodiceFiscale(avviso) : campo("comodo", { avviso })}
          required={obbligatorio && !codice}
          aria-required={obbligatorio || undefined}
          aria-describedby={avviso ? `${nome}-nota` : undefined}
        />
      </CampoModulo>
    );
  };

  return (
    <SezioneModulo titolo={testi.titolo} descrizione={testi.descrizione(tipoUtente)}>
      {testo("nome", 3, { obbligatorio: true })}
      {testo("cognome", 3, { obbligatorio: true })}
      {testo("codiceFiscale", 4, { obbligatorio: true })}
      <CampoModulo per="genere" etichetta={testi.genere} colonne={2}>
        <select
          id="genere"
          name="genere"
          value={formData.genere}
          onChange={handleChange}
          className={campo("comodo")}
        >
          <option value="" data-segnaposto>
            {SEGNAPOSTI_SELEZIONE.genere}
          </option>
          {testi.generi.map(([valore, etichetta]) => (
            <option key={valore} value={valore}>{etichetta}</option>
          ))}
        </select>
      </CampoModulo>
      {testo("dataDiNascita", 2, { obbligatorio: true, tipo: "date" })}
      {testo("luogoDiNascita", 3, { obbligatorio: true })}
      {testo("provDiNascita", 1)}
      {testo("cittadinanza", 3, { obbligatorio: true })}
    </SezioneModulo>
  );
}
