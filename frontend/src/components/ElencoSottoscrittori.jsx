import { useState, useEffect } from "react";
import { useNavigate } from "react-router";

function ElencoSottoscrittori() {
  const [sottoscrittori, setSottoscrittori] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const LIMIT = 20;

  const navigate = useNavigate();

  useEffect(() => {
    const fetchClientiIniziali = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/clienti/?skip=0&limit=${LIMIT}`,
        );
        if (!response.ok) {
          throw new Error("Errore durante il recupero dei dati");
        }
        const data = await response.json();

        if (data.length < LIMIT) {
          setHasMore(false);
        }

        setSottoscrittori(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
        setInitialLoading(false);
      }
    };

    fetchClientiIniziali();
  }, []);

  // Funzione per caricare altri elementi allo scroll
  useEffect(() => {
    const handleScroll = async () => {
      if (
        window.innerHeight + window.scrollY >=
          document.documentElement.scrollHeight - 100 &&
        !loading &&
        hasMore
      ) {
        const nextSkip = skip + LIMIT;
        setSkip(nextSkip);

        try {
          setLoading(true);
          const response = await fetch(
            `http://localhost:8000/clienti/?skip=${nextSkip}&limit=${LIMIT}`,
          );
          if (!response.ok) {
            throw new Error("Errore durante il recupero dei dati");
          }
          const data = await response.json();

          if (data.length < LIMIT) {
            setHasMore(false);
          }

          setSottoscrittori((prev) => [...prev, ...data]);
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [loading, hasMore, skip]);

  if (initialLoading)
    return <div className="p-4 text-center text-gray-500">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-red-500">Errore: {error}</div>;

  return (
    <>
      <div className="max-w-4xl mx-auto my-6 flex justify-between items-center px-2">
        <h3 className="text-xl font-bold text-gray-800">
          Elenco Sottoscrittori
        </h3>
        <button
          onClick={() => navigate("/nuovo")}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none transition-colors cursor-pointer"
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
