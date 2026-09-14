import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
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
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";

export default function ElencoProdottiFormativi() {
  const navigate = useNavigate();

  const [prodotti, setProdotti] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const [universitaList, setUniversitaList] = useState([]);
  const [tipiList, setTipiList] = useState([]);

  const [filtroUniversita, setFiltroUniversita] = useState(
    "Tutte le università",
  );
  const [filtroTipo, setFiltroTipo] = useState("Tutti i tipi");
  const [filtroAttivo, setFiltroAttivo] = useState("Tutti");
  const LIMIT = 40;

  const skipRef = useRef(0);
  const loadingRef = useRef(false);
  const hasMoreRef = useRef(true);
  const searchTermRef = useRef(searchTerm);
  const filtroUniversitaRef = useRef(filtroUniversita);
  const filtroTipoRef = useRef(filtroTipo);
  const filtroAttivoRef = useRef(filtroAttivo);

  useEffect(() => {
    loadingRef.current = loading;
  }, [loading]);
  useEffect(() => {
    hasMoreRef.current = hasMore;
  }, [hasMore]);
  useEffect(() => {
    searchTermRef.current = searchTerm;
  }, [searchTerm]);
  useEffect(() => {
    filtroUniversitaRef.current = filtroUniversita;
  }, [filtroUniversita]);
  useEffect(() => {
    filtroTipoRef.current = filtroTipo;
  }, [filtroTipo]);
  useEffect(() => {
    filtroAttivoRef.current = filtroAttivo;
  }, [filtroAttivo]);

  const handleModifica = (id) => {
    navigate(`/inserimentoprodotto/${id}`);
  };

  const handleNuovo = () => {
    navigate("/inserimentoprodotto");
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

  const fetchProdottiFiltrati = async (
    searchVal,
    uniVal,
    tipoVal,
    attivoVal,
  ) => {
    try {
      setLoading(true);
      loadingRef.current = true;
      skipRef.current = 0;

      const uniParam =
        uniVal !== "Tutte le università"
          ? `&universita=${encodeURIComponent(uniVal)}`
          : "";
      const tipoParam =
        tipoVal !== "Tutti i tipi"
          ? `&tipo_corso=${encodeURIComponent(tipoVal)}`
          : "";
      const attivoParam =
        attivoVal !== "Tutti" ? `&attivo=${attivoVal === "Sì" ? -1 : 0}` : "";
      const searchParam =
        searchVal && searchVal.trim()
          ? `&search=${encodeURIComponent(searchVal.trim())}`
          : "";

      const response = await apiFetch(
        `/listini-testa/?skip=0&limit=${LIMIT}${searchParam}${uniParam}${tipoParam}${attivoParam}`,
      );
      if (!response.ok) throw new Error("Errore durante il recupero dei dati");
      const data = await response.json();

      setHasMore(data.length >= LIMIT);
      setProdotti(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setInitialLoading(false);
      loadingRef.current = false;
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchProdottiFiltrati(
        searchTerm,
        filtroUniversita,
        filtroTipo,
        filtroAttivo,
      );
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, filtroUniversita, filtroTipo, filtroAttivo]);

  useEffect(() => {
    const handleScroll = async () => {
      if (
        window.innerHeight + window.scrollY >=
          document.documentElement.scrollHeight - 200 &&
        !loadingRef.current &&
        hasMoreRef.current
      ) {
        setLoading(true);
        loadingRef.current = true;

        const nextSkip = skipRef.current + LIMIT;
        skipRef.current = nextSkip;

        try {
          const uniParam =
            filtroUniversitaRef.current !== "Tutte le università"
              ? `&universita=${encodeURIComponent(filtroUniversitaRef.current)}`
              : "";
          const tipoParam =
            filtroTipoRef.current !== "Tutti i tipi"
              ? `&tipo_corso=${encodeURIComponent(filtroTipoRef.current)}`
              : "";
          const attivoParam =
            filtroAttivoRef.current !== "Tutti"
              ? `&attivo=${filtroAttivoRef.current === "Sì" ? -1 : 0}`
              : "";
          const searchParam = searchTermRef.current.trim()
            ? `&search=${encodeURIComponent(searchTermRef.current.trim())}`
            : "";

          const response = await apiFetch(
            `/listini-testa/?skip=${nextSkip}&limit=${LIMIT}${searchParam}${uniParam}${tipoParam}${attivoParam}`,
          );
          if (!response.ok)
            throw new Error("Errore durante il recupero dei dati");
          const data = await response.json();

          if (data.length < LIMIT) setHasMore(false);

          setProdotti((prev) => {
            const existingIds = new Set(prev.map((item) => item.listTesta_id));
            const uniqueNewItems = data.filter(
              (item) => !existingIds.has(item.listTesta_id),
            );
            return [...prev, ...uniqueNewItems];
          });
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
          loadingRef.current = false;
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  if (initialLoading)
    return (
      <div className={contenutoPagina()}>
        <IndicatoreCaricamento dimensione="grande" messaggio="Caricamento prodotti formativi..." centrato />
      </div>
    );
  if (error)
    return <div className="p-4 text-center text-negativo">Errore: {error}</div>;

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
          onAzzera: () => { setFiltroUniversita("Tutte le università"); setFiltroTipo("Tutti i tipi"); setFiltroAttivo("Tutti"); },
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
        <RigheElenco dati={prodotti.map(rigaProdotto)} modello={MODELLO_PRODOTTI}
          onApri={handleModifica}
          vuoto={!loading && "Nessun risultato trovato per i filtri di ricerca selezionati."} />

        {/* Indicatore di caricamento o fine lista */}
        {loading && (
          <div className="border-t border-bordo px-4 py-4">
            <IndicatoreCaricamento dimensione="compatto" messaggio="Caricamento altri elementi..." />
          </div>
        )}

        {!hasMore && prodotti.length > 0 && (
          <div className="border-t border-bordo px-4 py-4 text-center text-nota italic text-testo-tenue">
            Hai raggiunto la fine della lista. Non ci sono altri risultati.
          </div>
        )}
      </div>
    </div>
  );
}
