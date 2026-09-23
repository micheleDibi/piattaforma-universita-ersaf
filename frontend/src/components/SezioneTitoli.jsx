import { useId } from "react";
import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { TESTI_TITOLI } from "../config/testi/titoli.js";
import { campo, etichetta } from "../config/styles/campo";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import { riquadro } from "../config/styles/superficie";

// Gli anni del diploma e dell'anno integrativo sono varchar(45) nel database.
export default function SezioneTitoli({ formData, handleChange }) {
  const id = useId();
  return (
    <div>
      {/* SEZIONE 1: Istruzione Secondaria e Anno Integrativo */}
      <SezioneModulo titolo="Diploma di istruzione secondaria" descrizione="Requisito di accesso ai corsi universitari." griglia={false}>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          {/* Colonna Sinistra */}
          <div className="space-y-4">
            <div>
              <label className={etichetta()}>
                Diploma di istruzione secondaria
              </label>
              <input
                type="text"
                name="universita_diploma"
                value={formData.universita_diploma}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label htmlFor={`${id}-anno-diploma`} className={etichetta()}>
                Anno di conseguimento
              </label>
              <input
                id={`${id}-anno-diploma`}
                type="text"
                name="universita_anno_scolastico"
                value={formData.universita_anno_scolastico}
                onChange={handleChange}
                maxLength={45}
                placeholder={TESTI_TITOLI.segnapostoAnno}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                Istituto
              </label>
              <input
                type="text"
                name="universita_istituto"
                value={formData.universita_istituto}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                Indirizzo (via)
              </label>
              <input
                type="text"
                name="universita_via_istituto"
                value={formData.universita_via_istituto}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div className="col-span-2">
                <label className={etichetta()}>
                  Città
                </label>
                <input
                  type="text"
                  name="universita_citta_istituto"
                  value={formData.universita_citta_istituto}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
              <div>
                <label className={etichetta()}>
                  Prov.
                </label>
                <input
                  type="text"
                  name="universita_provincia_istituto"
                  value={formData.universita_provincia_istituto}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={etichetta()}>
                  Voto ricevuto
                </label>
                <input
                  type="number"
                  name="universita_votoRicevuto_diploma"
                  value={formData.universita_votoRicevuto_diploma}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
              <div>
                <label className={etichetta()}>
                  Voto massimo
                </label>
                <input
                  type="number"
                  name="universita_votoMassimo_diploma"
                  value={formData.universita_votoMassimo_diploma}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
          </div>

          {/* Colonna Destra (Anno Integrativo _ai) */}
          <div className="space-y-4">
            <div>
              <label className={etichetta()}>
                Anno integrativo presso
              </label>
              <input
                type="text"
                name="universita_istituto_ai"
                value={formData.universita_istituto_ai}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                Città
              </label>
              <input
                type="text"
                name="universita_citta_istituto_ai"
                value={formData.universita_citta_istituto_ai}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                Provincia
              </label>
              <input
                type="text"
                name="universita_provincia_istituto_ai"
                value={formData.universita_provincia_istituto_ai}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                Indirizzo (via)
              </label>
              <input
                type="text"
                name="universita_via_istituto_ai"
                value={formData.universita_via_istituto_ai}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label htmlFor={`${id}-anno-integrativo`} className={etichetta()}>
                Anno di conseguimento
              </label>
              <input
                id={`${id}-anno-integrativo`}
                type="text"
                name="universita_anno_scolastico_ai"
                value={formData.universita_anno_scolastico_ai}
                onChange={handleChange}
                maxLength={45}
                placeholder={TESTI_TITOLI.segnapostoAnno}
                className={campo()}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={etichetta()}>
                  Voto ricevuto
                </label>
                <input
                  type="number"
                  name="universita_votoRicevuto_ai"
                  value={formData.universita_votoRicevuto_ai}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
              <div>
                <label className={etichetta()}>
                  Voto massimo
                </label>
                <input
                  type="number"
                  name="universita_votoMassimo_ai"
                  value={formData.universita_votoMassimo_ai}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
          </div>
        </div>
      </SezioneModulo>

      {/* SEZIONE 2: Titolo Universitario */}
      <SezioneModulo titolo="Titolo universitario" descrizione="Titolo di studio più recente conseguito." griglia={false}>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          <div className="space-y-4">
            <div>
              <label className={etichetta()}>
                Titolo Universitario
              </label>
              <select
                name="universita_titolo_universitario"
                value={formData.universita_titolo_universitario}
                onChange={handleChange}
                className={campo()}
              >
                <option value="" data-segnaposto>{SEGNAPOSTI_SELEZIONE.titolo}</option>
                <option value="laurea_1_livello">
                  Laurea (Laurea 1° Livello)
                </option>
                <option value="laurea_magistrale">Laurea Magistrale</option>
                <option value="laurea_specialistica">
                  Laurea Specialistica
                </option>
                <option value="diploma_universitario">
                  Diploma Universitario
                </option>
                <option value="laurea_vecchio_ordinamento">
                  Laurea vecchio ordinamento
                </option>
              </select>
            </div>
            <div>
              <label className={etichetta()}>
                Corso di Laurea
              </label>
              <input
                type="text"
                name="universita_materia_titolo"
                value={formData.universita_materia_titolo}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                Università
              </label>
              <input
                type="text"
                name="universita_universita_titolo"
                value={formData.universita_universita_titolo}
                onChange={handleChange}
                className={campo()}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className={etichetta()}>
                Data di conseguimento
              </label>
              <div className="relative">
                <input
                  type="date"
                  name="universita_data_titolo"
                  value={formData.universita_data_titolo}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={etichetta()}>
                  Voto ricevuto
                </label>
                <input
                  type="number"
                  name="universita_votoRicevuto_titolo"
                  value={formData.universita_votoRicevuto_titolo}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
              <div>
                <label className={etichetta()}>
                  Voto massimo
                </label>
                <input
                  type="number"
                  name="universita_votoMassimo_titolo"
                  value={formData.universita_votoMassimo_titolo}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
          </div>
        </div>
      </SezioneModulo>

      {/* SEZIONE 3: Titoli post-laurea e Altri titoli di studio */}
      <SezioneModulo titolo="Altri titoli" descrizione="Post-laurea e titoli aggiuntivi, facoltativi." griglia={false}>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          {/* Colonna Sinistra: Post-laurea */}
          <div className="space-y-6">
            <div className={`${riquadro()} space-y-3`}>
              <span className="text-xs font-bold text-testo uppercase">
                Titolo post-laurea (1)
              </span>
              <div>
                <label className={etichetta()}>
                  Istituto
                </label>
                <input
                  type="text"
                  name="universita_istituto_pl1"
                  value={formData.universita_istituto_pl1}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
              <div>
                <label className={etichetta()}>
                  DATA
                </label>
                <input
                  type="date"
                  name="universita_data_pl1"
                  value={formData.universita_data_pl1}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>

            <div className={`${riquadro()} space-y-3`}>
              <span className="text-xs font-bold text-testo uppercase">
                Titolo post-laurea (2)
              </span>
              <div>
                <label className={etichetta()}>
                  Istituto
                </label>
                <input
                  type="text"
                  name="universita_istituto_pl2"
                  value={formData.universita_istituto_pl2}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
              <div>
                <label className={etichetta()}>
                  DATA
                </label>
                <input
                  type="date"
                  name="universita_data_pl2"
                  value={formData.universita_data_pl2}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
          </div>

          {/* Colonna Destra: Altri titoli */}
          <div className="space-y-6">
            <div className={`${riquadro()} space-y-3`}>
              <span className="text-xs font-bold text-testo uppercase">
                Altro titolo di studio (1)
              </span>
              <div>
                <label className={etichetta()}>
                  Istituto
                </label>
                <input
                  type="text"
                  name="universita_istituto_ats1"
                  value={formData.universita_istituto_ats1}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
              <div>
                <label className={etichetta()}>
                  DATA
                </label>
                <input
                  type="date"
                  name="universita_data_ats1"
                  value={formData.universita_data_ats1}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>

            <div className={`${riquadro()} space-y-3`}>
              <span className="text-xs font-bold text-testo uppercase">
                Altro titolo di studio (2)
              </span>
              <div>
                <label className={etichetta()}>
                  Istituto
                </label>
                <input
                  type="text"
                  name="universita_istituto_ats2"
                  value={formData.universita_istituto_ats2}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
              <div>
                <label className={etichetta()}>
                  DATA
                </label>
                <input
                  type="date"
                  name="universita_data_ats2"
                  value={formData.universita_data_ats2}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
          </div>
        </div>
      </SezioneModulo>
    </div>
  );
}
