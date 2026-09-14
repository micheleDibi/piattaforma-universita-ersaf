import { haSessione, leggiCsrf, pulisciSessione, salvaSessione } from "./sessione.js";
import { vaiAlLogin } from "./ritornoAccesso.js";
import { descriviErrore, ErroreApi } from "./erroriApi.js";

export const API_BASE_URL = (import.meta.env?.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");
let caricamentoSessione = null;

async function invia(percorso, opzioni) {
  try {
    return await fetch(`${API_BASE_URL}${percorso}`, { ...opzioni, credentials: "include" });
  } catch {
    throw new ErroreApi("Connessione non riuscita. Controlla la rete e riprova.");
  }
}

export async function leggiJson(risposta) { return risposta.json().catch(() => null); }

export async function messaggioErrore(risposta, ripiego = "Si è verificato un errore.") {
  return descriviErrore(risposta, await leggiJson(risposta), ripiego);
}

export async function caricaSessione() {
  if (haSessione()) return true;
  if (!caricamentoSessione) {
    caricamentoSessione = (async () => {
      const risposta = await invia("/auth/session", { headers: { "X-ERSAF-Request": "1" }, cache: "no-store" });
      if (risposta.status === 401) return false;
      if (!risposta.ok) throw new ErroreApi(await messaggioErrore(risposta), risposta.status);
      salvaSessione(await leggiJson(risposta) ?? {});
      return true;
    })().finally(() => { caricamentoSessione = null; });
  }
  return caricamentoSessione;
}

export async function apiFetch(percorso, { auth = true, gestisci401 = true, headers, ...opzioni } = {}) {
  const metodo = (opzioni.method ?? "GET").toUpperCase();
  const scrittura = !["GET", "HEAD", "OPTIONS"].includes(metodo);
  const intestazioni = { "Content-Type": "application/json", ...headers, "X-ERSAF-Request": "1" };
  if (auth && scrittura) {
    const valida = await caricaSessione();
    if (valida) intestazioni["X-CSRF-Token"] = leggiCsrf();
  }
  const risposta = await invia(percorso, { ...opzioni, headers: intestazioni });
  if (risposta.status === 401 && gestisci401) {
    pulisciSessione();
    vaiAlLogin();
    throw new ErroreApi("Sessione scaduta o non valida. Accedi di nuovo.", 401);
  }
  return risposta;
}
