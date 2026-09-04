import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";
import { leggiRuolo } from "../lib/sessione";

function ElencoClienti({ soloAttuatori = false }) {
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

  // Visibilità
  // leggiRuolo() legge dalla sessione e il valore e' normalizzato in minuscolo
  // alla scrittura: il backend confronta ruolo_codice.lower(), quindi un
  // confronto con "Aderente" maiuscolo dipenderebbe da come il database
  // capitalizza il valore.
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

  // Gestione della ricerca iniziale e quando cambiano searchTerm, selectedRuolo o soloAttuatori con debounce
  useEffect(() => {
    const fetchClientiFiltrati = async () => {
      try {
        setLoading(true);
        loadingRef.current = true;
        setSkip(0);
        skipRef.current = 0;

        const attuatoriParam = soloAttuatori ? "&solo_attuatori=true" : "";
        const ruoloParam =
          soloAttuatori && selectedRuolo
            ? `&ruolo_codice=${encodeURIComponent(selectedRuolo)}`
            : "";

        const response = await apiFetch(
          `/clienti/?skip=0&limit=${LIMIT}${attuatoriParam}${ruoloParam}&search=${encodeURIComponent(searchTerm)}`,
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
  }, [searchTerm, selectedRuolo, soloAttuatori]);

  // Funzione per caricare altri elementi allo scroll
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
          const attuatoriParam = soloAttuatori ? "&solo_attuatori=true" : "";
          const ruoloParam =
            soloAttuatori && selectedRuoloRef.current
              ? `&ruolo_codice=${encodeURIComponent(selectedRuoloRef.current)}`
              : "";

          const response = await apiFetch(
            `/clienti/?skip=${nextSkip}&limit=${LIMIT}${attuatoriParam}${ruoloParam}&search=${encodeURIComponent(searchTermRef.current)}`,
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
  }, [skip, soloAttuatori]);

  if (initialLoading)
    return <div className="p-4 text-center text-gray-500">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-red-500">Errore: {error}</div>;

  let colSpanCount = 3;
  if (soloAttuatori) colSpanCount += 1;
  if (canSeeAzienda) colSpanCount += 1;

  return (
    <>
      <div className="w-full p-6">
        <div className="w-full my-6 flex flex-col sm:flex-row justify-between items-center gap-4 px-2">
          <h3 className="text-xl font-bold text-gray-800">
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
          </div>

          <button
            onClick={() => navigate("/nuovo")}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none transition-colors cursor-pointer whitespace-nowrap"
          >
            Nuovo Sottoscrittore
          </button>
        </div>
        <div>
          {soloAttuatori && (
            <select
              value={selectedRuolo}
              onChange={(e) => setSelectedRuolo(e.target.value)}
              className="w-full sm:w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-white"
            >
              <option value="">Tutti i ruoli</option>
              <option value="Aderente">Aderente</option>
              <option value="Provinciale">Provinciale</option>
              <option value="Regionale">Regionale</option>
              <option value="Nazionale">Nazionale</option>
            </select>
          )}
        </div>

        <div className="w-full bg-white shadow-md rounded-lg overflow-hidden border border-gray-200 my-6">
          <table className="min-w-full divide-y divide-gray-200 text-left">
            <thead className="bg-gray-100 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Cognome
                </th>

                {/* Colonna Ruolo visibile solo per gli attuatori */}
                {soloAttuatori && (
                  <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Ruolo
                  </th>
                )}

                {canSeeAzienda && (
                  <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Azienda
                  </th>
                )}

                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider text-right">
                  Modifica
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sottoscrittori.map((item, index) => (
                <tr
                  key={item.cliente_id || index}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.cliente_nome}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.cliente_cognome}
                  </td>

                  {/* Stampiamo il ruolo prendendolo dalla relazione del backend */}
                  {soloAttuatori && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.ruolo?.ruolo_codice || "-"}
                    </td>
                  )}

                  {canSeeAzienda && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.azienda?.azienda_ragione_sociale || "-"}
                    </td>
                  )}
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => navigate(`/modifica/${item.cliente_id}`)}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none transition-colors cursor-pointer"
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
                    className="px-6 py-8 text-center text-sm text-gray-500"
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
            <div className="py-4 text-center text-sm text-gray-500 bg-gray-50">
              Caricamento altri elementi...
            </div>
          )}

          {!hasMore && (
            <div className="py-4 text-center text-xs text-gray-400 bg-gray-50">
              Hai raggiunto la fine dell'elenco
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default ElencoClienti;
