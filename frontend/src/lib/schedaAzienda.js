import { apiFetch, messaggioErrore } from "./api.js";
import { anomaliePerCampo, noteVisibili } from "./anomalieCampi.js";
import { TESTI_ANOMALIE } from "../config/testi/anomalie.js";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";

/*
 * Logica della scheda azienda: sottotitolo, controllo della partita IVA e
 * note per campo, lettura dell'azienda padre.
 */

/**
 * Partita IVA da segnalare mentre si scrive: non vuota e diversa da 11 cifre.
 * E' un avviso, non un blocco: il server rifiuta comunque il salvataggio.
 * @param {unknown} valore
 */
export function pivaNonConforme(valore) {
  const testo = String(valore ?? "");
  return testo !== "" && !/^\d{11}$/.test(testo);
}

/**
 * Nome da mostrare per un'azienda: la ragione sociale oppure "Azienda #id"
 * se il server non la restituisce.
 * @param {{ azienda_id?: number, azienda_ragione_sociale?: string|null }} azienda
 */
export function nomeAzienda(azienda) {
  return azienda?.azienda_ragione_sociale || TESTI_AZIENDA.senzaNome(azienda?.azienda_id);
}

/**
 * Sottotitolo della scheda in modifica: "Ragione sociale · Figlia di Padre".
 * La ragione sociale e' quella letta dal server, non quella che si sta
 * scrivendo. Resta la sola ragione sociale se l'azienda e' radice (padre
 * null) o se il padre e' ancora in caricamento (undefined).
 * @param {string|null|undefined} ragioneSalvata
 * @param {object|null|undefined} padre
 * @returns {string|undefined}  undefined se non c'e' niente da mostrare
 */
export function sottotitoloAzienda(ragioneSalvata, padre) {
  const parti = [String(ragioneSalvata ?? "").trim()];
  if (padre) parti.push(TESTI_AZIENDA.figliaDi(nomeAzienda(padre)));
  return parti.filter(Boolean).join(TESTI_AZIENDA.separatoreSottotitolo) || undefined;
}

/**
 * Note brevi sotto i campi: le anomalie del server sui campi non ancora
 * modificati e, sulla partita IVA, il controllo in tempo reale. Senza
 * anomalie (creazione rapida) resta solo il controllo in tempo reale.
 * @param {string[]|null|undefined} anomalie  frasi di GET /aziende/{id}
 * @param {Record<string, unknown>} valori  valori correnti del modulo
 * @param {Record<string, unknown>} salvati  valori letti dal server
 * @returns {Record<string, string[]>}
 */
export function noteCampiAzienda(anomalie, valori, salvati) {
  const note = noteVisibili(anomaliePerCampo(anomalie, "azienda"), valori, salvati);
  if (pivaNonConforme(valori?.azienda_partitaIVA)) {
    const voci = note.azienda_partitaIVA ?? [];
    if (!voci.includes(TESTI_ANOMALIE.pivaNonConforme)) {
      note.azienda_partitaIVA = [...voci, TESTI_ANOMALIE.pivaNonConforme];
    }
  }
  return note;
}

/**
 * Azienda padre: null se l'azienda e' radice. Se la scheda del padre non si
 * legge resta l'id, senza ragione sociale.
 * @param {string|number} aziendaId
 * @param {AbortSignal} [signal]
 */
export async function caricaPadreAzienda(aziendaId, signal) {
  const risposta = await apiFetch(`/aziende-xcod/${aziendaId}/padre`, { signal });
  if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
  const arco = await risposta.json();
  if (!arco || arco.azienda_padre_id == null) return null;
  const rispostaPadre = await apiFetch(`/aziende/${arco.azienda_padre_id}`, { signal });
  return rispostaPadre.ok
    ? await rispostaPadre.json()
    : { azienda_id: arco.azienda_padre_id, azienda_ragione_sociale: null };
}
