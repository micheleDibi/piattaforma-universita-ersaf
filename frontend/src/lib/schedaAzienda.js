import { apiFetch, leggiJson, messaggioErrore } from "./api.js";
import { descriviErrore } from "./erroriApi.js";
import { anomaliePerCampo, noteVisibili } from "./anomalieCampi.js";
import { TESTI_ANOMALIE } from "../config/testi/anomalie.js";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";
import { CAMPI_PERCENTUALI, CONVENZIONI } from "../config/campiPercentuali.js";

const ORDINE_PERCENTUALE = Object.fromEntries(CAMPI_PERCENTUALI.map(([chiave], indice) => [chiave, indice]));
const ETICHETTA_PERCENTUALE = Object.fromEntries(CAMPI_PERCENTUALI);
// L'ateneo di ogni campo percentuale (senza la tipologia: "eCampus", non
// "eCampus - Lauree"), per il messaggio di conferma dell'azzeramento.
const ATENEO_PER_CAMPO = Object.fromEntries(
  CONVENZIONI.flatMap(([ateneo, ...campi]) => campi.filter(Boolean).map((campo) => [campo, ateneo])),
);

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

/**
 * Percentuali delle convenzioni universitarie di un'azienda (GET
 * /aziende/{id}/dettagli). Usata sia in sola lettura (scheda dell'attuatore)
 * sia in scrittura (scheda dell'azienda, vedi useDettaglioConvenzioni).
 * @param {string|number} aziendaId
 * @param {AbortSignal} [signal]
 */
export async function caricaDettaglioConvenzioni(aziendaId, signal) {
  const risposta = await apiFetch(`/aziende/${aziendaId}/dettagli`, { signal });
  if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
  return risposta.json();
}

/**
 * Salva le percentuali delle convenzioni universitarie (PUT
 * /aziende/{id}/dettagli). Un valore sopra quello dell'azienda padre e' un
 * errore (422, vedi messaggioSuperamento). Se cambiarle azzererebbe delle
 * convenzioni a cascata sulle aziende figlie, il server risponde 409 finche' non si
 * ripete la richiesta con `conferma: true`; `reset` e' l'elenco (per
 * azienda coinvolta) dei campi che verrebbero azzerati, vedi
 * messaggioAzzeramento per come diventa il testo dell'avviso.
 * @param {string|number} aziendaId
 * @param {Record<string, number>} valori
 * @param {{ conferma?: boolean }} [opzioni]
 * @returns {Promise<
 *   { esito: "ok", dettaglio: object } |
 *   { esito: "richiedeConferma", reset: Array<{ azienda_id: number, azienda_ragione_sociale: string|null, campi: string[] }> }
 * >}
 */
export async function salvaDettaglioConvenzioni(aziendaId, valori, { conferma = false } = {}) {
  const query = conferma ? "?conferma_reset=true" : "";
  const risposta = await apiFetch(`/aziende/${aziendaId}/dettagli${query}`, {
    method: "PUT",
    body: JSON.stringify(valori),
  });
  if (risposta.status === 409) return { esito: "richiedeConferma", reset: (await leggiJson(risposta))?.reset ?? [] };
  if (!risposta.ok) {
    const dati = await leggiJson(risposta);
    const superamenti = dati?.detail?.superamenti;
    throw new Error(superamenti?.length
      ? messaggioSuperamento(superamenti)
      : descriviErrore(risposta, dati, "Si è verificato un errore."));
  }
  return { esito: "ok", dettaglio: await leggiJson(risposta) };
}

/**
 * L'errore del salvataggio quando una percentuale supera quella dell'azienda
 * padre (422 con `detail.superamenti`): niente azzeramento proposto, solo
 * quali campi correggere e il massimo ammesso per ciascuno.
 * @param {Array<{ campo: string, limite: number }>} superamenti
 */
export function messaggioSuperamento(superamenti) {
  const voci = [...superamenti]
    .sort((a, b) => ORDINE_PERCENTUALE[a.campo] - ORDINE_PERCENTUALE[b.campo])
    .map(({ campo, limite }) => `${ETICHETTA_PERCENTUALE[campo] ?? campo} (massimo ${limite}%)`);
  return `Le percentuali non possono superare quelle dell'azienda padre. Correggi: ${voci.join(", ")}.`;
}

/**
 * Il testo della conferma nel salvataggio delle percentuali: qui `reset`
 * contiene solo aziende figlie (i superamenti dell'azienda stessa sono un
 * errore, vedi messaggioSuperamento), quindi le nomina insieme agli atenei.
 * @param {Array<{ azienda_ragione_sociale: string|null, azienda_id: number, campi: string[] }>} reset
 */
export function messaggioAzzeramentoFiglie(reset) {
  const lista = (voci) => new Intl.ListFormat("it", { style: "long", type: "conjunction" }).format(voci);
  const chiavi = [...new Set(reset.flatMap((voce) => voce.campi))]
    .sort((a, b) => ORDINE_PERCENTUALE[a] - ORDINE_PERCENTUALE[b]);
  const atenei = [...new Set(chiavi.map((chiave) => ATENEO_PER_CAMPO[chiave] ?? chiave))];
  const aziende = [...new Set(reset.map((voce) => voce.azienda_ragione_sociale || `azienda ${voce.azienda_id}`))];
  return `I nuovi valori sono più bassi di quelli di ${aziende.length > 1 ? "alcune aziende figlie" : "un'azienda figlia"}: `
    + `le percentuali di ${lista(atenei)} di ${lista(aziende)} verranno azzerate. Continuare?`;
}

/**
 * Il testo dell'avviso di conferma prima di un azzeramento a cascata: elenca
 * gli atenei coinvolti invece del generico "Alcune percentuali verranno
 * azzerate" (deduplicati sull'ateneo, senza la tipologia - Lauree/Master/
 * Perfezionamenti - e senza indicare su quale azienda: `reset` può
 * coinvolgere sia l'azienda che si sta modificando sia le sue discendenti,
 * ma la richiesta di conferma è una sola). Usata sia dal salvataggio delle
 * percentuali sia dal cambio di padre (vedi GerarchiaAzienda.jsx): entrambi
 * gli endpoint rispondono con lo stesso formato (descrivi_cascata lato
 * server).
 * @param {Array<{ campi: string[] }>} reset
 */
export function messaggioAzzeramento(reset) {
  const chiavi = [...new Set(reset.flatMap((voce) => voce.campi))]
    .sort((a, b) => ORDINE_PERCENTUALE[a] - ORDINE_PERCENTUALE[b]);
  const atenei = [...new Set(chiavi.map((chiave) => ATENEO_PER_CAMPO[chiave] ?? chiave))];
  const elenco = new Intl.ListFormat("it", { style: "long", type: "conjunction" }).format(atenei);
  return `Le percentuali di ${elenco} verranno azzerate. Continuare?`;
}
