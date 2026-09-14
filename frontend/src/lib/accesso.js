import { apiFetch, leggiJson } from "./api.js";
import { descriviErrore, ErroreApi, secondiAttesa } from "./erroriApi.js";
import { salvaSessione } from "./sessione.js";

export async function accedi(username, password) {
  const risposta = await apiFetch("/auth/login", {
    method: "POST", auth: false, gestisci401: false,
    body: JSON.stringify({ utente_username: username, utente_password: password }),
  });
  const dati = await leggiJson(risposta);
  if (!risposta.ok) {
    const ripiego = risposta.status === 401 ? "Username o password errati" : "Risposta del server non valida. Riprova.";
    throw new ErroreApi(descriviErrore(risposta, dati, ripiego), risposta.status, secondiAttesa(risposta.headers.get("Retry-After")));
  }
  if (dati?.requires_2fa) return dati;
  salvaSessione(dati ?? {});
  return true;
}
