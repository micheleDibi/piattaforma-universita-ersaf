import { apiFetch, leggiJson, messaggioErrore } from "./api.js";
import { opzioneStudente } from "./opzioniPratica.js";
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
export async function caricaSchedaPratica(id, signal) {
  const [pratica, stati, universita] = await Promise.all([
    id ? richiedi(`/pratiche/${id}`, { signal }) : null,
    richiedi("/pratiche/filtri/stati", { signal }),
    richiedi("/listini-testa/opzioni/universita", { signal }),
  ]);
  const emittente = pratica?.cliente_emittente_aderente_id
    ? opzioneStudente(await richiedi(`/clienti/${pratica.cliente_emittente_aderente_id}`, { signal })) : null;
  return { pratica, stati, universita, emittente };
}
export async function salvaPratica(id, payload) {
  const pratica = await richiedi(id ? `/pratiche/${id}` : "/pratiche/",
    { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
  if (!idValido(pratica.pratica_id)) throw new Error("Il servizio non ha restituito l’identificativo della pratica.");
  return pratica;
}
