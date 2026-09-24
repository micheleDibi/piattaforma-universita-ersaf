import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { TESTI_IMMATRICOLAZIONI as testi } from "../config/testi/anagrafica.js";
import { daCasella, eVero } from "../lib/flagLegacy";
import { campo, spunta } from "../config/styles/campo";
import { STILI_ANAGRAFICA as stili } from "../config/styles/anagrafica.js";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

export default function ImmatricolazioniIscrizioni({ formData, handleChange }) {
  const testo = (nome, etichetta, colonne, tipo = "text") => (
    <CampoModulo per={nome} etichetta={etichetta} colonne={colonne}>
      <input
        id={nome}
        type={tipo}
        name={nome}
        value={formData[nome] || ""}
        onChange={handleChange}
        className={campo("comodo")}
      />
    </CampoModulo>
  );

  const scelta = (nome, etichetta, colonne, segnaposto, opzioni, valore = formData[nome] || "") => (
    <CampoModulo per={nome} etichetta={etichetta} colonne={colonne}>
      <select
        id={nome}
        name={nome}
        value={valore}
        onChange={handleChange}
        className={campo("comodo")}
      >
        <option value="" data-segnaposto>{segnaposto}</option>
        {opzioni.map(([valoreOpzione, etichettaOpzione]) => (
          <option key={valoreOpzione} value={valoreOpzione}>{etichettaOpzione}</option>
        ))}
      </select>
    </CampoModulo>
  );

  // La casella salva -1 o 0 (convenzione legacy), non true/false.
  const cambiaAltraUniversita = (evento) =>
    handleChange({
      target: {
        name: "universita_iscrizioneAltraUniversita",
        value: daCasella(evento.target.checked),
        type: "number",
      },
    });

  return (
    <div>
      <SezioneModulo titolo={testi.anagrafe.titolo} descrizione={testi.anagrafe.descrizione}>
        {scelta(
          "universita_immatricolato",
          testi.status,
          3,
          SEGNAPOSTI_SELEZIONE.stato,
          testi.stati,
          formData.universita_immatricolato !== undefined ? formData.universita_immatricolato : "",
        )}
        {scelta("universita_riforma", testi.tipoCorso, 3, SEGNAPOSTI_SELEZIONE.tipoCorso, testi.riforme)}
        {testo("universita_ateneoNullaosta", testi.ateneo, 4)}
        {testo("universita_data_immatricolazione", testi.dataImmatricolazione, 2, "date")}
        {testo("universita_universitaConclusione", testi.universita, 3)}
        {testo("universita_cittaUniConclusione", testi.citta, 2)}
        {testo("universita_provinciaConclusione", testi.provincia, 1)}
        {scelta("universita_conclusione", testi.conclusione, 4, SEGNAPOSTI_SELEZIONE.generico, testi.conclusioni)}
        {testo("universita_data_conclusione", testi.dataConclusione, 2, "date")}
      </SezioneModulo>

      <SezioneModulo titolo={testi.iscrizione.titolo} descrizione={testi.iscrizione.descrizione}>
        <label className={stili.sceltaIscrizione}>
          <input
            type="checkbox"
            name="universita_iscrizioneAltraUniversita"
            checked={eVero(formData.universita_iscrizioneAltraUniversita)}
            onChange={cambiaAltraUniversita}
            className={spunta()}
          />
          {testi.altraUniversita}
        </label>
        {scelta("universita_attIscritto_tipo", testi.tipo, 3, SEGNAPOSTI_SELEZIONE.tipo, testi.tipi)}
        {testo("universita_attIscritto_altro", testi.altro, 3)}
        {testo("universita_attIscritto_classeLaurea", testi.classeLaurea, 2)}
        {testo("universita_attIscritto_denominazione", testi.denominazione, 4)}
        {testo("universita_attIscritto_universita", testi.universita, 6)}
        {testo("universita_attIscritto_citta", testi.citta, 2)}
        {testo("universita_attIscritto_provincia", testi.provincia, 1)}
        {testo("universita_attIscritto_annoIscrizione", testi.anno, 1)}
        {scelta("universita_attIscritto_modalita", testi.modalita, 2, testi.segnapostoModalita, testi.modalitaCorso)}
      </SezioneModulo>
    </div>
  );
}
