import { useEffect, useState } from "react";

export default function ModalCambiaPadre({ isOpen, onClose, onSelectPadre }) {
  const [attuatori, setAttuatori] = useState([]);
  const [loadingAttuatori, setLoadingAttuatori] = useState(false);
  const [searchTermAttuatore, setSearchTermAttuatore] = useState("");
  const [selectedRuoloAttuatore, setSelectedRuoloAttuatore] = useState("");

  // Tracciamo l'ultimo stato di `isOpen` per resettare i filtri durante il render se il modale si apre
  const [prevIsOpen, setPrevIsOpen] = useState(isOpen);
  if (isOpen && !prevIsOpen) {
    setSearchTermAttuatore("");
    setSelectedRuoloAttuatore("");
  }
  if (isOpen !== prevIsOpen) {
    setPrevIsOpen(isOpen);
  }

  const fetchAttuatori = async (search = "", ruolo = "") => {
    setLoadingAttuatori(true);
    const token = localStorage.getItem("sessione_token");
    const headers = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    try {
      const ruoloParam = ruolo
        ? `&ruolo_codice=${encodeURIComponent(ruolo)}`
        : "";
      const response = await fetch(
        `http://localhost:8000/clienti/?skip=0&limit=50&solo_attuatori=true${ruoloParam}&search=${encodeURIComponent(search)}`,
        { headers },
      );
      if (!response.ok) throw new Error("Errore nel recupero degli attuatori");
      const data = await response.json();
      setAttuatori(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingAttuatori(false);
    }
  };

  // Debounce effect per la ricerca fluida e fetch iniziale all'apertura
  useEffect(() => {
    if (!isOpen) return;

    const delayDebounceFn = setTimeout(() => {
      fetchAttuatori(searchTermAttuatore, selectedRuoloAttuatore);
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTermAttuatore, selectedRuoloAttuatore, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="flex max-h-[85vh] w-[90%] max-w-[800px] flex-col rounded-xl bg-white p-6 shadow-2xl">
        <div className="mb-4 flex items-center justify-between border-b border-slate-200 pb-2.5">
          <h3 className="text-lg font-semibold text-slate-800">
            Seleziona Nuovo Utente Padre
          </h3>
          <button
            onClick={onClose}
            className="cursor-pointer text-2xl text-slate-500 hover:text-slate-800"
          >
            &times;
          </button>
        </div>

        <div className="mb-4 flex gap-3">
          <input
            type="text"
            placeholder="Cerca per nome, cognome o azienda..."
            value={searchTermAttuatore}
            onChange={(e) => setSearchTermAttuatore(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-3 text-sm text-slate-900 outline-none focus:border-blue-500"
            autoFocus
          />
          <select
            value={selectedRuoloAttuatore}
            onChange={(e) => setSelectedRuoloAttuatore(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3.5 py-3 text-sm text-slate-900 outline-none focus:border-blue-500"
          >
            <option value="">Tutti i ruoli</option>
            <option value="Aderente">Aderente</option>
            <option value="Provinciale">Provinciale</option>
            <option value="Regionale">Regionale</option>
            <option value="Nazionale">Nazionale</option>
          </select>
        </div>

        <div className="h-[350px] overflow-y-auto rounded-lg border border-slate-200 bg-white">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="sticky top-0 z-10 border-b border-slate-200 bg-slate-50">
                <th className="p-3 text-xs font-semibold text-slate-600">
                  Nome
                </th>
                <th className="p-3 text-xs font-semibold text-slate-600">
                  Cognome
                </th>
                <th className="p-3 text-xs font-semibold text-slate-600">
                  Ruolo
                </th>
                <th className="p-3 text-xs font-semibold text-slate-600">
                  Azienda
                </th>
                <th className="p-3 text-xs font-semibold text-slate-600">
                  Azione
                </th>
              </tr>
            </thead>
            <tbody>
              {attuatori.map((att) => (
                <tr
                  key={att.cliente_id}
                  className="border-b border-slate-200 hover:bg-slate-50/50"
                >
                  <td className="p-3 text-slate-800">{att.cliente_nome}</td>
                  <td className="p-3 text-slate-800">{att.cliente_cognome}</td>
                  <td className="p-3 text-slate-800">
                    {att.ruolo?.ruolo_codice || "-"}
                  </td>
                  <td className="p-3 text-slate-800">
                    {att.azienda?.azienda_ragione_sociale || "-"}
                  </td>
                  <td className="p-3">
                    <button
                      type="button"
                      onClick={() => onSelectPadre(att)}
                      className="cursor-pointer rounded-md bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700"
                    >
                      Seleziona
                    </button>
                  </td>
                </tr>
              ))}
              {attuatori.length === 0 && !loadingAttuatori && (
                <tr>
                  <td
                    colSpan="5"
                    className="p-[30px] text-center text-slate-500"
                  >
                    Nessun attuatore trovato.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loadingAttuatori && (
          <div className="mt-2 text-center text-xs text-slate-500">
            Aggiornamento in corso...
          </div>
        )}
      </div>
    </div>
  );
}
