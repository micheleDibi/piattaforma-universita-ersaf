import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";
import IntestazioneElenco from "./shared/IntestazioneElenco";
import AzioneCrea from "./shared/AzioneCrea";
import RigheElenco from "./shared/RigheElenco.jsx";
import { MODELLO_AZIENDE } from "../config/elenchi.js";
import { rigaAzienda } from "../lib/righeElenco.js";
import CampoRicerca from "./shared/CampoRicerca";
import { contenutoPagina } from "../config/styles/pagina";
import { schedaElenco } from "../config/styles/tabella";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";

function ElencoAziende() {
  const [aziende, setAziende] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const LIMIT = 40;

  const skipRef = useRef(0);
  const loadingRef = useRef(false);
  const hasMoreRef = useRef(true);
  const searchTermRef = useRef(searchTerm);

  const navigate = useNavigate();

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
    const fetchAziendeFiltrate = async () => {
      try {
        setLoading(true);
        loadingRef.current = true;
        setSkip(0);
        skipRef.current = 0;

        const response = await apiFetch(
          `/aziende/?skip=0&limit=${LIMIT}&search=${encodeURIComponent(searchTerm)}`,
        );
        if (!response.ok) {
          throw new Error("Errore durante il recupero dei dati delle aziende");
        }
        const data = await response.json();

        if (data.length < LIMIT) {
          setHasMore(false);
          hasMoreRef.current = false;
        } else {
          setHasMore(true);
          hasMoreRef.current = true;
        }

        setAziende(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
        setInitialLoading(false);
        loadingRef.current = false;
      }
    };

    const delayDebounceFn = setTimeout(() => {
      fetchAziendeFiltrate();
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm]);

  useEffect(() => {
    const handleScroll = async () => {
      if (
        window.innerHeight + window.scrollY >=
          document.documentElement.scrollHeight - 100 &&
        !loadingRef.current &&
        hasMoreRef.current
      ) {
        setLoading(true);
        loadingRef.current = true;

        const nextSkip = skip + LIMIT;
        setSkip(nextSkip);
        skipRef.current = nextSkip;

        try {
          const response = await apiFetch(
            `/aziende/?skip=${nextSkip}&limit=${LIMIT}&search=${encodeURIComponent(searchTermRef.current)}`,
          );
          if (!response.ok) {
            throw new Error("Errore durante il recupero dei dati");
          }
          const data = await response.json();

          if (data.length < LIMIT) {
            setHasMore(false);
            hasMoreRef.current = false;
          }

          setAziende((prev) => {
            const existingIds = new Set(prev.map((item) => item.azienda_id));
            const uniqueNewItems = data.filter(
              (item) => !existingIds.has(item.azienda_id),
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
  }, [skip]);

  if (initialLoading)
    return (
      <div className={contenutoPagina()}>
        <IndicatoreCaricamento dimensione="grande" messaggio="Caricamento aziende..." centrato />
      </div>
    );
  if (error)
    return <div className="p-4 text-center text-negativo">Errore: {error}</div>;

  return (
    <div className={contenutoPagina()}>
      <IntestazioneElenco
        titolo="Aziende"
        azioni={
          <AzioneCrea
            onClick={() => navigate("/nuova-azienda")}
            etichetta="Nuova"
            etichettaEstesa="Nuova azienda"
          />
        }
        ricerca={
          <CampoRicerca
            valore={searchTerm}
            onCambia={setSearchTerm}
            segnaposto="Cerca per ragione sociale"
          />
        }
      />
      <div className={schedaElenco("corpo")}>
        <RigheElenco dati={aziende.map(rigaAzienda)} modello={MODELLO_AZIENDE}
          onApri={(id) => navigate(`/modifica-azienda/${id}`)}
          vuoto={!loading && "Nessuna azienda trovata."} />

        {loading && (
          <div className="border-t border-bordo py-4">
            <IndicatoreCaricamento dimensione="compatto" messaggio="Caricamento altri elementi..." />
          </div>
        )}

        {!hasMore && (
          <div className="border-t border-bordo py-4 text-center text-nota text-testo-tenue">
            Hai raggiunto la fine dell'elenco
          </div>
        )}
      </div>
    </div>
  );
}

export default ElencoAziende;
