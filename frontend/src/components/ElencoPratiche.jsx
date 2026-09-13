import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";
import IntestazionePagina from "./shared/IntestazionePagina";
import AzioneCrea from "./shared/AzioneCrea";
import AzioneModificaRiga from "./shared/AzioneModificaRiga";
import BarraStrumenti from "./shared/BarraStrumenti";
import CampoRicerca from "./shared/CampoRicerca";
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
    return <div className="p-4 text-center text-testo-tenue">Caricamento...</div>;
  if (error)
    return <div className="p-4 text-center text-negativo">Errore: {error}</div>;

  return (
    <div className={contenutoPagina()}>
      <IntestazionePagina
        titolo="Pratiche"
        azioni={
          <AzioneCrea
            onClick={() => navigate("/nuova-pratica")}
            etichetta="Nuova pratica"
            etichettaBreve="Nuova"
          />
        }
      />

      <div className={schedaElenco()}>
        <BarraStrumenti>
          <CampoRicerca
            valore={searchTerm}
            onCambia={setSearchTerm}
            segnaposto="Cerca per numero pratica"
          />
        </BarraStrumenti>

        <div className={scorrimentoTabella()}>
          <table className={tabella()}>
            <thead className={intestazioneTabella()}>
              <tr>
                <th className={cellaIntestazione()}>Numero</th>
                <th className={cellaIntestazione()}>Cliente</th>
                <th className={cellaIntestazione()}>Corso</th>
                <th className={cellaIntestazione()}>Stato</th>
                <th className={cellaIntestazione("destra")}>
                  <span className="sr-only">Azioni</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {pratiche.map((item, index) => {
                const apri = () =>
                  navigate(`/modifica-pratica/${item.pratica_id}`);

                return (
                  <tr
                    key={item.pratica_id || index}
                    className={rigaTabella(true)}
                    onClick={apri}
                  >
                    <td className={cella("forte")}>
                      {item.pratica_numero || "-"}
                    </td>
                    <td className={cella("forte")}>
                      {item.cliente_nome_completo || "-"}
                    </td>
                    <td className={cella("tenue")}>
                      {item.listTesta_descrizione || "-"}
                    </td>
                    <td className={cella("tenue")}>
                      {item.pratica_stato_descrizione || "-"}
                    </td>
                    <td className={cellaAzioni()}>
                      <AzioneModificaRiga onClick={apri} />
                    </td>
                  </tr>
                );
              })}
              {pratiche.length === 0 && !loading && (
                <tr className="border-t border-bordo">
                  <td colSpan={5} className={statoVuoto()}>
                    Nessuna pratica trovata.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loading && (
          <div className="border-t border-bordo bg-superficie-tenue py-4 text-center text-sm text-testo-tenue">
            Caricamento altri elementi...
          </div>
        )}

        {!hasMore && (
          <div className="border-t border-bordo bg-superficie-tenue py-4 text-center text-nota text-testo-tenue">
            Hai raggiunto la fine dell'elenco
          </div>
        )}
      </div>
    </div>
  );
}

export default ElencoPratiche;
