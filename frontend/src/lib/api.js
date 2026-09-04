import { leggiToken, pulisciSessione } from "./sessione";

// Prima l'indirizzo del backend era una stringa ripetuta in cinque punti di
// tre file: al primo deploy tre pagine su cinque avrebbero continuato a
// puntare a localhost.
export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

/**
 * Unica porta d'uscita verso l'API.
 *
 * @param {string} percorso
 * @param {object} opzioni
 *   auth        allega l'Authorization se c'e' una sessione (predefinito: si')
 *   gestisci401 su 401 svuota la sessione e torna al login (predefinito: si').
 *               Va messo a false sulle rotte /auth/*: li' un 401 significa
 *               "credenziali errate", e reindirizzare cancellerebbe il
 *               messaggio d'errore che l'utente deve leggere.
 */
export async function apiFetch(
  percorso,
  { auth = true, gestisci401 = true, headers, ...opzioni } = {},
) {
  const intestazioni = { "Content-Type": "application/json", ...headers };

  const token = auth ? leggiToken() : null;
  if (token) intestazioni.Authorization = `Bearer ${token}`;

  const risposta = await fetch(`${API_BASE_URL}${percorso}`, {
    ...opzioni,
    headers: intestazioni,
  });

  if (risposta.status === 401 && gestisci401) {
    pulisciSessione();
    window.location.replace("/");
    // Promise che non si risolve: la pagina sta per essere sostituita e il
    // chiamante non deve avere il tempo di disegnare un messaggio d'errore.
    return new Promise(() => {});
  }

  return risposta;
}

/**
 * Il corpo puo' non essere JSON: un 502 di un proxy restituisce HTML, e una
 * .json() secca mostrava all'utente "Unexpected token <" dentro il banner
 * rosso.
 */
export async function leggiJson(risposta) {
  return risposta.json().catch(() => null);
}
