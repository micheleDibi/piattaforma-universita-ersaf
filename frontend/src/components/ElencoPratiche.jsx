import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";

function ElencoPratiche() {
  const [pratiche, setPratiche] = useState([]);
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
    const fetchPraticheFiltrate = async () => {
      try {
        setLoading(true);
        loadingRef.current = true;
        setSkip(0);
        skipRef.current = 0;

        const response = await apiFetch(
          `/pratiche/?skip=0&limit=${LIMIT}&search=${encodeURIComponent(searchTerm)}`,
        );
        if (!response.ok) {
          throw new Error("Errore durante il recupero dei dati delle pratiche");
        }
        const data = await response.json();

        if (data.length < LIMIT) {
          setHasMore(false);
          hasMoreRef.current = false;
        } else {
          setHasMore(true);
          hasMoreRef.current = true;
        }

        setPratiche(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
        setInitialLoading(false);
        loadingRef.current = false;
      }
    };

    const delayDebounceFn = setTimeout(() => {
      fetchPraticheFiltrate();
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
            `/pratiche/?skip=${nextSkip}&limit=${LIMIT}&search=${encodeURIComponent(searchTermRef.current)}`,
          );
          if (!response.ok) {
            throw new Error("Errore durante il recupero dei dati");
          }
          const data = await response.json();

          if (data.length < LIMIT) {
            setHasMore(false);
            hasMoreRef.current = false;
          }

          setPratiche((prev) => {
            const existingIds = new Set(prev.map((item) => item.pratica_id));
            const uniqueNewItems = data.filter(
              (item) => !existingIds.has(item.pratica_id),
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
      <div className="w-full p-6">
        <div className="w-full my-6 flex flex-col sm:flex-row justify-between items-center gap-4 px-2">
          <h3 className="text-xl font-bold text-gray-800">Elenco Pratiche:</h3>

          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <div className="w-full sm:w-72">
              <input
                type="text"
                placeholder="Cerca per numero pratica..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate("/nuova-pratica")}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none transition-colors cursor-pointer whitespace-nowrap"
          >
            Nuova Pratica
          </button>
        </div>

        <div className="w-full bg-white shadow-md rounded-lg overflow-hidden border border-gray-200 my-6">
          <table className="min-w-full divide-y divide-gray-200 text-left">
            <thead className="bg-gray-100 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Numero
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Corso
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Stato
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider text-right">
                  Modifica
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pratiche.map((item, index) => (
                <tr
                  key={item.pratica_id || index}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.pratica_numero || "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.cliente_nome_completo || "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.listTesta_descrizione || "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.pratica_stato_descrizione || "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      type="button"
                      onClick={() =>
                        navigate(`/modifica-pratica/${item.pratica_id}`)
                      }
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none transition-colors cursor-pointer"
                    >
                      Modifica
                    </button>
                  </td>
                </tr>
              ))}
              {pratiche.length === 0 && !loading && (
                <tr>
                  <td
                    colSpan={5}
                    className="px-6 py-8 text-center text-sm text-gray-500"
                  >
                    Nessuna pratica trovata.
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

export default ElencoPratiche;
