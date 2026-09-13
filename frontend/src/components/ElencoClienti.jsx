import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../lib/api";
import { leggiRuolo } from "../lib/sessione";
import IntestazionePagina from "./shared/IntestazionePagina";
import BarraStrumenti from "./shared/BarraStrumenti";
import CampoRicerca from "./shared/CampoRicerca";
import AzioneCrea from "./shared/AzioneCrea";
import AzioneModificaRiga from "./shared/AzioneModificaRiga";
import { campo } from "../config/styles/campo";
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
    <div className={contenutoPagina()}>
      <IntestazionePagina
        titolo={soloAttuatori ? "Attuatori" : "Sottoscrittori"}
        azioni={
          <AzioneCrea
            onClick={() =>
              navigate(
                soloAttuatori
                  ? "/nuovo?tipo=attuatore"
                  : "/nuovo?tipo=sottoscrittore",
              )
            }
            etichetta={soloAttuatori ? "Nuovo attuatore" : "Nuovo sottoscrittore"}
            etichettaBreve="Nuovo"
          />
        }
      />

      <div className={schedaElenco()}>
        <BarraStrumenti>
          <CampoRicerca
            valore={searchTerm}
            onCambia={setSearchTerm}
            segnaposto={
              soloAttuatori
                ? "Cerca per nome, cognome o azienda"
                : "Cerca per nome o cognome"
            }
          />
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
        </BarraStrumenti>

        <div className={scorrimentoTabella()}>
          <table className={tabella()}>
            <thead className={intestazioneTabella()}>
              <tr>
                <th className={cellaIntestazione()}>Nome</th>
                <th className={cellaIntestazione()}>Cognome</th>

                {soloAttuatori && (
                  <th className={cellaIntestazione()}>Ruolo</th>
                )}

                {canSeeAzienda && (
                  <th className={cellaIntestazione()}>Azienda</th>
                )}

                <th className={cellaIntestazione("destra")}>
                  <span className="sr-only">Azioni</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {sottoscrittori.map((item, index) => {
                const apri = () =>
                  navigate(
                    `/modifica/${item.cliente_id}${soloAttuatori ? "?tipo=attuatore" : ""}`,
                  );

                return (
                  <tr
                    key={item.cliente_id || index}
                    className={rigaTabella(true)}
                    onClick={apri}
                  >
                    <td className={cella("forte")}>{item.cliente_nome}</td>
                    <td className={cella("forte")}>{item.cliente_cognome}</td>

                    {soloAttuatori && (
                      <td className={cella("tenue")}>
                        {item.ruolo?.ruolo_codice || "-"}
                      </td>
                    )}

                    {canSeeAzienda && (
                      <td className={cella("tenue")}>
                        {item.azienda?.azienda_ragione_sociale || "-"}
                      </td>
                    )}
                    <td className={cellaAzioni()}>
                      <AzioneModificaRiga onClick={apri} />
                    </td>
                  </tr>
                );
              })}
              {sottoscrittori.length === 0 && !loading && (
                <tr className="border-t border-bordo">
                  <td colSpan={colSpanCount} className={statoVuoto()}>
                    {soloAttuatori
                      ? "Nessun attuatore trovato."
                      : "Nessun sottoscrittore trovato."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loading && (
          <div className="border-t border-bordo px-4 py-3 text-center text-sm text-testo-tenue">
            Caricamento altri elementi...
          </div>
        )}

        {!hasMore && (
          <div className="border-t border-bordo px-4 py-3 text-center text-nota text-testo-tenue">
            Hai raggiunto la fine dell'elenco
          </div>
        )}
      </div>
    </div>
  );
}

export default ElencoClienti;
