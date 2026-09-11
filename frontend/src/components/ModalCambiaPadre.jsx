import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { intestazioneTabella, rigaTabella, velo } from "../config/styles/superficie";

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
    try {
      const ruoloParam = ruolo
        ? `&ruolo_codice=${encodeURIComponent(ruolo)}`
        : "";
      // Passa da apiFetch: l'indirizzo del backend era scritto a mano e il
      // token letto da localStorage direttamente. Al primo deploy questa
      // finestra avrebbe continuato a chiamare localhost.
      const response = await apiFetch(
        `/clienti/?skip=0&limit=50&solo_attuatori=true${ruoloParam}&search=${encodeURIComponent(search)}`,
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
    <div className={velo()}>
      <div className="flex max-h-[85vh] w-[90%] max-w-[800px] flex-col rounded-superficie bg-superficie p-6 shadow-2xl">
        <div className="mb-4 flex items-center justify-between border-b border-bordo pb-2.5">
          <h3 className="text-lg font-semibold text-testo">
            Seleziona Nuovo Utente Padre
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="cursor-pointer text-2xl text-testo-tenue hover:text-testo"
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
            className={campo("comodo")}
            autoFocus
          />
          <select
            value={selectedRuoloAttuatore}
            onChange={(e) => setSelectedRuoloAttuatore(e.target.value)}
            className={`${campo("comodo")} w-auto!`}
          >
            <option value="">Tutti i ruoli</option>
            <option value="Aderente">Aderente</option>
            <option value="Provinciale">Provinciale</option>
            <option value="Regionale">Regionale</option>
            <option value="Nazionale">Nazionale</option>
          </select>
        </div>

        <div className="h-[350px] overflow-y-auto rounded-superficie border border-bordo bg-superficie">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr
                className={`${intestazioneTabella()} sticky top-0 z-10 border-b border-bordo`}
              >
                <th className="p-3 font-semibold">
                  Nome
                </th>
                <th className="p-3 font-semibold">
                  Cognome
                </th>
                <th className="p-3 font-semibold">
                  Ruolo
                </th>
                <th className="p-3 font-semibold">
                  Azienda
                </th>
                <th className="p-3 font-semibold">
                  Azione
                </th>
              </tr>
            </thead>
            <tbody>
              {attuatori.map((att) => (
                <tr
                  key={att.cliente_id}
                  className={rigaTabella()}
                >
                  <td className="p-3 text-testo">{att.cliente_nome}</td>
                  <td className="p-3 text-testo">{att.cliente_cognome}</td>
                  <td className="p-3 text-testo">
                    {att.ruolo?.ruolo_codice || "-"}
                  </td>
                  <td className="p-3 text-testo">
                    {att.azienda?.azienda_ragione_sociale || "-"}
                  </td>
                  <td className="p-3">
                    <button
                      type="button"
                      onClick={() => onSelectPadre(att)}
                      className={pulsante("primario", "piccolo")}
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
                    className="p-[30px] text-center text-testo-tenue"
                  >
                    Nessun attuatore trovato.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loadingAttuatori && (
          <div className="mt-2 text-center text-nota text-testo-tenue">
            Aggiornamento in corso...
          </div>
        )}
      </div>
    </div>
  );
}
