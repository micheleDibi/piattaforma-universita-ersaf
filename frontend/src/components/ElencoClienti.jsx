import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";
import { leggiRuolo } from "../lib/sessione";
import IntestazioneElenco from "./shared/IntestazioneElenco";
import CampoRicerca from "./shared/CampoRicerca";
import AzioneCrea from "./shared/AzioneCrea";
import RigheElenco from "./shared/RigheElenco.jsx";
import { modelloClienti } from "../config/elenchi.js";
import { rigaCliente } from "../lib/righeElenco.js";
import { campo } from "../config/styles/campo";
import { TESTI_ELENCO } from "../config/testi/elenco.js";
import { contenutoPagina } from "../config/styles/pagina";
import { schedaElenco } from "../config/styles/tabella";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";

function ElencoClienti({ soloAttuatori = false, soloUtenti = false }) {
  const [sottoscrittori, setSottoscrittori] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRuolo, setSelectedRuolo] = useState("");
  const LIMIT = 40;

  const skipRef = useRef(0);
  const loadingRef = useRef(false);
  const hasMoreRef = useRef(true);
  const searchTermRef = useRef(searchTerm);
  const selectedRuoloRef = useRef(selectedRuolo);

  const navigate = useNavigate();

  const canSee = leggiRuolo() === "nazionale";
  const canSeeAzienda = canSee && soloAttuatori;
  const opzioniRighe = { attuatori: soloAttuatori, mostraAzienda: canSeeAzienda };

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
    selectedRuoloRef.current = selectedRuolo;
  }, [selectedRuolo]);

  useEffect(() => {
    const fetchClientiFiltrati = async () => {
      try {
        setLoading(true);
        loadingRef.current = true;
        skipRef.current = 0;

        const utentiParam = soloUtenti ? "&solo_utenti=true" : "";
        const attuatoriParam = soloAttuatori ? "&solo_attuatori=true" : "";
        const ruoloParam =
          soloAttuatori && selectedRuolo
            ? `&ruolo_codice=${encodeURIComponent(selectedRuolo)}`
            : "";

        const response = await apiFetch(
          `/clienti/?skip=0&limit=${LIMIT}${attuatoriParam}${utentiParam}${ruoloParam}&search=${encodeURIComponent(searchTerm)}`,
        );
        if (!response.ok) {
          throw new Error("Errore durante il recupero dei dati");
        }
        const data = await response.json();

        if (data.length < LIMIT) {
          setHasMore(false);
          hasMoreRef.current = false;
        } else {
          setHasMore(true);
          hasMoreRef.current = true;
        }

        setSottoscrittori(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
        setInitialLoading(false);
        loadingRef.current = false;
      }
    };

    const delayDebounceFn = setTimeout(() => {
      fetchClientiFiltrati();
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, selectedRuolo, soloAttuatori, soloUtenti]);

  // Modifica principale: Evento scroll ottimizzato e corretto
  useEffect(() => {
    const handleScroll = async () => {
      // Calcolo più robusto per l'altezza dello scroll su vari browser
      const scrollTop =
        document.documentElement.scrollTop || document.body.scrollTop;
      const scrollHeight =
        document.documentElement.scrollHeight || document.body.scrollHeight;
      const clientHeight =
        document.documentElement.clientHeight || window.innerHeight;

      if (
        scrollTop + clientHeight >= scrollHeight - 100 &&
        !loadingRef.current &&
        hasMoreRef.current
      ) {
        setLoading(true);
        loadingRef.current = true;

        // Usa skipRef al posto dello state skip per evitare loop
        const nextSkip = skipRef.current + LIMIT;
        skipRef.current = nextSkip;

        try {
          const utentiParam = soloUtenti ? "&solo_utenti=true" : "";
          const attuatoriParam = soloAttuatori ? "&solo_attuatori=true" : "";
          const ruoloParam =
            soloAttuatori && selectedRuoloRef.current
              ? `&ruolo_codice=${encodeURIComponent(selectedRuoloRef.current)}`
              : "";

          const response = await apiFetch(
            `/clienti/?skip=${nextSkip}&limit=${LIMIT}${attuatoriParam}${utentiParam}${ruoloParam}&search=${encodeURIComponent(searchTermRef.current)}`,
          );
          if (!response.ok) {
            throw new Error("Errore durante il recupero dei dati");
          }
          const data = await response.json();

          if (data.length < LIMIT) {
            setHasMore(false);
            hasMoreRef.current = false;
          }

          setSottoscrittori((prev) => {
            const existingIds = new Set(prev.map((item) => item.cliente_id));
            const uniqueNewItems = data.filter(
              (item) => !existingIds.has(item.cliente_id),
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
  }, [soloAttuatori, soloUtenti]); // Rimossa la dipendenza "skip"

  if (initialLoading)
    return (
      <div className={contenutoPagina()}>
        <IndicatoreCaricamento
          dimensione="grande"
          messaggio={soloAttuatori ? "Caricamento attuatori..." : "Caricamento sottoscrittori..."}
          centrato
        />
      </div>
    );
  if (error)
    return <div className="p-4 text-center text-negativo">Errore: {error}</div>;

return (
    <div className={contenutoPagina()}>
      <IntestazioneElenco
        titolo={soloAttuatori ? "Attuatori" : "Sottoscrittori"}
        azioni={
          <AzioneCrea
            onClick={() =>
              navigate(
                soloAttuatori
                  ? "/nuovo?tipo=attuatore"
                  : "/nuovo?tipo=sottoscrittore",
              )
            }
            etichetta="Nuovo"
            etichettaEstesa={
              soloAttuatori ? "Nuovo attuatore" : "Nuovo sottoscrittore"
            }
          />
        }
        ricerca={
          <CampoRicerca
            valore={searchTerm}
            onCambia={setSearchTerm}
            segnaposto={
              soloAttuatori
                ? "Cerca per nome, cognome o azienda"
                : "Cerca per nome o cognome"
            }
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
              <option value="" data-senza-filtro>Tutti i ruoli</option>
              <option value="Aderente">Aderente</option>
              <option value="Provinciale">Provinciale</option>
              <option value="Regionale">Regionale</option>
              <option value="Nazionale">Nazionale</option>
            </select>
            </label>
          ) } : undefined}
      />
      <div className={schedaElenco("corpo")}>
        <RigheElenco
          dati={sottoscrittori.map((item) => rigaCliente(item, opzioniRighe))}
          modello={modelloClienti(opzioniRighe)}
          onApri={(id) => navigate(`/modifica/${id}${soloAttuatori ? "?tipo=attuatore" : ""}`)}
          vuoto={!loading && (soloAttuatori ? "Nessun attuatore trovato." : "Nessun sottoscrittore trovato.")}
        />

        {loading && (
          <div className="border-t border-bordo px-4 py-4">
            <IndicatoreCaricamento dimensione="compatto" messaggio="Caricamento altri elementi..." />
          </div>
        )}

        {!hasMore && (
          <div className="border-t border-bordo px-4 py-3 text-center text-nota text-testo-tenue">
            Hai raggiunto la fine dell'elenco
          </div>
        )}
      </div>
    </div>
  );
}

export default ElencoClienti;
