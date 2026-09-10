// Unico punto in cui si decide DOVE vive la sessione.
//
// Si usa localStorage, come prima. sessionStorage ridurrebbe la finestra utile
// a un XSS, ma su un back-office rompe l'apertura di un link in una scheda
// nuova e impone un login a ogni chiusura di scheda; il token scade comunque
// lato server dopo SESSION_TTL_HOURS e il 401 viene gestito da apiFetch.
// Un cookie HttpOnly sarebbe piu' solido, ma e' incompatibile con la scelta
// Authorization: Bearer e porterebbe con se' CSRF e modifiche a CORS.
// Per cambiare idea basta questa riga.
const DEPOSITO = window.localStorage;

// Le tre chiavi devono stare nello STESSO deposito: se utente_id
// sopravvivesse al token, NuovoSottoscrittore salverebbe clienti attribuiti a
// una sessione morta.
const CHIAVE_TOKEN = "sessione_token";
const CHIAVE_UTENTE = "utente_id";
const CHIAVE_RUOLO = "ruolo_codice";

export function salvaSessione({ token, utenteId, ruoloCodice }) {
  DEPOSITO.setItem(CHIAVE_TOKEN, token);
  DEPOSITO.setItem(CHIAVE_UTENTE, String(utenteId));
  // Normalizzato in minuscolo IN SCRITTURA: il backend confronta
  // ruolo_codice.lower(), il frontend confrontava === "nazionale" con la N
  // maiuscola che arriva dal database. Normalizzare qui rende ogni confronto a
  // valle insensibile al maiuscolo.
  DEPOSITO.setItem(CHIAVE_RUOLO, String(ruoloCodice ?? "").toLowerCase());
}

export function leggiToken() {
  return DEPOSITO.getItem(CHIAVE_TOKEN);
}

export function leggiRuolo() {
  return DEPOSITO.getItem(CHIAVE_RUOLO) ?? "";
}

/**
 * clienti.utente_id e' NOT NULL. Prima si faceva
 * Number(localStorage.getItem("utente_id")): con la chiave assente diventava
 * NaN, che JSON.stringify serializza come null, e il POST falliva con un
 * errore incomprensibile a meta' compilazione del form. Qui si restituisce
 * null in modo esplicito, cosi' il chiamante puo' fermarsi prima.
 */
export function leggiUtenteId() {
  const grezzo = DEPOSITO.getItem(CHIAVE_UTENTE);
  const numero = Number(grezzo);
  return grezzo !== null && Number.isInteger(numero) && numero > 0 ? numero : null;
}

export function pulisciSessione() {
  [CHIAVE_TOKEN, CHIAVE_UTENTE, CHIAVE_RUOLO].forEach((chiave) =>
    DEPOSITO.removeItem(chiave),
  );
}
