import { API_BASE_URL, apiFetch, caricaSessione, messaggioErrore } from "./api.js";
import { TESTI_CHAT as testi } from "../config/testi/chatPratica.js";
import { leggiCsrf } from "./sessione.js";

async function richiesta(percorso, opzioni) {
  const risposta = await apiFetch(percorso, opzioni);
  if (!risposta.ok) {
    const errore = new Error(await messaggioErrore(risposta));
    errore.status = risposta.status;
    throw errore;
  }
  return risposta.json();
}
export function leggiMessaggi(id, cursore, signal) {
  const query = cursore ? `?cursor=${encodeURIComponent(cursore)}` : "";
  return richiesta(`/pratiche/${id}/messaggi${query}`, { signal, cache: "no-store" });
}
export function preparaMessaggio(id, testo, clientMessageId, signal) {
  return richiesta(`/pratiche/${id}/messaggi/prepara`, {
    method: "POST", signal, body: JSON.stringify({ testo, clientMessageId }),
  });
}
export async function apriSocketPratica(id) {
  if (!await caricaSessione()) throw new Error(testi.sessioneScaduta);
  const url = new URL(`${API_BASE_URL}/pratiche/${id}/messaggi/socket`, window.location.href);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return new WebSocket(url, ["ersaf.pratiche.v1", `csrf.${leggiCsrf()}`]);
}
