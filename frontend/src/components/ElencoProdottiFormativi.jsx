import { useState, useEffect, useRef } from "react";

export default function ElencoProdottiFormativi() {
  const [prodotti, setProdotti] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
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
    console.log("Modifica prodotto con id:", id);
  };

  const fetchProdottiFiltrati = async (
    searchVal,
    uniVal,
    tipoVal,
    attivoVal,
  ) => {
    try {
      setLoading(true);
      loadingRef.current = true;
      setSkip(0);
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

      const response = await fetch(
        `http://localhost:8000/listini-testa/?skip=0&limit=${LIMIT}${searchParam}${uniParam}${tipoParam}${attivoParam}`,
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
          document.documentElement.scrollHeight - 100 &&
        !loadingRef.current &&
        hasMoreRef.current
      ) {
        setLoading(true);
        loadingRef.current = true;

        const nextSkip = skipRef.current + LIMIT;
        setSkip(nextSkip);
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

          const response = await fetch(
            `http://localhost:8000/listini-testa/?skip=${nextSkip}&limit=${LIMIT}${searchParam}${uniParam}${tipoParam}${attivoParam}`,
          );
          if (!response.ok) {
            throw new Error("Errore durante il recupero dei dati");
          }
          const data = await response.json();

          if (data.length < LIMIT) {
            setHasMore(false);
            hasMoreRef.current = false;
          }

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
    return <div className="p-4 text-center text-gray-500">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-red-500">Errore: {error}</div>;

  const universitaList = [
    "Tutte le università",
    ...new Set(prodotti.map((p) => p.nome_universita).filter(Boolean)),
  ];
  const tipiList = [
    "Tutti i tipi",
    ...new Set(
      prodotti.map((p) => p.listino_tipoCorso_descrizione).filter(Boolean),
    ),
  ];

  return (
    <div className="w-full p-6">
      <div className="w-full my-6 flex flex-col sm:flex-row justify-between items-center gap-4 px-2">
        <h3 className="text-xl font-bold text-gray-800">
          Elenco Prodotti Formativi:
        </h3>

        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <div className="w-full sm:w-72">
            <input
              type="text"
              placeholder="Cerca per titolo o codice..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-700"
            />
          </div>
        </div>

        <button
          type="button"
          onClick={() => console.log("Nuovo prodotto")}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none transition-colors cursor-pointer whitespace-nowrap"
        >
          Nuovo Prodotto
        </button>
      </div>

      <div className="flex flex-wrap gap-3 mb-6 px-2">
        <select
          value={filtroUniversita}
          onChange={(e) => setFiltroUniversita(e.target.value)}
          className="w-full sm:w-60 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-white text-gray-700"
        >
          {universitaList.map((uni, idx) => (
            <option key={idx} value={uni}>
              {uni}
            </option>
          ))}
        </select>

        <select
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
          className="w-full sm:w-60 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-white text-gray-700"
        >
          {tipiList.map((tipo, idx) => (
            <option key={idx} value={tipo}>
              {tipo}
            </option>
          ))}
        </select>

        <select
          value={filtroAttivo}
          onChange={(e) => setFiltroAttivo(e.target.value)}
          className="w-full sm:w-40 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-white text-gray-700"
        >
          <option value="Tutti">Attivo: Tutti</option>
          <option value="Sì">Attivo: Sì</option>
          <option value="No">Attivo: No</option>
        </select>
      </div>

      <div className="w-full bg-white shadow-md rounded-lg overflow-hidden border border-gray-200 my-6">
        <table className="min-w-full divide-y divide-gray-200 text-left">
          <thead className="bg-gray-100 sticky top-0 z-10">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Università
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Codice / SSID
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Titolo
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Tipo Prodotto
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Attivo
              </th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider text-right">
                Modifica
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {prodotti.map((item, index) => {
              const isAttivo = item.listino_attivoSN === -1;
              return (
                <tr
                  key={item.listTesta_id || index}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.nome_universita || "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {item.listTesta_codice}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800">
                    {item.listTesta_descrizione}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {item.listino_tipoCorso_descrizione || "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${
                        isAttivo
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {isAltivoSino(isAttivo)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      type="button"
                      onClick={() => handleModifica(item.listTesta_id)}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none transition-colors cursor-pointer"
                    >
                      Modifica
                    </button>
                  </td>
                </tr>
              );
            })}
            {prodotti.length === 0 && !loading && (
              <tr>
                <td
                  colSpan="6"
                  className="px-6 py-8 text-center text-sm text-gray-500"
                >
                  Nessun prodotto trovato.
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

        {!hasMore && prodotti.length > 0 && (
          <div className="py-4 text-center text-xs text-gray-400 bg-gray-50">
            Hai raggiunto la fine dell'elenco
          </div>
        )}
      </div>
    </div>
  );
}

function isAltivoSino(isAttivo) {
  return isAttivo ? "Sì" : "No";
}
