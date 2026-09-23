import { useEffect, useState } from "react";
import { queryPratiche } from "../lib/pratiche";
import { caricaPagina } from "../lib/pagineRemote";
import useQueryPagina from "./useQueryPagina.js";
import { QUERY_PRATICHE } from "../config/routes/query.js";

export default function useFiltriPratiche() {
  const [query, aggiornaQuery] = useQueryPagina(QUERY_PRATICHE);
  const {
    ricerca,
    numeroPratica,
    stato,
    universita,
    tipoCorso,
    filtroInterno,
    tipoSelezionato,
  } = query;
  const setRicerca = (ricerca) => aggiornaQuery({ ricerca });
  const setNumeroPratica = (numeroPratica) => aggiornaQuery({ numeroPratica });
  const setStato = (stato) => aggiornaQuery({ stato });
  const setTipoSelezionato = (tipoSelezionato) =>
    aggiornaQuery({ tipoSelezionato });

  const [catalogo, setCatalogo] = useState({
    stati: [],
    tipiCorso: [],
    errore: null,
  });
  const [tentativo, setTentativo] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      caricaPagina("/pratiche/filtri/stati", controller.signal),
      caricaPagina("/listini-tipi-corsi/", controller.signal),
    ])
      .then(([stati, tipiCorso]) => {
        if (!controller.signal.aborted)
          setCatalogo({ stati, tipiCorso, errore: null });
      })
      .catch((errore) => {
        if (!controller.signal.aborted)
          setCatalogo({ stati: [], tipiCorso: [], errore: errore.message });
      });
    return () => controller.abort();
  }, [tentativo]);

  return {
    ricerca,
    setRicerca,
    numeroPratica,
    setNumeroPratica,
    stato,
    setStato,
    ...catalogo,
    universita,
    tipoCorso,
    filtroInterno,
    tipoSelezionato,
    setTipoSelezionato,
    riprova: () => setTentativo((n) => n + 1),
    attivi:
      Number(!!stato) + Number(!!numeroPratica) + Number(!!tipoSelezionato),
    azzera: () =>
      aggiornaQuery({
        stato: "",
        numeroPratica: "",
        tipoSelezionato: "",
      }),
    query: queryPratiche({
      ricerca,
      numeroPratica,
      stato,
      studenti: [],
      universita,
      tipoCorso,
      tipoSelezionato,
    }),
  };
}
