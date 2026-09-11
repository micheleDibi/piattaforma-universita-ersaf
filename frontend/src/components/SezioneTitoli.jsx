import { campo, etichetta } from "../config/styles/campo";
import { riquadro, titoloSezione } from "../config/styles/superficie";

export default function SezioneTitoli({ formData, handleChange }) {
  return (
    <div className="space-y-10 text-testo">
      {/* SEZIONE 1: Istruzione Secondaria e Anno Integrativo */}
      <div>
        <h3 className={titoloSezione("separato")}>
          Istruzione Secondaria
        </h3>

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
              <label className={etichetta()}>
                Anno di conseguimento
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
              <label className={etichetta()}>
                Anno di conseguimento
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
      </div>

      {/* SEZIONE 2: Titolo Universitario */}
      <div>
        <h3 className={titoloSezione("separato")}>
          Titolo Universitario
        </h3>

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
                <option value="">Seleziona titolo</option>
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
      </div>

      {/* SEZIONE 3: Titoli post-laurea e Altri titoli di studio */}
      <div>
        <h3 className={titoloSezione("separato")}>
          Titoli Post-Laurea e Altri Titoli
        </h3>

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
      </div>
    </div>
  );
}
