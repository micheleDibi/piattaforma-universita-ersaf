import { useEffect, useState } from "react";
import { queryConteggiNazionale, queryPraticheNazionale, statiNazionale } from "../lib/pratiche";
import { caricaPagina } from "../lib/pagineRemote";
import useQueryPagina from "./useQueryPagina.js";
import { QUERY_PRATICHE } from "../config/routes/query.js";

/** Filtri dell'elenco del Nazionale: sottoscrittore, codice pratica, stato e
 * universita' (quest'ultima dai loghi degli atenei, non dal pannello Filtri).
 * Stessi parametri dell'indirizzo dell'elenco degli altri ruoli
 * (QUERY_PRATICHE), cosi' un collegamento con ?universita= seleziona il logo. */
export default function useFiltriPraticheNazionale() {
  const [query, aggiornaQuery] = useQueryPagina(QUERY_PRATICHE);
  const { ricerca, numeroPratica, stato, universita, tipoCorso, filtroInterno, tipoSelezionato } = query;

  // Il tipo di corso non e' un filtro di questo elenco. Si toglie
  // dall'indirizzo perche' la scheda pratica lo legge dall'indirizzo di
  // ritorno (leggiContestoUrl) e lo prenderebbe per il tipo della pratica.
  const contestoEstraneo = tipoCorso.length > 0 || Boolean(filtroInterno) || Boolean(tipoSelezionato);
  useEffect(() => {
    if (contestoEstraneo) aggiornaQuery({ tipoCorso: [], filtroInterno: "", tipoSelezionato: "" });
  }, [contestoEstraneo, aggiornaQuery]);

  const [catalogo, setCatalogo] = useState({ stati: [], errore: null });
  const [tentativo, setTentativo] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    caricaPagina("/pratiche/filtri/stati", controller.signal)
      .then((stati) => {
        if (!controller.signal.aborted) setCatalogo({ stati: statiNazionale(stati), errore: null });
      })
      .catch((errore) => {
        if (!controller.signal.aborted) setCatalogo({ stati: [], errore: errore.message });
      });
    return () => controller.abort();
  }, [tentativo]);

  const filtri = { ricerca, numeroPratica, stato, universita };
  return {
    ...filtri,
    ...catalogo,
    setRicerca: (valore) => aggiornaQuery({ ricerca: valore }),
    setNumeroPratica: (valore) => aggiornaQuery({ numeroPratica: valore }),
    setStato: (valore) => aggiornaQuery({ stato: valore }),
    setUniversita: (valore) => aggiornaQuery({ universita: valore }),
    riprova: () => setTentativo((n) => n + 1),
    // L'universita' non e' nel pannello Filtri: non si conta e "Azzera
    // filtri" non la toglie.
    attivi: Number(!!stato) + Number(!!numeroPratica),
    // Ne' ricerca ne' filtri: l'elenco mostra un solo gruppo (gruppoUnico).
    senzaFiltri: !ricerca.trim() && !stato && !numeroPratica.trim() && !universita,
    azzera: () => aggiornaQuery({ stato: "", numeroPratica: "" }),
    query: queryPraticheNazionale(filtri),
    queryConteggi: queryConteggiNazionale(filtri),
  };
}
