import { useEffect, useRef, useState } from "react";
import { caricaProdottoPratica, caricaSchedaPratica, salvaPratica } from "../lib/schedaPratica.js";
import { payloadPratica, praticaVuota, prezzoAttuale, prezzoPerInput, sommaPrezzi } from "../lib/praticaForm.js";

const NESSUN_PREZZO_ATTIVO = "Il percorso formativo scelto non ha un prezzo attivo.";

export default function useSchedaPratica(id, { corsiSingoli = false } = {}) {
  const [dati, setDati] = useState(praticaVuota);
  const [catalogo, setCatalogo] = useState({ loading: true, errore: "", stati: [], universita: [], tipiCorso: [] });
  const [tentativo, setTentativo] = useState(0);
  const [studente, setStudente] = useState(null);
  const [percorso, setPercorso] = useState(null);
  // Solo per Corsi Singoli: tutti i corsi scelti (percorso e' sempre il
  // primo di questo elenco, vedi setPercorsi). Per gli altri tipi di corso
  // resta vuoto: non serve, percorso basta.
  const [corsiSelezionati, setCorsiSelezionati] = useState([]);
  const setPercorsi = (scelti) => { setPercorso(scelti[0] ?? null); setCorsiSelezionati(scelti); };
  const [prodotto, setProdotto] = useState(null);
  const [erroreProdotto, setErroreProdotto] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);
  const [messaggio, setMessaggio] = useState(null);
  const invio = useRef(false);
  useEffect(() => {
    const controller = new AbortController();
    caricaSchedaPratica(id, controller.signal).then(({ pratica, ...opzioni }) => {
      if (controller.signal.aborted) return;
      setCatalogo({ ...opzioni, loading: false, errore: "" });
      if (pratica) {
        setDati({ ...Object.fromEntries(Object.entries(pratica).map(([k, v]) => [k, v ?? ""])),
          pratica_prezzo: prezzoPerInput(pratica.pratica_prezzo) });
        setStudente({ id: pratica.cliente_id, label: pratica.cliente_nome_completo });
        setPercorso({ id: pratica.listTesta_id, label: pratica.listTesta_descrizione });
      }
    }).catch(errore => {
      if (!controller.signal.aborted) setCatalogo({ loading: false, errore: errore.message, status: errore.status, stati: [], universita: [], tipiCorso: [] });
    });
    return () => controller.abort();
  }, [id, tentativo]);

  const percorsoId = percorso?.id;
  // Reset sincrono durante il render (non in un effetto, come
  // aziendaIdMostrata in SchedaAziendaAttuatori.jsx): se il percorso viene
  // tolto, prodotto e prezzo del percorso precedente non devono restare.
  const [percorsoIdVisto, setPercorsoIdVisto] = useState(percorsoId);
  if (percorsoId !== percorsoIdVisto) {
    setPercorsoIdVisto(percorsoId);
    if (!percorsoId) {
      setProdotto(null);
      setErroreProdotto("");
      setDati(attuali => ({ ...attuali, pratica_prezzo: "" }));
    }
  }
  useEffect(() => {
    // Il percorso si carica anche in modifica, non solo in creazione: serve
    // a mostrare le caratteristiche del percorso (CaratteristichePercorso.jsx)
    // anche per una pratica gia' salvata.
    if (!percorsoId) return;
    const controller = new AbortController();
    caricaProdottoPratica(percorsoId, controller.signal).then(prodottoCaricato => {
      if (controller.signal.aborted) return;
      setProdotto(prodottoCaricato);
      if (id || corsiSingoli) return;
      // Il prezzo non si digita piu': arriva dal prezzo attuale del percorso
      // formativo, cioe' il dettaglio del listino valido oggi. Solo in
      // creazione: in modifica pratica_prezzo resta quello storico della
      // pratica, non quello (magari cambiato nel frattempo) del percorso.
      // Per Corsi Singoli il prezzo e' la somma dei corsi scelti (vedi
      // l'effetto sotto), non solo quello del primo: qui non si tocca.
      const prezzo = prezzoAttuale(prodottoCaricato.dettagli);
      setErroreProdotto(prezzo === null ? NESSUN_PREZZO_ATTIVO : "");
      setDati(attuali => ({ ...attuali, pratica_prezzo: prezzo === null ? "" : prezzoPerInput(String(prezzo)) }));
    }).catch(errore => { if (!controller.signal.aborted) setErroreProdotto(errore.message); });
    return () => controller.abort();
  }, [id, percorsoId, corsiSingoli]);
  // Corsi Singoli: il prezzo e' la somma dei prezzi correnti di tutti i corsi
  // scelti (ognuno gia' calcolato da opzionePercorsoConDettaglio nel modale),
  // non il prezzo di uno solo. Reset sincrono durante il render, stesso
  // motivo di percorsoIdVisto sopra: solo in creazione.
  const chiaveCorsi = corsiSelezionati.map(corso => `${corso.id}:${corso.prezzo}`).join("|");
  const [chiaveCorsiVista, setChiaveCorsiVista] = useState(chiaveCorsi);
  if (corsiSingoli && !id && chiaveCorsi !== chiaveCorsiVista) {
    setChiaveCorsiVista(chiaveCorsi);
    const somma = sommaPrezzi(corsiSelezionati.map(corso => corso.prezzo));
    setDati(attuali => ({ ...attuali,
      pratica_prezzo: corsiSelezionati.length ? somma : "" }));
  }
  const aggiorna = evento => setDati(attuali => ({ ...attuali, [evento.target.name]: evento.target.value }));
  const salva = async () => {
    if (invio.current) return null;
    invio.current = true;
    setSalvataggio(true);
    setMessaggio(null);
    try {
      const payload = payloadPratica(dati, { nuova: !id, studente, percorso, prodotto, corsiSingoli, corsiSelezionati });
      const pratica = await salvaPratica(id, payload);
      setMessaggio({ type: "success", text: "Pratica salvata." });
      return pratica;
    } catch (errore) { setMessaggio({ type: "error", text: errore.message }); return null; }
    finally { invio.current = false; setSalvataggio(false); }
  };
  const universitaId = id ? dati.nome_universita_id : prodotto && prodotto.listTesta_id === percorsoId ? prodotto.nome_universita_id : null;
  return { dati, aggiorna, ...catalogo, messaggio, salvataggio, salva, studente, setStudente,
    percorso, corsiSelezionati, setPercorsi, prodotto, erroreProdotto,
    universitaLabel: catalogo.universita.find(item => item.id === universitaId)?.descrizione,
    // Stato di una pratica nuova: fisso su "Bozza", non scelto dall'utente.
    statoIniziale: catalogo.stati?.find(stato => stato.label === "Bozza"),
    riprova: () => setTentativo(n => n + 1) };
}
