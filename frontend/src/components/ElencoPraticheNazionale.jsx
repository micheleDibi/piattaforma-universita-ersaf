import { useEffect, useId, useState } from "react";
import { PERCORSI } from "../config/routes/percorsi.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import IntestazioneElenco from "./shared/IntestazioneElenco";
import RigheElenco from "./shared/RigheElenco.jsx";
import CampoRicerca from "./shared/CampoRicerca";
import StatoPagineElenco from "./shared/StatoPagineElenco.jsx";
import { MODELLO_PRATICHE_NAZIONALE } from "../config/elenchi.js";
import { rigaPratica } from "../lib/righeElenco.js";
import { gruppoUnico, paginaPratiche, raggruppaPerStato } from "../lib/pratiche";
import { caricaPagina } from "../lib/pagineRemote";
import { BLOCCHI_PRATICHE } from "../lib/configPratiche";
import useFiltriPraticheNazionale from "../hooks/useFiltriPraticheNazionale";
import usePagineRemote from "../hooks/usePagineRemote";
import { contenutoPagina } from "../config/styles/pagina";
import { schedaElenco, statoVuoto } from "../config/styles/tabella";
import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";

function Filtri({ filtri }) {
  return (
    <>
      <label className="filtri-elenco__campo">
        Codice pratica
        <input
          type="text"
          className={campo()}
          value={filtri.numeroPratica}
          onChange={(e) => filtri.setNumeroPratica(e.target.value)}
          placeholder="Cerca per codice pratica"
        />
      </label>
      <label className="filtri-elenco__campo">
        Stato
        <select className={campo()} value={filtri.stato} onChange={(e) => filtri.setStato(e.target.value)}>
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
      {filtri.errore && (
        <div role="alert">
          {filtri.errore}
          <button type="button" className={pulsante("discreto")} onClick={filtri.riprova}>
            Riprova
          </button>
        </div>
      )}
    </>
  );
}

/** I loghi dei quattro atenei, gli stessi del pannello Pratiche degli altri
 * ruoli: uno scelto filtra l'elenco, di nuovo lo stesso torna a tutti. */
function SelettoreAtenei({ universita, onCambia }) {
  return (
    <div className="atenei-elenco" role="group" aria-label="Università">
      {BLOCCHI_PRATICHE.map((blocco) => {
        const id = String(blocco.nomeUniversitaId);
        const scelto = universita === id;
        return (
          <button
            key={blocco.chiave}
            type="button"
            className="atenei-elenco__pulsante"
            aria-pressed={scelto}
            title={blocco.titolo}
            onClick={() => onCambia(scelto ? "" : id)}
          >
            <img src={blocco.logo} alt={blocco.titolo} className="atenei-elenco__logo" />
          </button>
        );
      })}
    </div>
  );
}

/** I numeri accanto ai gruppi: quante pratiche ha ogni stato con i filtri
 * attivi, anche quelle non ancora caricate. Null mentre arrivano o se la
 * richiesta fallisce: i gruppi restano, senza numero. */
function useConteggi(percorso) {
  const [conteggi, setConteggi] = useState({ percorso: null, valori: null });
  useEffect(() => {
    const controller = new AbortController();
    caricaPagina(percorso, controller.signal)
      .then((valori) => !controller.signal.aborted && setConteggi({ percorso, valori }))
      .catch(() => !controller.signal.aborted && setConteggi({ percorso, valori: null }));
    return () => controller.abort();
  }, [percorso]);
  return conteggi.percorso === percorso ? conteggi.valori : null;
}

function Gruppo({ gruppo, onApri }) {
  const id = useId();
  return (
    <section className="gruppo-pratiche" aria-labelledby={id}>
      <h2 id={id} className="gruppo-pratiche__titolo">
        {gruppo.titolo}
        {gruppo.totale !== null && <span className="gruppo-pratiche__totale">({gruppo.totale})</span>}
      </h2>
      <RigheElenco
        dati={gruppo.pratiche.map(rigaPratica)}
        modello={{ ...MODELLO_PRATICHE_NAZIONALE, etichetta: gruppo.titolo }}
        onApri={onApri}
      />
    </section>
  );
}

/** Elenco pratiche del Nazionale: tutte le pratiche tranne le Bozze, ordinate
 * per stato e, dentro ogni stato, dalla modifica piu' recente. Con ricerca o
 * filtri attivi l'elenco e' diviso in un gruppo per stato; senza, un solo
 * gruppo "Tutte le pratiche". Niente tasto
 * Nuova: il Nazionale gestisce le pratiche, non le crea. */
export default function ElencoPraticheNazionale() {
  const risorsa = PERCORSI.pratiche;
  const { apri } = useNavigazioneElenco(risorsa.elenco);
  const filtri = useFiltriPraticheNazionale();
  const pagina = usePagineRemote(filtri.query, paginaPratiche, true);
  const conteggi = useConteggi(filtri.queryConteggi);
  const gruppi = filtri.senzaFiltri
    ? gruppoUnico(pagina.elementi, conteggi)
    : raggruppaPerStato(pagina.elementi, conteggi);

  return (
    <div className={contenutoPagina()}>
      <IntestazioneElenco
        titolo="Elenco Pratiche"
        selettore={<SelettoreAtenei universita={filtri.universita} onCambia={filtri.setUniversita} />}
        ricerca={
          <CampoRicerca valore={filtri.ricerca} onCambia={filtri.setRicerca} segnaposto="Cerca per sottoscrittore" />
        }
        filtri={{
          contenuto: <Filtri filtri={filtri} />,
          attivi: filtri.attivi,
          onAzzera: filtri.azzera,
        }}
      />
      <div className={schedaElenco("corpo")} aria-busy={pagina.loading}>
        {gruppi.length === 0
          ? !pagina.loading && !pagina.errore && (
              <p className={statoVuoto()} role="status">
                Nessuna pratica trovata.
              </p>
            )
          : gruppi.map((gruppo) => (
              <Gruppo key={gruppo.statoId} gruppo={gruppo} onApri={(id) => apri(risorsa.dettaglio(id))} />
            ))}
        <StatoPagineElenco pagina={pagina} />
      </div>
    </div>
  );
}
