import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";
import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import {
  contenitoreTabella,
  intestazioneTabella,
  rigaTabella,
} from "../config/styles/superficie";

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
    return <div className="p-4 text-center text-testo-tenue">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-negativo">Errore: {error}</div>;

  return (
    <>
      <div className="w-full p-6">
        <div className="w-full my-6 flex flex-col sm:flex-row justify-between items-center gap-4 px-2">
          <h3 className="text-xl font-bold text-testo">Elenco Aziende:</h3>

          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <div className="w-full sm:w-72">
              <input
                type="text"
                placeholder="Cerca per ragione sociale..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={campo()}
              />
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate("/nuova-azienda")}
            className={`${pulsante()} whitespace-nowrap`}
          >
            Nuova Azienda
          </button>
        </div>

        <div className={`${contenitoreTabella()} my-6`}>
          <table className="min-w-full text-left">
            <thead className={`${intestazioneTabella()} sticky top-0 z-10`}>
              <tr>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Ragione Sociale
                </th>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Sede
                </th>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider text-right">
                  Modifica
                </th>
              </tr>
            </thead>
            <tbody className="bg-superficie">
              {aziende.map((item, index) => {
                const sede = [
                  item.azienda_via,
                  item.azienda_civico,
                  item.azienda_citta && item.azienda_provincia
                    ? `- ${item.azienda_citta} (${item.azienda_provincia})`
                    : item.azienda_citta,
                  item.azienda_CAP,
                ]
                  .filter(Boolean)
                  .join(" ");

                return (
                  <tr
                    key={item.azienda_id || index}
                    className={rigaTabella()}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-testo-forte">
                      {item.azienda_ragione_sociale}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-testo-tenue">
                      {sede || "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        type="button"
                        onClick={() =>
                          navigate(`/modifica-azienda/${item.azienda_id}`)
                        }
                        className={pulsante("primario", "piccolo")}
                      >
                        Modifica
                      </button>
                    </td>
                  </tr>
                );
              })}
              {aziende.length === 0 && !loading && (
                <tr className="border-t border-bordo">
                  <td
                    colSpan={3}
                    className="px-6 py-8 text-center text-sm text-testo-tenue"
                  >
                    Nessuna azienda trovata.
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          {loading && (
            <div className="py-4 text-center text-sm text-testo-tenue bg-superficie-tenue">
              Caricamento altri elementi...
            </div>
          )}

          {!hasMore && (
            <div className="py-4 text-center text-nota text-testo-tenue bg-superficie-tenue">
              Hai raggiunto la fine dell'elenco
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default ElencoAziende;
