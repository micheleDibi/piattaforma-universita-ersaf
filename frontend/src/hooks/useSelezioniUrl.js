import { useEffect, useState } from "react";
import { caricaPagina } from "../lib/pagineRemote.js";

/** La query contiene solo ID; le etichette sono rilette anche aprendo un link condiviso. */
export default function useSelezioniUrl(ids, endpoint, estrai, nome) {
  const chiave = ids.join(",");
  const [opzioni, setOpzioni] = useState({});
  useEffect(() => {
    const controller = new AbortController();
    const identificativi = chiave ? chiave.split(",").map(Number) : [];
    Promise.allSettled(identificativi.map(async id => {
      const opzione = estrai(await caricaPagina(`${endpoint}/${id}`, controller.signal));
      if (!controller.signal.aborted) setOpzioni(attuali => ({ ...attuali, [id]: opzione }));
    }));
    return () => controller.abort();
  }, [chiave, endpoint, estrai]);
  return ids.map(id => opzioni[id] || { id, label: `${nome} ${id}`, dettaglio: "" });
}
