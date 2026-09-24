import { useEffect, useState, useRef, useCallback } from "react";
import { apiFetch } from "../lib/api";
import { campo } from "../config/styles/campo";
import { pulsante, pulsanteIcona } from "../config/styles/pulsante";
import { X } from "../config/icone.js";
import Dialogo from "./shared/Dialogo.jsx";
import {
  cellaIntestazione,
  intestazioneTabella,
  rigaTabella,
  statoVuoto,
} from "../config/styles/tabella";

export default function ModalCambiaPadre({ isOpen, onClose, onSelectPadre }) {
  const [attuatori, setAttuatori] = useState([]);
  const [loadingAttuatori, setLoadingAttuatori] = useState(false);
  const [searchTermAttuatore, setSearchTermAttuatore] = useState("");
  const [selectedRuoloAttuatore, setSelectedRuoloAttuatore] = useState("");
  const [skip, setSkip] = useState(0);
  const [haAltri, setHaAltri] = useState(false);
  const scrollRef = useRef(null);
  const LIMITE = 50;

  // Tracciamo l'ultimo stato di `isOpen` per resettare i filtri durante il render se il modale si apre
  const [prevIsOpen, setPrevIsOpen] = useState(isOpen);
  if (isOpen && !prevIsOpen) {
    setSearchTermAttuatore("");
    setSelectedRuoloAttuatore("");
  }
  if (isOpen !== prevIsOpen) {
    setPrevIsOpen(isOpen);
  }

  const fetchAttuatori = useCallback(
    async (search = "", ruolo = "", skipCorrente = 0, append = false) => {
      setLoadingAttuatori(true);
      try {
        const ruoloParam = ruolo
          ? `&ruolo_codice=${encodeURIComponent(ruolo)}`
          : "";
        const response = await apiFetch(
          `/clienti/?skip=${skipCorrente}&limit=${LIMITE}&solo_attuatori=true${ruoloParam}&search=${encodeURIComponent(search)}`,
        );
        if (!response.ok)
          throw new Error("Errore nel recupero degli attuatori");
        const data = await response.json();
        setAttuatori((prev) => (append ? [...prev, ...data] : data));
        setHaAltri(data.length === LIMITE);
        setSkip(skipCorrente);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingAttuatori(false);
      }
    },
    [],
  );

  // Debounce effect per la ricerca fluida e fetch iniziale all'apertura
  useEffect(() => {
    if (!isOpen) return;

    const delayDebounceFn = setTimeout(() => {
      fetchAttuatori(searchTermAttuatore, selectedRuoloAttuatore, 0, false);
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTermAttuatore, selectedRuoloAttuatore, isOpen, fetchAttuatori]);

  // Scroll infinito: quando ci si avvicina al fondo della tabella, carica
  // altri 50 risultati mantenendo filtro e ricerca correnti.
  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el || loadingAttuatori || !haAltri) return;
    const vicinoAlFondo =
      el.scrollTop + el.clientHeight >= el.scrollHeight - 80;
    if (vicinoAlFondo) {
      fetchAttuatori(
        searchTermAttuatore,
        selectedRuoloAttuatore,
        skip + LIMITE,
        true,
      );
    }
  };

  return (
    <Dialogo
      aperto={isOpen}
      onChiudi={onClose}
      etichetta="Seleziona Nuovo Utente Padre"
    >
      <div className="dialogo__contenuto">
        <div className="mb-4 flex items-center justify-between border-b border-divisore pb-2.5">
          <h3 className="text-lg font-semibold text-testo">
            Seleziona Nuovo Utente Padre
          </h3>
          <button
            type="button"
            onClick={onClose}
            className={pulsanteIcona()}
            aria-label="Chiudi selezione utente padre"
            title="Chiudi"
          >
            <X aria-hidden="true" className="size-icona" />
          </button>
        </div>

        <div className="mb-4 flex gap-3">
          <input
            type="text"
            placeholder="Cerca per nome, cognome o azienda..."
            value={searchTermAttuatore}
            onChange={(e) => setSearchTermAttuatore(e.target.value)}
            className={campo("comodo")}
            data-focus-iniziale
          />
          <select
            value={selectedRuoloAttuatore}
            onChange={(e) => setSelectedRuoloAttuatore(e.target.value)}
            className={`${campo("comodo")} w-auto!`}
          >
            <option value="" data-senza-filtro>
              Tutti i ruoli
            </option>
            <option value="Aderente">Aderente</option>
            <option value="Provinciale">Provinciale</option>
            <option value="Regionale">Regionale</option>
            <option value="Nazionale">Nazionale</option>
          </select>
        </div>

        <div
          ref={scrollRef}
          onScroll={handleScroll}
          className="h-[350px] overflow-y-auto rounded-riquadro border border-bordo bg-superficie"
        >
          <table className="w-full border-collapse text-left text-sm">
            <thead className={`${intestazioneTabella()} sticky top-0 z-10`}>
              <tr>
                <th className={cellaIntestazione()}>Nome</th>
                <th className={cellaIntestazione()}>Cognome</th>
                <th className={cellaIntestazione()}>Ruolo</th>
                <th className={cellaIntestazione()}>Azienda</th>
                <th className={cellaIntestazione()}>Azione</th>
              </tr>
            </thead>
            <tbody>
              {attuatori.map((att) => (
                <tr key={att.cliente_id} className={rigaTabella()}>
                  <td className="px-4 py-2.5 text-testo">{att.cliente_nome}</td>
                  <td className="px-4 py-2.5 text-testo">{att.cliente_cognome}</td>
                  <td className="px-4 py-2.5 text-testo">
                    {att.ruolo?.ruolo_codice || "-"}
                  </td>
                  <td className="px-4 py-2.5 text-testo">
                    {att.azienda?.azienda_ragione_sociale || "-"}
                  </td>
                  <td className="px-4 py-2.5">
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
                  <td colSpan="5" className={statoVuoto()}>
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
    </Dialogo>
  );
}
