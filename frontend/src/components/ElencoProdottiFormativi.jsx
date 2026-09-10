import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";

export default function ElencoProdottiFormativi() {
  const navigate = useNavigate();

  const [prodotti, setProdotti] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);
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
          fetch("http://localhost:8000/listini-testa/opzioni/universita"),
          fetch("http://localhost:8000/listini-testa/opzioni/tipi-corso"),
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
    return <div className="p-4 text-center text-gray-500">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-red-500">Errore: {error}</div>;

  return (
    <div className="w-full p-6">
      <div className="w-full my-6 flex flex-col sm:flex-row justify-between items-center gap-4 px-2">
        <h3 className="text-xl font-bold text-gray-800">
          Elenco Prodotti Formativi:
        </h3>

        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto items-center">
          <div className="w-full sm:w-72">
            <input
              type="text"
              placeholder="Cerca per titolo o codice..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm text-gray-700"
            />
          </div>
          <button
            type="button"
            onClick={handleNuovo}
            className="w-full sm:w-auto px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors whitespace-nowrap cursor-pointer"
          >
            Nuovo Prodotto
          </button>
        </div>
      </div>

      {/* Filtri a tendina */}
      <div className="flex flex-wrap gap-3 mb-6 px-2">
        <select
          value={filtroUniversita}
          onChange={(e) => setFiltroUniversita(e.target.value)}
          className="w-full sm:w-60 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm bg-white text-gray-700"
        >
          <option value="Tutte le università">Tutte le università</option>
          {universitaList.map((uni) => (
            <option key={uni.id} value={uni.descrizione}>
              {uni.descrizione}
            </option>
          ))}
        </select>

        <select
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
          className="w-full sm:w-60 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm bg-white text-gray-700"
        >
          <option value="Tutti i tipi">Tutti i tipi</option>
          {tipiList.map((tipo) => (
            <option key={tipo.id} value={tipo.descrizione}>
              {tipo.descrizione}
            </option>
          ))}
        </select>

        <select
          value={filtroAttivo}
          onChange={(e) => setFiltroAttivo(e.target.value)}
          className="w-full sm:w-40 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm bg-white text-gray-700"
        >
          <option value="Tutti">Attivo: Tutti</option>
          <option value="Sì">Attivo: Sì</option>
          <option value="No">Attivo: No</option>
        </select>
      </div>

      {/* Tabella o messaggio nessun risultato */}
      {prodotti.length === 0 && !loading ? (
        <div className="w-full bg-white shadow-md rounded-lg p-8 text-center text-gray-500 text-sm border border-gray-200">
          Nessun risultato trovato per i filtri di ricerca selezionati.
        </div>
      ) : (
        <div className="w-full bg-white shadow-md rounded-lg overflow-hidden border border-gray-200 my-6">
          <table className="min-w-full divide-y divide-gray-200 text-left">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase">
                  Università
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase">
                  Codice
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase">
                  Titolo
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase">
                  Tipo Prodotto
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase">
                  Attivo
                </th>
                <th className="px-6 py-3 text-xs font-semibold text-gray-700 uppercase text-right">
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
                    className="hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {item.nome_universita || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {item.listTesta_codice}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-800">
                      {item.listTesta_descrizione}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {item.listino_tipoCorso_descrizione || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${isAttivo ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}
                      >
                        {isAttivo ? "Sì" : "No"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        type="button"
                        onClick={() => handleModifica(item.listTesta_id)}
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 transition-colors cursor-pointer"
                      >
                        Modifica
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Indicatore di caricamento o fine lista */}
      {loading && (
        <div className="text-center py-4 text-gray-500 text-sm">
          Caricamento altri elementi...
        </div>
      )}

      {!hasMore && prodotti.length > 0 && (
        <div className="text-center py-6 text-gray-400 text-xs italic">
          Hai raggiunto la fine della lista. Non ci sono altri risultati.
        </div>
      )}
    </div>
  );
}
