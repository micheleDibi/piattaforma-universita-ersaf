import { daCasella, eVero } from "../lib/flagLegacy";
export default function ImmatricolazioniIscrizioni({ formData, handleChange }) {
  return (
    <div className="space-y-10 text-slate-700 max-w-4xl">
      {/* SEZIONE 1: Anagrafe Nazionale Studenti */}
      <div>
        <h3 className="text-base font-bold text-slate-800 mb-6 border-b pb-2">
          Anagrafe Nazionale Studenti
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          {/* Colonna Sinistra */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
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
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
              >
                <option value="">Seleziona status</option>
                <option value={0}>Non immatricolato</option>
                <option value={1}>Immatricolato</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
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
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Data di immatricolazione
              </label>
              <div className="relative">
                <input
                  type="date"
                  name="universita_data_immatricolazione"
                  value={formData.universita_data_immatricolazione || ""}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
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
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Università
              </label>
              <input
                type="text"
                name="universita_universitaConclusione"
                value={formData.universita_universitaConclusione || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Città
              </label>
              <input
                type="text"
                name="universita_cittaUniConclusione"
                value={formData.universita_cittaUniConclusione || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Provincia
              </label>
              <input
                type="text"
                name="universita_provinciaConclusione"
                value={formData.universita_provinciaConclusione || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
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
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  Data di conclusione
                </label>
                <div className="relative">
                  <input
                    type="date"
                    name="universita_data_conclusione"
                    value={formData.universita_data_conclusione || ""}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* SEZIONE 2: Attualmente iscritto al seguente corso */}
      <div>
        <h3 className="text-base font-bold text-slate-800 mb-6 border-b pb-2">
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
              className="w-4 h-4 text-blue-600 bg-slate-50 border-slate-300 rounded focus:ring-blue-500"
            />
            <label
              htmlFor="altroCorso"
              className="text-sm font-medium text-slate-700 cursor-pointer"
            >
              Iscritto ad altro corso di studi di altre Università
            </label>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Tipo
              </label>
              <select
                name="universita_attIscritto_tipo"
                value={formData.universita_attIscritto_tipo || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
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
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                In caso di 'Altro'
              </label>
              <input
                type="text"
                name="universita_attIscritto_altro"
                value={formData.universita_attIscritto_altro || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Classe di laurea
            </label>
            <input
              type="text"
              name="universita_attIscritto_classeLaurea"
              value={formData.universita_attIscritto_classeLaurea || ""}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Denominazione
            </label>
            <input
              type="text"
              name="universita_attIscritto_denominazione"
              value={formData.universita_attIscritto_denominazione || ""}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Università
            </label>
            <input
              type="text"
              name="universita_attIscritto_universita"
              value={formData.universita_attIscritto_universita || ""}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Anno di iscrizione
              </label>
              <input
                type="text"
                name="universita_attIscritto_annoIscrizione"
                value={formData.universita_attIscritto_annoIscrizione || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Modalità
              </label>
              <select
                name="universita_attIscritto_modalita"
                value={formData.universita_attIscritto_modalita || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
              >
                <option value="">Seleziona modalità</option>
                <option value="full_time">Full-Time</option>
                <option value="part_time">Part-Time</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Città
              </label>
              <input
                type="text"
                name="universita_attIscritto_citta"
                value={formData.universita_attIscritto_citta || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Provincia
              </label>
              <input
                type="text"
                name="universita_attIscritto_provincia"
                value={formData.universita_attIscritto_provincia || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
