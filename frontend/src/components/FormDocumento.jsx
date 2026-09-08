export default function FormDocumento({ formData, handleChange }) {
  return (
    <div className="space-y-4">
      <h3 className="text-base font-bold text-slate-800 mb-4">Documento</h3>

      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
          Tipo Documento
        </label>
        <select
          name="tipoDocumento"
          value={formData.tipoDocumento}
          onChange={handleChange}
          className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
        >
          <option value="">Seleziona il tipo di documento</option>
          <option value="Carta d'identità">Carta d'identità</option>
          <option value="Passaporto">Passaporto</option>
          <option value="Patente">Patente</option>
        </select>
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
          N° Documento
        </label>
        <input
          type="text"
          name="nDocumento"
          value={formData.nDocumento}
          onChange={handleChange}
          className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
          Comune di Rilascio
        </label>
        <input
          type="text"
          name="comuneDiRilascio"
          value={formData.comuneDiRilascio}
          onChange={handleChange}
          className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
            Data Rilascio
          </label>
          <input
            type="date"
            name="dataInizioRilascio"
            value={formData.dataInizioRilascio}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
            Data Scadenza
          </label>
          <input
            type="date"
            name="dataScadenza"
            value={formData.dataScadenza}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
          />
        </div>
      </div>
    </div>
  );
}
