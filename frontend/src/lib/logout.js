import { apiFetch } from "./api";
import { pulisciSessione } from "./sessione";

/**
 * Revoca la sessione sul backend e pulisce lo storage locale.
 *
 * Il fallimento di rete non deve impedire il logout lato client: l'utente
 * vuole uscire comunque, anche offline.
 */
export async function logout() {
  try {
    await apiFetch("/auth/logout", {
      method: "POST",
      gestisci401: false,
    });
  } catch {
    // Solo errori di rete: qui non c'e' un corpo di risposta da leggere ne'
    // un caso applicativo da gestire, la risposta e' sempre 204 senza corpo.
  } finally {
    pulisciSessione();
  }
}
