import { useEffect, useState } from "react";
import { queryPratiche } from "../lib/pratiche";
import { caricaPagina } from "../lib/pagineRemote";
import useQueryPagina from "./useQueryPagina.js";
import useSelezioniUrl from "./useSelezioniUrl.js";
import { QUERY_PRATICHE } from "../config/routes/query.js";
import { opzioneStudente, opzionePercorso } from "../lib/opzioniPratica.js";

export default function useFiltriPratiche() {
  const [query, aggiornaQuery] = useQueryPagina(QUERY_PRATICHE);
  const { ricerca, stato } = query;
  const studenti = useSelezioniUrl(query.studenti, "/clienti", opzioneStudente, "Studente");
  const percorsi = useSelezioniUrl(query.percorso ? [Number(query.percorso)] : [], "/listini-testa", opzionePercorso, "Percorso");
  const percorso = percorsi[0] || null;
  const setRicerca = ricerca => aggiornaQuery({ ricerca });
  const setStato = stato => aggiornaQuery({ stato });
  const setStudenti = studenti => aggiornaQuery({ studenti: studenti.map(item => item.id) });
  const setPercorso = percorso => aggiornaQuery({ percorso: percorso?.id });
  const [catalogo, setCatalogo] = useState({ stati: [], errore: null });
  const [tentativo, setTentativo] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    caricaPagina("/pratiche/filtri/stati", controller.signal)
      .then(stati => { if (!controller.signal.aborted) setCatalogo({ stati, errore: null }); })
      .catch(errore => { if (!controller.signal.aborted) setCatalogo({ stati: [], errore: errore.message }); });
    return () => controller.abort();
  }, [tentativo]);
  return {
    ricerca, setRicerca, stato, setStato, studenti, setStudenti, percorso, setPercorso, ...catalogo,
    riprova: () => setTentativo(n => n + 1),
    attivi: Number(!!stato) + Number(!!studenti.length) + Number(!!percorso),
    azzera: () => aggiornaQuery({ stato: "", studenti: [], percorso: "" }),
    query: queryPratiche({ ricerca, stato, studenti, percorso }),
  };
}
