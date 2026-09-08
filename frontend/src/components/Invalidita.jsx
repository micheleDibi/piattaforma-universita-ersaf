export default function Invalidita({ formData, handleChange }) {
  return (
    <div className="space-y-6 text-slate-700 max-w-2xl">
      <h3 className="text-base font-bold text-slate-800 mb-6 border-b pb-2">
        Dati Invalidità
      </h3>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
            Percentuale
          </label>
          <input
            type="text"
            name="universita_percentualeInvalidita"
            value={formData.universita_percentualeInvalidita || ""}
            onChange={handleChange}
            placeholder="Es. 75%"
            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
            Tipo di Invalidità
          </label>
          <input
            type="text"
            name="universita_tipoInvalidita"
            value={formData.universita_tipoInvalidita || ""}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>
      </div>
    </div>
  );
}
