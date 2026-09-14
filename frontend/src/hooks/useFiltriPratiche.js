import { useEffect, useState } from "react";
import { queryPratiche } from "../lib/pratiche";
import { caricaPagina } from "../lib/pagineRemote";

export default function useFiltriPratiche() {
  const [ricerca, setRicerca] = useState("");
  const [stato, setStato] = useState("");
  const [studenti, setStudenti] = useState([]);
  const [percorso, setPercorso] = useState(null);
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
    azzera: () => { setStato(""); setStudenti([]); setPercorso(null); },
    query: queryPratiche({ ricerca, stato, studenti, percorso }),
  };
}
