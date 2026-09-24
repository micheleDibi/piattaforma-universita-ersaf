import { useId } from "react";
import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { TESTI_TITOLI } from "../config/testi/titoli.js";
import { campo, etichetta } from "../config/styles/campo";
import { intestazioneCampi, rigaCampi, tabellaCampi } from "../config/styles/tabella";
import {
  campoDataEvidenziata,
  colonnaCampo,
  STILI_ANAGRAFICA as stili,
} from "../config/styles/anagrafica.js";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

// Righe della tabella "Altri titoli": suffisso delle colonne universita_*_<suffisso>.
const ALTRI_TITOLI = ["pl1", "pl2", "ats1", "ats2"];

// Campi dell'anno integrativo: campi e etichette attenuati.
const SECONDARIO = { dimensione: "secondario", secondario: true };

// Gli anni del diploma e dell'anno integrativo sono varchar(45) nel database.
// I due campi degli anni e la data del titolo sono scritti per intero, senza
// funzioni di supporto: tests/sezioneTitoli.test.js ne legge il sorgente.
export default function SezioneTitoli({ formData, handleChange }) {
  const id = useId();
  const t = TESTI_TITOLI;

  const testo = (nome, chiave, etichettaCampo, colonne, { dimensione = "comodo", secondario = false } = {}) => (
    <CampoModulo per={`${id}-${chiave}`} etichetta={etichettaCampo} colonne={colonne} secondario={secondario}>
      <input
        id={`${id}-${chiave}`}
        type="text"
        name={nome}
        value={formData[nome]}
        onChange={handleChange}
        className={campo(dimensione)}
      />
    </CampoModulo>
  );

  // Voto ricevuto e massimo: un gruppo con una sola etichetta visibile.
  const voto = (ricevuto, massimo, chiave, { dimensione = "comodo", secondario = false } = {}) => (
    <div role="group" aria-labelledby={`${id}-${chiave}`} className={colonnaCampo(3)}>
      <span id={`${id}-${chiave}`} className={etichetta(secondario ? "secondaria" : "compatta")}>
        {t.voto}
      </span>
      <div className={stili.voto}>
        <input
          type="number"
          name={ricevuto}
          value={formData[ricevuto]}
          onChange={handleChange}
          aria-label={t.votoRicevuto}
          className={campo(dimensione)}
        />
        <span aria-hidden="true" className={stili.separatoreVoto}>{t.separatoreVoto}</span>
        <input
          type="number"
          name={massimo}
          value={formData[massimo]}
          onChange={handleChange}
          aria-label={t.votoMassimo}
          className={campo(dimensione)}
        />
      </div>
    </div>
  );

  return (
    <div>
      <SezioneModulo
        titolo={t.diploma.titolo}
        descrizione={t.diploma.descrizione}
        etichetta={t.diploma.etichetta}
        rilievo="evidenziato"
        evidenziata
        griglia={false}
      >
        <div className={stili.grigliaCampi}>
          {testo("universita_diploma", "diploma", t.campoDiploma, 6, { dimensione: "evidenziato" })}
          {testo("universita_istituto", "istituto", t.istituto, 4)}
          <div className={colonnaCampo(2)}>
            <label htmlFor={`${id}-anno-diploma`} className={etichetta()}>
              {t.anno}
            </label>
            <input
              id={`${id}-anno-diploma`}
              type="text"
              name="universita_anno_scolastico"
              value={formData.universita_anno_scolastico}
              onChange={handleChange}
              maxLength={45}
              placeholder={TESTI_TITOLI.segnapostoAnno}
              className={campo("comodo")}
            />
          </div>
          {testo("universita_via_istituto", "via", t.via, 3)}
          {testo("universita_citta_istituto", "citta", t.citta, 2)}
          {testo("universita_provincia_istituto", "provincia", t.provincia, 1)}
          {voto("universita_votoRicevuto_diploma", "universita_votoMassimo_diploma", "voto")}
        </div>

        <div className={stili.parteFacoltativa}>
          <span className={stili.didascalia}>{t.integrativo}</span>
          <div className={stili.grigliaSecondaria}>
            {testo("universita_istituto_ai", "presso", t.presso, 4, SECONDARIO)}
            <div className={colonnaCampo(2)}>
              <label htmlFor={`${id}-anno-integrativo`} className={etichetta("secondaria")}>
                {t.anno}
              </label>
              <input
                id={`${id}-anno-integrativo`}
                type="text"
                name="universita_anno_scolastico_ai"
                value={formData.universita_anno_scolastico_ai}
                onChange={handleChange}
                maxLength={45}
                placeholder={TESTI_TITOLI.segnapostoAnno}
                className={campo("secondario")}
              />
            </div>
            {testo("universita_via_istituto_ai", "via-integrativo", t.via, 3, SECONDARIO)}
            {testo("universita_citta_istituto_ai", "citta-integrativo", t.citta, 2, SECONDARIO)}
            {testo("universita_provincia_istituto_ai", "provincia-integrativo", t.provincia, 1, SECONDARIO)}
            {voto("universita_votoRicevuto_ai", "universita_votoMassimo_ai", "voto-integrativo", SECONDARIO)}
          </div>
        </div>
      </SezioneModulo>

      <SezioneModulo
        titolo={t.universitario.titolo}
        descrizione={t.universitario.descrizione}
        etichetta={t.universitario.etichetta}
        rilievo="evidenziato"
        evidenziata
      >
        <CampoModulo per={`${id}-titolo`} etichetta={t.titolo} colonne={4}>
          <select
            id={`${id}-titolo`}
            name="universita_titolo_universitario"
            value={formData.universita_titolo_universitario}
            onChange={handleChange}
            className={campo("evidenziato")}
          >
            <option value="" data-segnaposto>{SEGNAPOSTI_SELEZIONE.titolo}</option>
            {t.titoliUniversitari.map(([valore, etichettaTitolo]) => (
              <option key={valore} value={valore}>{etichettaTitolo}</option>
            ))}
          </select>
        </CampoModulo>
        <CampoModulo per={`${id}-data-titolo`} etichetta={t.dataConseguimento} colonne={2}>
          <input
            id={`${id}-data-titolo`}
            type="date"
            name="universita_data_titolo"
            value={formData.universita_data_titolo}
            onChange={handleChange}
            className={campoDataEvidenziata()}
          />
        </CampoModulo>
        {testo("universita_materia_titolo", "corso", t.corso, 3)}
        {testo("universita_universita_titolo", "universita", t.universita, 3)}
        {voto("universita_votoRicevuto_titolo", "universita_votoMassimo_titolo", "voto-titolo")}
      </SezioneModulo>

      <SezioneModulo
        titolo={t.altri.titolo}
        descrizione={t.altri.descrizione}
        rilievo="secondario"
        griglia={false}
      >
        <div role="table" aria-label={t.altri.titolo} className={tabellaCampi()}>
          <div role="row" className={intestazioneCampi("compatta", "titoli", "tenue")}>
            <span role="columnheader">{t.titolo}</span>
            <span role="columnheader">{t.istituto}</span>
            <span role="columnheader">{t.data}</span>
          </div>
          {ALTRI_TITOLI.map((suffisso) => {
            const riga = t.righe[suffisso];
            const istituto = `universita_istituto_${suffisso}`;
            const data = `universita_data_${suffisso}`;
            return (
              <div key={suffisso} role="row" className={rigaCampi("compatta", "titoli")}>
                <span role="rowheader" className={stili.titoloRiga}>{riga}</span>
                <div role="cell">
                  <input
                    type="text"
                    name={istituto}
                    value={formData[istituto]}
                    onChange={handleChange}
                    aria-label={t.campoRiga(t.istituto, riga)}
                    className={campo("minimo")}
                  />
                </div>
                <div role="cell">
                  <input
                    type="date"
                    name={data}
                    value={formData[data]}
                    onChange={handleChange}
                    aria-label={t.campoRiga(t.data, riga)}
                    className={campo("minimo")}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </SezioneModulo>
    </div>
  );
}
