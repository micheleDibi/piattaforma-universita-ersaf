import { apiFetch, leggiJson, messaggioErrore } from "./api.js";
import { idValido } from "../config/routes/percorsi.js";

async function richiedi(url, opzioni) {
  const risposta = await apiFetch(url, opzioni);
  if (!risposta.ok) {
    const errore = new Error(await messaggioErrore(risposta, "Impossibile caricare la pratica. Riprova."));
    errore.status = risposta.status;
    throw errore;
  }
  const dati = await leggiJson(risposta);
  if (dati === null) throw new Error("Risposta del servizio non valida. Riprova.");
  return dati;
}
export const caricaProdottoPratica = (id, signal) => richiedi(`/listini-testa/${id}`, { signal });

/** Università e tipi di corso scelti nel pannello Pratiche, letti
 * dall'indirizzo di ritorno (?universita=&tipoCorso=, uno o più) che
 * useNavigazioneElenco ricorda in `ritorno`. Puri numeri, senza dover
 * aspettare che le liste di università/tipi di corso siano state scaricate:
 * servono subito a useSchedaPratica per sapere se restringere la selezione
 * del percorso formativo (vedi SchedaPratica.jsx e RelazioniPratica.jsx). */
export function leggiContestoUrl(ritorno) {
  const posizione = ritorno.indexOf("?");
  if (posizione === -1) return { universitaId: null, tipoCorsoIds: [] };
  const parametri = new URLSearchParams(ritorno.slice(posizione + 1));
  const universita = parametri.get("universita");
  return {
    universitaId: universita ? Number(universita) : null,
    tipoCorsoIds: parametri.getAll("tipoCorso").map(Number),
  };
}
export async function caricaSchedaPratica(id, signal) {
  const [pratica, stati, universita, tipiCorso] = await Promise.all([
    id ? richiedi(`/pratiche/${id}`, { signal }) : null,
    richiedi("/pratiche/filtri/stati", { signal }),
    richiedi("/listini-testa/opzioni/universita", { signal }),
    // Solo per il titolo di una pratica nuova (vedi titoloScheda in
    // SchedaPratica.jsx): traduce gli id di ?tipoCorso= nell'indirizzo di
    // provenienza nelle etichette da mostrare.
    richiedi("/listini-tipi-corsi/", { signal }),
  ]);
  return { pratica, stati, universita, tipiCorso };
}
export async function salvaPratica(id, payload) {
  const pratica = await richiedi(id ? `/pratiche/${id}` : "/pratiche/",
    { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
  if (!idValido(pratica.pratica_id)) throw new Error("Il servizio non ha restituito l’identificativo della pratica.");
  return pratica;
}
