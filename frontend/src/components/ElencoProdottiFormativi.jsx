import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";
import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import {
  contenitoreTabella,
  intestazioneTabella,
  rigaTabella,
  scheda,
} from "../config/styles/superficie";

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
          apiFetch(`/listini-testa/opzioni/universita`),
          apiFetch(`/listini-testa/opzioni/tipi-corso`),
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

      const response = await apiFetch(
        `/listini-testa/?skip=0&limit=${LIMIT}${searchParam}${uniParam}${tipoParam}${attivoParam}`,
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

          const response = await apiFetch(
            `/listini-testa/?skip=${nextSkip}&limit=${LIMIT}${searchParam}${uniParam}${tipoParam}${attivoParam}`,
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
    return <div className="p-4 text-center text-testo-tenue">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-negativo">Errore: {error}</div>;

  return (
    <div className="w-full p-6">
      <div className="w-full my-6 flex flex-col sm:flex-row justify-between items-center gap-4 px-2">
        <h3 className="text-xl font-bold text-testo">
          Elenco Prodotti Formativi:
        </h3>

        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto items-center">
          <div className="w-full sm:w-72">
            <input
              type="text"
              placeholder="Cerca per titolo o codice..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={campo()}
            />
          </div>
          <button
            type="button"
            onClick={handleNuovo}
            className={`${pulsante()} w-full sm:w-auto whitespace-nowrap`}
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
          className={`${campo()} sm:w-60`}
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
          className={`${campo()} sm:w-60`}
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
          className={`${campo()} sm:w-40`}
        >
          <option value="Tutti">Attivo: Tutti</option>
          <option value="Sì">Attivo: Sì</option>
          <option value="No">Attivo: No</option>
        </select>
      </div>

      {/* Tabella o messaggio nessun risultato */}
      {prodotti.length === 0 && !loading ? (
        <div className={`${scheda()} w-full p-8 text-center text-testo-tenue text-sm`}>
          Nessun risultato trovato per i filtri di ricerca selezionati.
        </div>
      ) : (
        <div className={`${contenitoreTabella()} my-6`}>
          <table className="min-w-full text-left">
            <thead className={intestazioneTabella()}>
              <tr>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Università
                </th>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Codice
                </th>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Titolo
                </th>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Tipo Prodotto
                </th>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider">
                  Attivo
                </th>
                <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wider text-right">
                  Modifica
                </th>
              </tr>
            </thead>
            <tbody className="bg-superficie">
              {prodotti.map((item, index) => {
                const isAttivo = item.listino_attivoSN === -1;
                return (
                  <tr
                    key={item.listTesta_id || index}
                    className={rigaTabella()}
                  >
                    <td className="px-6 py-4 text-sm font-medium text-testo-forte">
                      {item.nome_universita || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm text-testo-tenue">
                      {item.listTesta_codice}
                    </td>
                    <td className="px-6 py-4 text-sm text-testo">
                      {item.listTesta_descrizione}
                    </td>
                    <td className="px-6 py-4 text-sm text-testo-tenue">
                      {item.listino_tipoCorso_descrizione || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`px-2 py-1 rounded-controllo text-xs font-semibold ${isAttivo ? "bg-positivo/10 text-positivo" : "bg-superficie-alta text-testo-tenue"}`}
                      >
                        {isAttivo ? "Sì" : "No"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        type="button"
                        onClick={() => handleModifica(item.listTesta_id)}
                        className={pulsante("primario", "piccolo")}
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
        <div className="text-center py-4 text-testo-tenue text-sm">
          Caricamento altri elementi...
        </div>
      )}

      {!hasMore && prodotti.length > 0 && (
        <div className="text-center py-6 text-testo-tenue text-nota italic">
          Hai raggiunto la fine della lista. Non ci sono altri risultati.
        </div>
      )}
    </div>
  );
}
