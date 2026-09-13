import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { Plus } from "lucide-react";
import { apiFetch } from "../lib/api";
import IntestazionePagina from "./shared/IntestazionePagina";
import BarraStrumenti from "./shared/BarraStrumenti";
import CampoRicerca from "./shared/CampoRicerca";
import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { contenutoPagina } from "../config/styles/pagina";
import {
  cella,
  cellaAzioni,
  cellaIntestazione,
  intestazioneTabella,
  rigaTabella,
  schedaElenco,
  scorrimentoTabella,
  statoVuoto,
  tabella,
} from "../config/styles/tabella";

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
    <div className={contenutoPagina()}>
      <IntestazionePagina
        titolo="Prodotti formativi"
        azioni={
          <button type="button" onClick={handleNuovo} className={pulsante()}>
            <Plus aria-hidden="true" className="size-icona-piccola" />
            Nuovo prodotto
          </button>
        }
      />

      <div className={schedaElenco()}>
        {/* Ricerca e filtri a tendina */}
        <BarraStrumenti>
          <CampoRicerca
            valore={searchTerm}
            onCambia={setSearchTerm}
            segnaposto="Cerca per titolo o codice"
          />

          <select
            value={filtroUniversita}
            onChange={(e) => setFiltroUniversita(e.target.value)}
            className={`${campo()} sm:w-56`}
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
            className={`${campo()} sm:w-56`}
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
        </BarraStrumenti>

        {/* Tabella o messaggio nessun risultato */}
        {prodotti.length === 0 && !loading ? (
          <div className={statoVuoto()}>
            Nessun risultato trovato per i filtri di ricerca selezionati.
          </div>
        ) : (
          <div className={scorrimentoTabella()}>
            <table className={tabella()}>
              <thead className={intestazioneTabella()}>
                <tr>
                  <th className={cellaIntestazione()}>Università</th>
                  <th className={cellaIntestazione()}>Codice</th>
                  <th className={cellaIntestazione()}>Titolo</th>
                  <th className={cellaIntestazione()}>Tipo Prodotto</th>
                  <th className={cellaIntestazione()}>Attivo</th>
                  <th className={cellaIntestazione("destra")}>
                    <span className="sr-only">Azioni</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {prodotti.map((item, index) => {
                  const isAttivo = item.listino_attivoSN === -1;
                  return (
                    <tr
                      key={item.listTesta_id || index}
                      className={rigaTabella()}
                    >
                      <td className={cella("tenue")}>
                        {item.nome_universita || "-"}
                      </td>
                      <td className={cella("forte")}>
                        {item.listTesta_codice}
                      </td>
                      <td className={cella("forte")}>
                        {item.listTesta_descrizione}
                      </td>
                      <td className={cella("tenue")}>
                        {item.listino_tipoCorso_descrizione || "-"}
                      </td>
                      <td className={cella()}>
                        <span
                          className={`px-2 py-1 rounded-controllo text-xs font-semibold ${isAttivo ? "bg-positivo/10 text-positivo" : "bg-superficie-alta text-testo-tenue"}`}
                        >
                          {isAttivo ? "Sì" : "No"}
                        </span>
                      </td>
                      <td className={cellaAzioni()}>
                        <button
                          type="button"
                          onClick={() => handleModifica(item.listTesta_id)}
                          className={pulsante("secondario", "piccolo")}
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
          <div className="border-t border-bordo px-4 py-4 text-center text-sm text-testo-tenue">
            Caricamento altri elementi...
          </div>
        )}

        {!hasMore && prodotti.length > 0 && (
          <div className="border-t border-bordo px-4 py-4 text-center text-nota italic text-testo-tenue">
            Hai raggiunto la fine della lista. Non ci sono altri risultati.
          </div>
        )}
      </div>
    </div>
  );
}
