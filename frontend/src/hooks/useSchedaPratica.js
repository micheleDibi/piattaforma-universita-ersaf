import { useEffect, useRef, useState } from "react";
import { caricaProdottoPratica, caricaSchedaPratica, salvaPratica } from "../lib/schedaPratica.js";
import { payloadPratica, praticaVuota, prezzoPerInput } from "../lib/praticaForm.js";

export default function useSchedaPratica(id) {
  const [dati, setDati] = useState(praticaVuota);
  const [catalogo, setCatalogo] = useState({ loading: true, errore: "", stati: [], universita: [] });
  const [tentativo, setTentativo] = useState(0);
  const [studente, setStudente] = useState(null);
  const [percorso, setPercorso] = useState(null);
  const [emittente, setEmittente] = useState(null);
  const [prodotto, setProdotto] = useState(null);
  const [erroreProdotto, setErroreProdotto] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);
  const [messaggio, setMessaggio] = useState(null);
  const invio = useRef(false);
  useEffect(() => {
    const controller = new AbortController();
    caricaSchedaPratica(id, controller.signal).then(({ pratica, emittente, ...opzioni }) => {
      if (controller.signal.aborted) return;
      setCatalogo({ ...opzioni, loading: false, errore: "" });
      if (pratica) {
        setDati({ ...Object.fromEntries(Object.entries(pratica).map(([k, v]) => [k, v ?? ""])),
          pratica_prezzo: prezzoPerInput(pratica.pratica_prezzo) });
        setStudente({ id: pratica.cliente_id, label: pratica.cliente_nome_completo });
        setPercorso({ id: pratica.listTesta_id, label: pratica.listTesta_descrizione });
        setEmittente(emittente);
      }
    }).catch(errore => {
      if (!controller.signal.aborted) setCatalogo({ loading: false, errore: errore.message, status: errore.status, stati: [], universita: [] });
    });
    return () => controller.abort();
  }, [id, tentativo]);

  const percorsoId = percorso?.id;
  useEffect(() => {
    if (id || !percorsoId) return;
    const controller = new AbortController();
    caricaProdottoPratica(percorsoId, controller.signal).then(dati => {
      if (!controller.signal.aborted) { setProdotto(dati); setErroreProdotto(""); }
    }).catch(errore => { if (!controller.signal.aborted) setErroreProdotto(errore.message); });
    return () => controller.abort();
  }, [id, percorsoId]);
  const aggiorna = evento => setDati(attuali => ({ ...attuali, [evento.target.name]: evento.target.value }));
  const salva = async () => {
    if (invio.current) return null;
    invio.current = true;
    setSalvataggio(true);
    setMessaggio(null);
    try {
      const payload = payloadPratica(dati, { nuova: !id, studente, percorso, emittente, prodotto });
      const pratica = await salvaPratica(id, payload);
      setMessaggio({ type: "success", text: "Pratica salvata." });
      return pratica;
    } catch (errore) { setMessaggio({ type: "error", text: errore.message }); return null; }
    finally { invio.current = false; setSalvataggio(false); }
  };
  const universitaId = id ? dati.nome_universita_id : prodotto && prodotto.listTesta_id === percorsoId ? prodotto.nome_universita_id : null;
  return { dati, aggiorna, ...catalogo, messaggio, salvataggio, salva, studente, setStudente,
    percorso, setPercorso, emittente, setEmittente, erroreProdotto,
    universitaLabel: catalogo.universita.find(item => item.id === universitaId)?.descrizione,
    riprova: () => setTentativo(n => n + 1) };
}
