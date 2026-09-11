import { daCasella, eVero } from "../lib/flagLegacy";
import { campo, etichetta, spunta } from "../config/styles/campo";
import { titoloSezione } from "../config/styles/superficie";
export default function ImmatricolazioniIscrizioni({ formData, handleChange }) {
  return (
    <div className="space-y-10 text-testo max-w-4xl">
      {/* SEZIONE 1: Anagrafe Nazionale Studenti */}
      <div>
        <h3 className={titoloSezione("separato")}>
          Anagrafe Nazionale Studenti
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          {/* Colonna Sinistra */}
          <div className="space-y-4">
            <div>
              <label className={etichetta()}>
                Status Accademico Attuale
              </label>
              <select
                name="universita_immatricolato"
                value={
                  formData.universita_immatricolato !== undefined
                    ? formData.universita_immatricolato
                    : ""
                }
                onChange={handleChange}
                className={campo()}
              >
                <option value="">Seleziona status</option>
                <option value={0}>Non immatricolato</option>
                <option value={1}>Immatricolato</option>
              </select>
            </div>
            <div>
              <label className={etichetta()}>
                Tipo di Corso
              </label>
              <select
                name="universita_riforma"
                value={formData.universita_riforma || ""}
                onChange={handleChange}
              >
                <option value="">Seleziona tipo corso</option>
                <option value="pre_riforma_dm_509_99">
                  PRE riforma D.M. 509/99
                </option>
                <option value="post_riforma_dm_509_99">
                  POST riforma D.M. 509/99
                </option>
              </select>
            </div>
            <div>
              <label className={etichetta()}>
                Data di immatricolazione
              </label>
              <div className="relative">
                <input
                  type="date"
                  name="universita_data_immatricolazione"
                  value={formData.universita_data_immatricolazione || ""}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
            <div>
              <label className={etichetta()}>
                Ateneo di iscrizione
              </label>
              <input
                type="text"
                name="universita_ateneoNullaosta"
                value={formData.universita_ateneoNullaosta || ""}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* Colonna Destra */}
          <div className="space-y-4">
            <div>
              <label className={etichetta()}>
                Università
              </label>
              <input
                type="text"
                name="universita_universitaConclusione"
                value={formData.universita_universitaConclusione || ""}
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
                name="universita_cittaUniConclusione"
                value={formData.universita_cittaUniConclusione || ""}
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
                name="universita_provinciaConclusione"
                value={formData.universita_provinciaConclusione || ""}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={etichetta()}>
                  Conclusione carriera con
                </label>
                <select
                  name="universita_conclusione"
                  value={formData.universita_conclusione || ""}
                  onChange={handleChange}
                >
                  <option value="">Seleziona</option>
                  <option value="conseguimento_titolo_finale">
                    conseguimento titolo finale
                  </option>
                  <option value="rinuncia">rinuncia</option>
                  <option value="decadenza">decadenza</option>
                  <option value="trasferimento">Trasferimento</option>
                </select>
              </div>
              <div>
                <label className={etichetta()}>
                  Data di conclusione
                </label>
                <div className="relative">
                  <input
                    type="date"
                    name="universita_data_conclusione"
                    value={formData.universita_data_conclusione || ""}
                    onChange={handleChange}
                    className={campo()}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* SEZIONE 2: Attualmente iscritto al seguente corso */}
      <div>
        <h3 className={titoloSezione("separato")}>
          ATTUALMENTE iscritto al seguente corso:
        </h3>

        <div className="space-y-4 max-w-2xl">
          {/* Checkbox personalizzata */}
          <div className="flex items-center space-x-3 py-2">
            <input
              type="checkbox"
              id="altroCorso"
              name="universita_iscrizioneAltraUniversita"
              checked={eVero(formData.universita_iscrizioneAltraUniversita)}
              onChange={(e) => {
                // Gestione personalizzata per inviare -1 o 0 a seconda dello stato della checkbox
                const syntheticEvent = {
                  target: {
                    name: "universita_iscrizioneAltraUniversita",
                    value: daCasella(e.target.checked),
                    type: "number",
                  },
                };
                handleChange(syntheticEvent);
              }}
              className={`${spunta()} bg-superficie-tenue`}
            />
            <label
              htmlFor="altroCorso"
              className="text-sm font-medium text-testo cursor-pointer"
            >
              Iscritto ad altro corso di studi di altre Università
            </label>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={etichetta()}>
                Tipo
              </label>
              <select
                name="universita_attIscritto_tipo"
                value={formData.universita_attIscritto_tipo || ""}
                onChange={handleChange}
                className={campo()}
              >
                <option value="">Seleziona tipo</option>
                <option value="laurea_i_livello">Laurea I Livello</option>
                <option value="laurea_ii_livello">Laurea II Livello</option>
                <option value="laurea_ciclo_unico">Laurea Ciclo Unico</option>
                <option value="master_i_livello">Master I Livello</option>
                <option value="master_ii_livello">Master II Livello</option>
                <option value="altro">Altro</option>
              </select>
            </div>
            <div>
              <label className={etichetta()}>
                In caso di 'Altro'
              </label>
              <input
                type="text"
                name="universita_attIscritto_altro"
                value={formData.universita_attIscritto_altro || ""}
                onChange={handleChange}
                className={campo()}
              />
            </div>
          </div>

          <div>
            <label className={etichetta()}>
              Classe di laurea
            </label>
            <input
              type="text"
              name="universita_attIscritto_classeLaurea"
              value={formData.universita_attIscritto_classeLaurea || ""}
              onChange={handleChange}
              className={campo()}
            />
          </div>

          <div>
            <label className={etichetta()}>
              Denominazione
            </label>
            <input
              type="text"
              name="universita_attIscritto_denominazione"
              value={formData.universita_attIscritto_denominazione || ""}
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
              name="universita_attIscritto_universita"
              value={formData.universita_attIscritto_universita || ""}
              onChange={handleChange}
              className={campo()}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={etichetta()}>
                Anno di iscrizione
              </label>
              <input
                type="text"
                name="universita_attIscritto_annoIscrizione"
                value={formData.universita_attIscritto_annoIscrizione || ""}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                Modalità
              </label>
              <select
                name="universita_attIscritto_modalita"
                value={formData.universita_attIscritto_modalita || ""}
                onChange={handleChange}
                className={campo()}
              >
                <option value="">Seleziona modalità</option>
                <option value="full_time">Full-Time</option>
                <option value="part_time">Part-Time</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2">
              <label className={etichetta()}>
                Città
              </label>
              <input
                type="text"
                name="universita_attIscritto_citta"
                value={formData.universita_attIscritto_citta || ""}
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
                name="universita_attIscritto_provincia"
                value={formData.universita_attIscritto_provincia || ""}
                onChange={handleChange}
                className={campo()}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
