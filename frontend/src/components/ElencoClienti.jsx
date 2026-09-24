import { useEffect, useState } from "react";
import useQueryPagina from "../hooks/useQueryPagina.js";
import { QUERY_CLIENTI } from "../config/routes/query.js";
import { PERCORSI } from "../config/routes/percorsi.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";


import { leggiRuolo } from "../lib/sessione";
import IntestazioneElenco from "./shared/IntestazioneElenco";
import CampoRicerca from "./shared/CampoRicerca";
import AzioneCrea from "./shared/AzioneCrea";
import RigheElenco from "./shared/RigheElenco.jsx";
import { modelloClienti, RUOLI_FILTRO } from "../config/elenchi.js";
import { rigaCliente } from "../lib/righeElenco.js";
import { campo } from "../config/styles/campo";
import { TESTI_ELENCO } from "../config/testi/elenco.js";
import { contenutoPagina } from "../config/styles/pagina";
import { schedaElenco } from "../config/styles/tabella";
import StatoPagineElenco from "./shared/StatoPagineElenco.jsx";
import usePagineRemote from "../hooks/usePagineRemote.js";
import { apiFetch } from "../lib/api";
import { conteggioClienti, paginaElenco, queryClienti } from "../lib/queryElenchi.js";

function ElencoClienti({ soloAttuatori = false, soloSottoscrittori = false }) {
  const [query, aggiornaQuery] = useQueryPagina(QUERY_CLIENTI);
  const searchTerm = query.ricerca;
  const setSearchTerm = ricerca => aggiornaQuery({ ricerca });
  const selectedRuolo = soloAttuatori ? query.ruolo : "";
  const setSelectedRuolo = ruolo => aggiornaQuery({ ruolo });
  const risorsa = soloAttuatori ? PERCORSI.attuatori : PERCORSI.sottoscrittori;
  const { apri } = useNavigazioneElenco(risorsa.elenco);

  const canSee = leggiRuolo() === "nazionale";
  const canSeeAzienda = canSee && soloAttuatori;
  const opzioniRighe = { attuatori: soloAttuatori, mostraAzienda: canSeeAzienda };

  const pagina = usePagineRemote(queryClienti(query, { soloAttuatori, soloSottoscrittori }), paginaElenco, true);

  // Totale dei risultati con gli stessi filtri dell'elenco. Se la richiesta
  // fallisce il conteggio semplicemente non compare: l'elenco resta usabile.
  const percorsoConteggio = conteggioClienti(query, { soloAttuatori, soloSottoscrittori });
  const [conteggio, setConteggio] = useState({ percorso: null, totale: null });
  useEffect(() => {
    const controllo = new AbortController();
    const timer = setTimeout(() => {
      apiFetch(percorsoConteggio, { signal: controllo.signal })
        .then((risposta) => (risposta.ok ? risposta.json() : null))
        .then((dati) => {
          if (dati) setConteggio({ percorso: percorsoConteggio, totale: dati.totale });
        })
        .catch(() => {});
    }, 300);
    return () => {
      clearTimeout(timer);
      controllo.abort();
    };
  }, [percorsoConteggio]);
  const totale = conteggio.percorso === percorsoConteggio ? conteggio.totale : null;
  const testi = TESTI_ELENCO.clienti[soloAttuatori ? "attuatori" : "sottoscrittori"];
  return (
    <div className={contenutoPagina()}>
      <IntestazioneElenco
        titolo={testi.titolo}
        conteggio={totale === null ? undefined : TESTI_ELENCO.risultati(totale)}
        azioni={
          <AzioneCrea
            onClick={() => apri(risorsa.nuovo)}
            etichetta={testi.nuovo}
            etichettaEstesa={testi.nuovoEsteso}
          />
        }
        ricerca={
          <CampoRicerca
            valore={searchTerm}
            onCambia={setSearchTerm}
            segnaposto={testi.segnaposto}
          />
        }
        filtri={soloAttuatori ? { attivi: selectedRuolo ? 1 : 0,
          onAzzera: () => setSelectedRuolo(""), contenuto: (
            <label className="filtri-elenco__campo"><span>{TESTI_ELENCO.ruolo}</span>
            <select
              value={selectedRuolo}
              aria-label={TESTI_ELENCO.ruolo}
              onChange={(e) => setSelectedRuolo(e.target.value)}
              className={campo()}
            >
              <option value="" data-senza-filtro>{TESTI_ELENCO.tuttiRuoli}</option>
              {RUOLI_FILTRO.map((ruolo) => (
                <option key={ruolo} value={ruolo}>{ruolo}</option>
              ))}
            </select>
            </label>
          ) } : undefined}
      />
      <div className={schedaElenco("corpo")}>
        <RigheElenco
          dati={pagina.elementi.map((item) => rigaCliente(item, opzioniRighe))}
          modello={modelloClienti(opzioniRighe)}
          onApri={(id) => apri(risorsa.dettaglio(id))}
          vuoto={!pagina.loading && !pagina.errore && testi.vuoto}
        />

        <StatoPagineElenco pagina={pagina} />
      </div>
    </div>
  );
}

export default ElencoClienti;
