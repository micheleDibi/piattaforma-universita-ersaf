import useQueryPagina from "../hooks/useQueryPagina.js";
import { QUERY_PRODOTTI } from "../config/routes/query.js";
import { PERCORSI } from "../config/routes/percorsi.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import IntestazioneElenco from "./shared/IntestazioneElenco";
import AzioneCrea from "./shared/AzioneCrea";
import RigheElenco from "./shared/RigheElenco.jsx";
import { MODELLO_PRODOTTI } from "../config/elenchi.js";
import { rigaProdotto } from "../lib/righeElenco.js";
import CampoRicerca from "./shared/CampoRicerca";
import { campo } from "../config/styles/campo";
import { TESTI_ELENCO } from "../config/testi/elenco.js";
import { contenutoPagina } from "../config/styles/pagina";
import { schedaElenco } from "../config/styles/tabella";
import StatoPagineElenco from "./shared/StatoPagineElenco.jsx";
import usePagineRemote from "../hooks/usePagineRemote.js";
import { paginaElenco, queryProdotti } from "../lib/queryElenchi.js";

export default function ElencoProdottiFormativi() {
  const risorsa = PERCORSI.prodotti;
  const { apri } = useNavigazioneElenco(risorsa.elenco);

  const [query, aggiornaQuery] = useQueryPagina(QUERY_PRODOTTI);
  const searchTerm = query.ricerca;
  const setSearchTerm = ricerca => aggiornaQuery({ ricerca });

  const [universitaList, setUniversitaList] = useState([]);
  const [tipiList, setTipiList] = useState([]);

  const filtroUniversita = query.universita;
  const filtroTipo = query.tipo;
  const filtroAttivo = query.attivo;
  const setFiltroUniversita = universita => aggiornaQuery({ universita });
  const setFiltroTipo = tipo => aggiornaQuery({ tipo });
  const setFiltroAttivo = attivo => aggiornaQuery({ attivo });
  const handleModifica = (id) => {
    apri(risorsa.dettaglio(id));
  };

  const handleNuovo = () => {
    apri(risorsa.nuovo);
  };

  useEffect(() => {
    const fetchFiltriOpzioni = async () => {
      try {
        const [uniRes, tipiRes] = await Promise.all([
          apiFetch(`/listini-testa/opzioni/universita`),
          apiFetch(`/listini-testa/opzioni/tipi-corso`),
        ]);

        if (uniRes.ok) {
          const uniData = await uniRes.json();
          setUniversitaList(uniData);
        }
        if (tipiRes.ok) {
          const tipiData = await tipiRes.json();
          setTipiList(tipiData);
        }
      } catch (err) {
        console.error("Errore caricamento opzioni filtri:", err);
      }
    };
    fetchFiltriOpzioni();
  }, []);

  const pagina = usePagineRemote(queryProdotti(query), paginaElenco, true);

  return (
    <div className={contenutoPagina()}>
      <IntestazioneElenco
        titolo="Prodotti formativi"
        azioni={
          <AzioneCrea
            onClick={handleNuovo}
            etichetta="Nuovo"
            etichettaEstesa="Nuovo prodotto"
          />
        }
        ricerca={
          <CampoRicerca
            valore={searchTerm}
            onCambia={setSearchTerm}
            segnaposto="Cerca per titolo o codice"
          />
        }
        filtri={{
          onAzzera: () => aggiornaQuery({ universita: "Tutte le università", tipo: "Tutti i tipi", attivo: "Tutti" }),
          attivi: [filtroUniversita !== "Tutte le università",
            filtroTipo !== "Tutti i tipi", filtroAttivo !== "Tutti"].filter(Boolean).length,
          contenuto: <>
            <label className="filtri-elenco__campo"><span>{TESTI_ELENCO.universita}</span>
            <select
              value={filtroUniversita}
              aria-label={TESTI_ELENCO.universita}
              onChange={(e) => setFiltroUniversita(e.target.value)}
              className={campo()}
            >
              <option value="Tutte le università" data-senza-filtro>Tutte le università</option>
              {universitaList.map((uni) => (
                <option key={uni.id} value={uni.descrizione}>
                  {uni.descrizione}
                </option>
              ))}
            </select>
            </label>
            <label className="filtri-elenco__campo"><span>{TESTI_ELENCO.tipoCorso}</span>
            <select
              value={filtroTipo}
              aria-label={TESTI_ELENCO.tipoCorso}
              onChange={(e) => setFiltroTipo(e.target.value)}
              className={campo()}
            >
              <option value="Tutti i tipi" data-senza-filtro>Tutti i tipi</option>
              {tipiList.map((tipo) => (
                <option key={tipo.id} value={tipo.descrizione}>
                  {tipo.descrizione}
                </option>
              ))}
            </select>
            </label>
            <label className="filtri-elenco__campo"><span>{TESTI_ELENCO.statoProdotto}</span>
            <select
              value={filtroAttivo}
              aria-label={TESTI_ELENCO.statoProdotto}
              onChange={(e) => setFiltroAttivo(e.target.value)}
              className={campo()}
            >
              <option value="Tutti" data-senza-filtro>Attivo: Tutti</option>
              <option value="Sì">Attivo: Sì</option>
              <option value="No">Attivo: No</option>
            </select>
            </label>
          </>,
        }}
      />
      <div className={schedaElenco("corpo")}>
        <RigheElenco dati={pagina.elementi.map(rigaProdotto)} modello={MODELLO_PRODOTTI}
          onApri={handleModifica}
          vuoto={!pagina.loading && !pagina.errore && "Nessun risultato trovato per i filtri di ricerca selezionati."} />

        <StatoPagineElenco pagina={pagina} />
      </div>
    </div>
  );
}
