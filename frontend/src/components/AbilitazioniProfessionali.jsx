import { eVero } from "../lib/flagLegacy";
import { campo, etichetta, spunta } from "../config/styles/campo";
import { titoloSezione } from "../config/styles/superficie";
export default function AbilitazioniProfessionali({ formData, handleChange }) {
  return (
    <div className="space-y-10 text-testo max-w-4xl">
      {/* SEZIONE 1: Abilitazione Professionale */}
      <div>
        <h3 className={titoloSezione("separato")}>
          Abilitazione Professionale
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          <div className="space-y-4">
            <div>
              <label className={etichetta()}>
                Abilitazione Professionale
              </label>
              <input
                type="text"
                name="universita_professione"
                value={formData.universita_professione || ""}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                DATA
              </label>
              <div className="relative">
                <input
                  type="date"
                  name="universita_data_professione"
                  value={formData.universita_data_professione || ""}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
            <div>
              <label className={etichetta()}>
                Luogo
              </label>
              <input
                type="text"
                name="universita_luogo_professione"
                value={formData.universita_luogo_professione || ""}
                onChange={handleChange}
                className={campo()}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className={etichetta()}>
                Qualifica Professionale
              </label>
              <input
                type="text"
                name="universita_qualifica_professionale"
                value={formData.universita_qualifica_professionale || ""}
                onChange={handleChange}
                className={campo()}
              />
            </div>
            <div>
              <label className={etichetta()}>
                DATA
              </label>
              <div className="relative">
                <input
                  type="date"
                  name="universita_data_qualifica"
                  value={formData.universita_data_qualifica || ""}
                  onChange={handleChange}
                  className={campo()}
                />
              </div>
            </div>
            <div>
              <label className={etichetta()}>
                Luogo
              </label>
              <input
                type="text"
                name="universita_luogo"
                value={formData.universita_luogo || ""}
                onChange={handleChange}
                className={campo()}
              />
            </div>
          </div>
        </div>
      </div>

      {/* SEZIONE 2: Albo o Elenco */}
      <div>
        <h3 className={titoloSezione("separato")}>
          Albo o Elenco
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          <div>
            <label className={etichetta()}>
              Albo / Elenco
            </label>
            <input
              type="text"
              name="universita_albo"
              value={formData.universita_albo || ""}
              onChange={handleChange}
              className={campo()}
            />
          </div>
          <div>
            <label className={etichetta()}>
              Forze dell'Ordine
            </label>
            <input
              type="text"
              name="universita_forzeDellOrdine"
              value={formData.universita_forzeDellOrdine || ""}
              onChange={handleChange}
              className={campo()}
            />
          </div>
        </div>
      </div>

      {/* SEZIONE 3: Richiesta di convalida delle esperienze */}
      <div>
        <h3 className={titoloSezione("separato")}>
          Richiesta di convalida delle esperienze
        </h3>

        <div className="space-y-4 max-w-xl">
          {/* Attività Professionalizzanti */}
          <div className="flex items-center justify-between p-3 bg-superficie-tenue/50 rounded-superficie border border-bordo">
            <span className="text-sm font-medium text-testo">
              Attività Professionalizzanti
            </span>
            <input
              type="checkbox"
              name="universita_attivita_professionalizzanti"
              checked={eVero(formData.universita_attivita_professionalizzanti)}
              onChange={handleChange}
              className={spunta()}
            />
          </div>

          {/* Corsi di Formazione */}
          <div className="flex items-center justify-between p-3 bg-superficie-tenue/50 rounded-superficie border border-bordo">
            <span className="text-sm font-medium text-testo">
              Corsi di Formazione
            </span>
            <input
              type="checkbox"
              name="universita_corsi_di_formazione"
              checked={eVero(formData.universita_corsi_di_formazione)}
              onChange={handleChange}
              className={spunta()}
            />
          </div>

          {/* Altre Attività Certificate */}
          <div className="flex items-center justify-between p-3 bg-superficie-tenue/50 rounded-superficie border border-bordo">
            <span className="text-sm font-medium text-testo">
              Altre Attività Certificate
            </span>
            <input
              type="checkbox"
              name="universita_altre_attivita_certificate"
              checked={eVero(formData.universita_altre_attivita_certificate)}
              onChange={handleChange}
              className={spunta()}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
