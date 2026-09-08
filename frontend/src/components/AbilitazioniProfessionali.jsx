export default function AbilitazioniProfessionali({ formData, handleChange }) {
  return (
    <div className="space-y-10 text-slate-700 max-w-4xl">
      {/* SEZIONE 1: Abilitazione Professionale */}
      <div>
        <h3 className="text-base font-bold text-slate-800 mb-6 border-b pb-2">
          Abilitazione Professionale
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Abilitazione Professionale
              </label>
              <input
                type="text"
                name="universita_professione"
                value={formData.universita_professione || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                DATA
              </label>
              <div className="relative">
                <input
                  type="date"
                  name="universita_data_professione"
                  value={formData.universita_data_professione || ""}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Luogo
              </label>
              <input
                type="text"
                name="universita_luogo_professione"
                value={formData.universita_luogo_professione || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Qualifica Professionale
              </label>
              <input
                type="text"
                name="universita_qualifica_professionale"
                value={formData.universita_qualifica_professionale || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                DATA
              </label>
              <div className="relative">
                <input
                  type="date"
                  name="universita_data_qualifica"
                  value={formData.universita_data_qualifica || ""}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-700"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Luogo
              </label>
              <input
                type="text"
                name="universita_luogo"
                value={formData.universita_luogo || ""}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* SEZIONE 2: Albo o Elenco */}
      <div>
        <h3 className="text-base font-bold text-slate-800 mb-6 border-b pb-2">
          Albo o Elenco
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Albo / Elenco
            </label>
            <input
              type="text"
              name="universita_albo"
              value={formData.universita_albo || ""}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Forze dell'Ordine
            </label>
            <input
              type="text"
              name="universita_forzeDellOrdine"
              value={formData.universita_forzeDellOrdine || ""}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* SEZIONE 3: Richiesta di convalida delle esperienze */}
      <div>
        <h3 className="text-base font-bold text-slate-800 mb-6 border-b pb-2">
          Richiesta di convalida delle esperienze
        </h3>

        <div className="space-y-4 max-w-xl">
          {/* Attività Professionalizzanti */}
          <div className="flex items-center justify-between p-3 bg-slate-50/50 rounded-xl border border-slate-100">
            <span className="text-sm font-medium text-slate-700">
              Attività Professionalizzanti
            </span>
            <input
              type="checkbox"
              name="universita_attivita_professionalizzanti"
              checked={
                Number(formData.universita_attivita_professionalizzanti) === 1
              }
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 bg-slate-50 border-slate-300 rounded focus:ring-blue-500"
            />
          </div>

          {/* Corsi di Formazione */}
          <div className="flex items-center justify-between p-3 bg-slate-50/50 rounded-xl border border-slate-100">
            <span className="text-sm font-medium text-slate-700">
              Corsi di Formazione
            </span>
            <input
              type="checkbox"
              name="universita_corsi_di_formazione"
              checked={Number(formData.universita_corsi_di_formazione) === 1}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 bg-slate-50 border-slate-300 rounded focus:ring-blue-500"
            />
          </div>

          {/* Altre Attività Certificate */}
          <div className="flex items-center justify-between p-3 bg-slate-50/50 rounded-xl border border-slate-100">
            <span className="text-sm font-medium text-slate-700">
              Altre Attività Certificate
            </span>
            <input
              type="checkbox"
              name="universita_altre_attivita_certificate"
              checked={
                Number(formData.universita_altre_attivita_certificate) === 1
              }
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 bg-slate-50 border-slate-300 rounded focus:ring-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
