import { useEffect, useState } from "react";
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
import { STILI_AZIENDA as stili } from "../config/styles/azienda.js";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";

const TESTI = TESTI_AZIENDA.finestraPadre;

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
      if (!response.ok) throw new Error(TESTI.erroreRecupero);
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
    <Dialogo aperto={isOpen} onChiudi={onClose} etichetta={TESTI.titolo}>
      <div className="dialogo__contenuto">
        <div className={stili.intestazioneFinestra}>
          <h3 className={stili.titoloFinestra}>{TESTI.titolo}</h3>
          <button
            type="button"
            onClick={onClose}
            className={pulsanteIcona()}
            aria-label={TESTI.chiudi}
            title={TESTI.chiudiBreve}
          >
            <X aria-hidden="true" className="size-icona" />
          </button>
        </div>

        <div className={stili.ricercaFinestra}>
          <input
            type="text"
            placeholder={TESTI.cerca}
            aria-label={TESTI.cerca}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={campo("comodo")}
            data-focus-iniziale
          />
          <button
            type="button"
            onClick={() => onSelectPadre(null)}
            className={pulsante("contorno", "grande")}
          >
            {TESTI.rendiRadice}
          </button>
        </div>

        <div className={stili.elencoFinestra}>
          <table className={stili.tabellaFinestra}>
            <thead className={`${intestazioneTabella()} sticky top-0 z-10`}>
              <tr>
                {TESTI.colonne.map((colonna) => (
                  <th key={colonna} className={cellaIntestazione()}>
                    {colonna}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {aziende.map((az) => (
                <tr key={az.azienda_id} className={rigaTabella()}>
                  <td className={stili.cellaFinestra}>
                    {az.azienda_ragione_sociale}
                  </td>
                  <td className={stili.cellaFinestra}>{az.azienda_partitaIVA}</td>
                  <td className={stili.cellaFinestra}>{az.azienda_citta}</td>
                  <td className={stili.cellaFinestra}>
                    <button
                      type="button"
                      onClick={() => onSelectPadre(az)}
                      className={pulsante("primario", "piccolo")}
                    >
                      {TESTI.seleziona}
                    </button>
                  </td>
                </tr>
              ))}
              {aziende.length === 0 && !loadingAziende && (
                <tr>
                  <td colSpan={TESTI.colonne.length} className={statoVuoto()}>
                    {TESTI.nessuna}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loadingAziende && (
          <div className={stili.aggiornamentoFinestra}>{TESTI.aggiornamento}</div>
        )}
      </div>
    </Dialogo>
  );
}
