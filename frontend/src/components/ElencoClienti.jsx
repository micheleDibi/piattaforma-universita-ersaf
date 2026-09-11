import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";
import { leggiRuolo } from "../lib/sessione";
import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import {
  contenitoreTabella,
  intestazioneTabella,
  rigaTabella,
} from "../config/styles/superficie";

function ElencoClienti({ soloAttuatori = false, soloUtenti = false }) {
  const [sottoscrittori, setSottoscrittori] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);
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

  const canSee = leggiRuolo() === "aderente";
  const canSeeAzienda = canSee && soloAttuatori;

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
        setSkip(0);
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
        setSkip(nextSkip);
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
    return <div className="p-4 text-center text-testo-tenue">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-negativo">Errore: {error}</div>;

  let colSpanCount = 3;
  if (soloAttuatori) colSpanCount += 1;
  if (canSeeAzienda) colSpanCount += 1;

  return (
    <>
      <div className="w-full p-6">
        <div className="w-full my-6 flex flex-col sm:flex-row justify-between items-center gap-4 px-2">
          <h3 className="text-xl font-bold text-testo">
            {soloAttuatori ? "Elenco Attuatori:" : "Elenco Sottoscrittori:"}
          </h3>

          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <div className="w-full sm:w-72">
              <input
                type="text"
                placeholder={
                  soloAttuatori
                    ? "Cerca per nome, cognome o azienda..."
                    : "Cerca per nome o cognome..."
                }
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={campo()}
              />
            </div>
          </div>

          <button
            type="button"
            onClick={() =>
              navigate(
                soloAttuatori
                  ? "/nuovo?tipo=attuatore"
                  : "/nuovo?tipo=sottoscrittore",
              )
            }
            className={`${pulsante()} whitespace-nowrap`}
          >
            {soloAttuatori ? "Nuovo Attuatore" : "Nuovo Sottoscrittore"}
          </button>
        </div>
        <div>
          {soloAttuatori && (
            <select
              value={selectedRuolo}
              onChange={(e) => setSelectedRuolo(e.target.value)}
              className={`${campo()} sm:w-48`}
            >
              <option value="">Tutti i ruoli</option>
              <option value="Aderente">Aderente</option>
              <option value="Provinciale">Provinciale</option>
              <option value="Regionale">Regionale</option>
              <option value="Nazionale">Nazionale</option>
            </select>
          )}
        </div>

        <div className={`${contenitoreTabella()} my-6`}>
          <table className="min-w-full text-left">
            <thead className={`${intestazioneTabella()} sticky top-0 z-10`}>
              <tr>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Cognome
                </th>

                {soloAttuatori && (
                  <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                    Ruolo
                  </th>
                )}

                {canSeeAzienda && (
                  <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                    Azienda
                  </th>
                )}

                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider text-right">
                  Modifica
                </th>
              </tr>
            </thead>
            <tbody className="bg-superficie">
              {sottoscrittori.map((item, index) => (
                <tr
                  key={item.cliente_id || index}
                  className={rigaTabella()}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-testo-forte">
                    {item.cliente_nome}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-testo-forte">
                    {item.cliente_cognome}
                  </td>

                  {soloAttuatori && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-testo-tenue">
                      {item.ruolo?.ruolo_codice || "-"}
                    </td>
                  )}

                  {canSeeAzienda && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-testo-tenue">
                      {item.azienda?.azienda_ragione_sociale || "-"}
                    </td>
                  )}
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      type="button"
                      onClick={() => navigate(`/modifica/${item.cliente_id}`)}
                      className={pulsante("primario", "piccolo")}
                    >
                      Modifica
                    </button>
                  </td>
                </tr>
              ))}
              {sottoscrittori.length === 0 && !loading && (
                <tr>
                  <td
                    colSpan={colSpanCount}
                    className="px-6 py-8 text-center text-sm text-testo-tenue"
                  >
                    {soloAttuatori
                      ? "Nessun attuatore trovato."
                      : "Nessun sottoscrittore trovato."}
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

export default ElencoClienti;
