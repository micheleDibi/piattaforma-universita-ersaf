import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { STUDENTI_PRATICHE } from "../config/filtriPratiche";
import SelezioneRicercabile from "./shared/SelezioneRicercabile";

export default function FiltriPratiche({ filtri }) {
  const opzioniTipoCorso = filtri.tipiCorso.filter((t) =>
    filtri.tipoCorso.includes(t.listino_tipoCorso_id),
  );

  return (
    <>
      <label className="filtri-elenco__campo">
        Numero pratica
        <input
          type="text"
          className={campo()}
          value={filtri.numeroPratica}
          onChange={(e) => filtri.setNumeroPratica(e.target.value)}
          placeholder="Cerca per numero pratica"
        />
      </label>
      <label className="filtri-elenco__campo">
        Stato
        <select
          className={campo()}
          value={filtri.stato}
          onChange={(e) => filtri.setStato(e.target.value)}
        >
          <option value="" data-senza-filtro>
            Tutti gli stati
          </option>
          {filtri.stati.map((stato) => (
            <option key={stato.id} value={stato.id}>
              {stato.label}
            </option>
          ))}
        </select>
      </label>
      {filtri.filtroInterno === "1" && opzioniTipoCorso.length > 1 && (
        <label className="filtri-elenco__campo">
          Tipologia corso
          <select
            className={campo()}
            value={filtri.tipoSelezionato}
            onChange={(e) => filtri.setTipoSelezionato(e.target.value)}
          >
            <option value="" data-senza-filtro>
              Tutte
            </option>
            {opzioniTipoCorso.map((t) => (
              <option
                key={t.listino_tipoCorso_id}
                value={t.listino_tipoCorso_id}
              >
                {t.listino_tipoCorso_descrizione}
              </option>
            ))}
          </select>
        </label>
      )}
      {filtri.errore && (
        <div role="alert">
          {filtri.errore}
          <button
            type="button"
            className={pulsante("discreto")}
            onClick={filtri.riprova}
          >
            Riprova
          </button>
        </div>
      )}
      <SelezioneRicercabile
        configurazione={STUDENTI_PRATICHE}
        selezionati={filtri.studenti}
        onCambia={filtri.setStudenti}
      />
    </>
  );
}
