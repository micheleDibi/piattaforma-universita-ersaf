import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";

function ElencoSottoscrittori() {
  const [sottoscrittori, setSottoscrittori] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const LIMIT = 20;

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

  // Gestione della ricerca iniziale e quando cambia searchTerm con debounce
  useEffect(() => {
    const fetchClientiFiltrati = async () => {
      try {
        setLoading(true);
        loadingRef.current = true;
        setSkip(0);
        skipRef.current = 0;

        const response = await fetch(
          `http://localhost:8000/clienti/?skip=0&limit=${LIMIT}&search=${encodeURIComponent(searchTerm)}`,
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
  }, [searchTerm]);

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
          const response = await fetch(
            `http://localhost:8000/clienti/?skip=${nextSkip}&limit=${LIMIT}&search=${encodeURIComponent(searchTermRef.current)}`,
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
  }, [skip]);

  if (initialLoading)
    return <div className="p-4 text-center text-gray-500">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-red-500">Errore: {error}</div>;

  return (
    <>
      <div className="max-w-4xl mx-auto my-6 flex flex-col sm:flex-row justify-between items-center gap-4 px-2">
        <h3 className="text-xl font-bold text-gray-800">
          Elenco Sottoscrittori:
        </h3>

        <div className="w-full sm:w-72">
          <input
            type="text"
            placeholder="Cerca per nome o cognome..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          />
        </div>

        <button
          onClick={() => navigate("/nuovo")}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none transition-colors cursor-pointer whitespace-nowrap"
        >
          Nuovo Sottoscrittore
        </button>
      </div>

      <div className="max-w-4xl mx-auto bg-white shadow-md rounded-lg overflow-hidden border border-gray-200 my-6">
        <table className="min-w-full divide-y divide-gray-200 text-left">
          <thead className="bg-gray-100 sticky top-0 z-10">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Nome
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Cognome
              </th>
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
                  colSpan="3"
                  className="px-6 py-8 text-center text-sm text-gray-500"
                >
                  Nessun sottoscrittore trovato.
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
    </>
  );
}

export default ElencoSottoscrittori;
