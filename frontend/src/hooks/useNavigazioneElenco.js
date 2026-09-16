import { useLocation, useNavigate } from "react-router";

/** Il ritorno dal dettaglio ripristina esattamente la ricerca dell'elenco. */
export default function useNavigazioneElenco(elenco) {
  const location = useLocation();
  const navigate = useNavigate();
  const precedente = location.state?.elenco;
  const ritorno = typeof precedente === "string" &&
    (precedente === elenco || precedente.startsWith(`${elenco}?`)) ? precedente : elenco;
  const apri = percorso => navigate(percorso, { state: { elenco: location.pathname + location.search } });
  return { apri, ritorno };
}
