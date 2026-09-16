import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { campo } from "../config/styles/campo";
import { pulsante, pulsanteIcona } from "../config/styles/pulsante";
import { X } from "../config/icone.js";
import Dialogo from "./shared/Dialogo.jsx";
import { intestazioneTabella, rigaTabella } from "../config/styles/tabella";

export default function ModalCambiaPadreAzienda({
  isOpen,
  onClose,
  onSelectPadre,
  aziendaIdEsclusa,
}) {
  const [aziende, setAziende] = useState([]);
  const [loadingAziende, setLoadingAziende] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  // Stesso trucco di ModalCambiaPadre: reset dei filtri durante il render
  // quando il modale passa da chiuso ad aperto, senza un useEffect in piu'.
  const [prevIsOpen, setPrevIsOpen] = useState(isOpen);
  if (isOpen && !prevIsOpen) {
    setSearchTerm("");
  }
  if (isOpen !== prevIsOpen) {
    setPrevIsOpen(isOpen);
  }

  const fetchAziende = async (search = "") => {
    setLoadingAziende(true);
    try {
      const response = await apiFetch(
        `/aziende/?skip=0&limit=50&search=${encodeURIComponent(search)}`,
      );
      if (!response.ok) throw new Error("Errore nel recupero delle aziende");
      const data = await response.json();
      // L'azienda che si sta modificando non puo' essere padre di se stessa:
      // la si toglie qui invece che nel backend, dove arriverebbe comunque
      // rifiutata con un 400, ma non ha senso mostrarla come opzione.
      setAziende(data.filter((a) => a.azienda_id !== aziendaIdEsclusa));
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingAziende(false);
    }
  };

  useEffect(() => {
    if (!isOpen) return;

    const delayDebounceFn = setTimeout(() => {
      fetchAziende(searchTerm);
    }, 300);

    return () => clearTimeout(delayDebounceFn);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, isOpen]);

  return (
    <Dialogo
      aperto={isOpen}
      onChiudi={onClose}
      etichetta="Seleziona Nuova Azienda Padre"
    >
      <div className="dialogo__contenuto">
        <div className="mb-4 flex items-center justify-between border-b border-bordo pb-2.5">
          <h3 className="text-lg font-semibold text-testo">
            Seleziona Nuova Azienda Padre
          </h3>
          <button
            type="button"
            onClick={onClose}
            className={pulsanteIcona()}
            aria-label="Chiudi selezione azienda padre"
            title="Chiudi"
          >
            <X aria-hidden="true" className="size-icona" />
          </button>
        </div>

        <div className="mb-4 flex gap-3">
          <input
            type="text"
            placeholder="Cerca per ragione sociale..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={campo("comodo")}
            data-focus-iniziale
          />
          <button
            type="button"
            onClick={() => onSelectPadre(null)}
            className={`${pulsante("discreto", "comodo")} whitespace-nowrap`}
          >
            Rendi radice (nessun padre)
          </button>
        </div>

        <div className="h-[350px] overflow-y-auto rounded-superficie border border-bordo bg-superficie">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr
                className={`${intestazioneTabella()} sticky top-0 z-10 border-b border-bordo`}
              >
                <th className="p-3 font-semibold">Ragione sociale</th>
                <th className="p-3 font-semibold">Partita IVA</th>
                <th className="p-3 font-semibold">Città</th>
                <th className="p-3 font-semibold">Azione</th>
              </tr>
            </thead>
            <tbody>
              {aziende.map((az) => (
                <tr key={az.azienda_id} className={rigaTabella()}>
                  <td className="p-3 text-testo">
                    {az.azienda_ragione_sociale}
                  </td>
                  <td className="p-3 text-testo">{az.azienda_partitaIVA}</td>
                  <td className="p-3 text-testo">{az.azienda_citta}</td>
                  <td className="p-3">
                    <button
                      type="button"
                      onClick={() => onSelectPadre(az)}
                      className={pulsante("primario", "piccolo")}
                    >
                      Seleziona
                    </button>
                  </td>
                </tr>
              ))}
              {aziende.length === 0 && !loadingAziende && (
                <tr>
                  <td
                    colSpan="4"
                    className="p-[30px] text-center text-testo-tenue"
                  >
                    Nessuna azienda trovata.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loadingAziende && (
          <div className="mt-2 text-center text-nota text-testo-tenue">
            Aggiornamento in corso...
          </div>
        )}
      </div>
    </Dialogo>
  );
}
