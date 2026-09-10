export default function ProdottoDettagliTabella({
  dettagli,
  handleDettaglioChange,
  handleAggiungiRiga,
  handleRimuoviRiga,
}) {
  return (
    <div className="pt-6 border-t border-slate-200">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-md font-bold text-slate-700">Dettaglio prodotto</h3>
        <button
          type="button"
          onClick={handleAggiungiRiga}
          className="bg-slate-800 hover:bg-slate-900 text-white text-xs font-medium px-3 py-2 rounded-lg transition-colors shadow-sm cursor-pointer"
        >
          + Aggiungi nuova riga
        </button>
      </div>

      <div className="overflow-x-auto border border-slate-200 rounded-lg">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-100 text-xs uppercase text-slate-700 border-b border-slate-200">
            <tr>
              <th className="p-2.5">Inizio Validità</th>
              <th className="p-2.5">Fine Validità</th>
              <th className="p-2.5">Prezzo (€)</th>
              <th className="p-2.5">Durata (mesi)</th>
              <th className="p-2.5">CFU</th>
              <th className="p-2.5">Tasse (€)</th>
              <th className="p-2.5 text-center">Azioni</th>
            </tr>
          </thead>
          <tbody>
            {dettagli.map((det, index) => (
              <tr
                key={index}
                className="border-b border-slate-200 hover:bg-slate-50"
              >
                <td className="p-2">
                  <input
                    type="date"
                    name="listDettaglio_dataInizioValidazione"
                    value={det.listDettaglio_dataInizioValidazione ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </td>
                <td className="p-2">
                  <input
                    type="date"
                    name="listDettaglio_dataFineValidazione"
                    value={det.listDettaglio_dataFineValidazione ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </td>
                <td className="p-2">
                  <input
                    type="number"
                    step="0.01"
                    name="listDettaglio_prezzo"
                    placeholder="0.00"
                    value={det.listDettaglio_prezzo ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </td>
                <td className="p-2">
                  <input
                    type="number"
                    name="listDettaglio_durata"
                    placeholder="Mesi"
                    value={det.listDettaglio_durata ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </td>
                <td className="p-2">
                  <input
                    type="number"
                    name="listDettaglio_CFU"
                    placeholder="CFU"
                    value={det.listDettaglio_CFU ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </td>
                <td className="p-2">
                  <input
                    type="number"
                    step="0.01"
                    name="listDettaglio_tasse"
                    placeholder="Tasse"
                    value={det.listDettaglio_tasse ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </td>
                <td className="p-2 text-center">
                  {dettagli.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRimuoviRiga(index)}
                      className="text-rose-600 hover:text-rose-800 font-bold px-2 py-1 text-xs cursor-pointer"
                      title="Rimuovi riga"
                    >
                      ✕
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
