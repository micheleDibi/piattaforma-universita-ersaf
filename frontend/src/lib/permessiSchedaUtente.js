// Cosa puo' modificare l'utente collegato sulla scheda Utente di una persona.
// Rispecchia i controlli del server, cosi' i campi non ammessi si presentano
// bloccati invece di finire in un errore al salvataggio:
// - nome utente, stato e utente padre: solo sulla propria scheda, oppure
//   Regionale o Nazionale (PUT /utenti/{id}, e_amministrativo);
// - ruolo: verifica_ruolo_assegnabile in backend/src/clienti/servizio.py.
//   Il Nazionale assegna tutto; il Regionale Aderente e Provinciale; il
//   Provinciale solo Aderente; gli altri nulla. Chi sta sotto (un ruolo che
//   si potrebbe assegnare) si declassa anche a Utente, dalla sola scheda
//   Utente. Chi non e' Nazionale non cambia il proprio ruolo, ne' quello di
//   chi ha un ruolo da attuatore che non potrebbe assegnare; chi ha un ruolo
//   senza accesso si promuove.

const RUOLI_AMMINISTRATIVI = ["nazionale", "regionale"];
// Gemella di RUOLI_ASSEGNABILI in backend/src/auth/autorizzazioni.py.
const RUOLI_ASSEGNABILI = {
  regionale: ["Aderente", "Provinciale"],
  provinciale: ["Aderente"],
};
const RUOLI_SENZA_ACCESSO = ["Utente", "Consulente", "Operatore"];
export const RUOLI_ATTUATORE = ["Aderente", "Provinciale", "Regionale", "Nazionale"];
const TUTTI_I_RUOLI = [...RUOLI_SENZA_ACCESSO, ...RUOLI_ATTUATORE];

/** `codiceRuoloAttuale`: il ruolo salvato della persona della scheda come
 * codice ("Aderente"), vuoto in creazione.
 *
 * `ruoliScheda` e `ruoliAttuatore` sono i codici che si possono scegliere
 * nella tendina della scheda Utente e in quella "Ruolo attuatore" di Dati
 * principali, compreso quello attuale: con un solo codice il ruolo non si
 * sceglie e si mostra come valore bloccato. */
export function permessiSchedaUtente(sessione, utenteIdScheda, codiceRuoloAttuale = "") {
  const ruolo = sessione?.ruoloCodice ?? "";
  const nazionale = ruolo === "nazionale";
  const sonoIo =
    utenteIdScheda != null && sessione?.utenteId === Number(utenteIdScheda);
  const assegnabili = nazionale ? TUTTI_I_RUOLI : RUOLI_ASSEGNABILI[ruolo] ?? [];
  const attuale = codiceRuoloAttuale ? [codiceRuoloAttuale] : [];
  const bloccato =
    (!nazionale && sonoIo) ||
    (Boolean(codiceRuoloAttuale) &&
      !RUOLI_SENZA_ACCESSO.includes(codiceRuoloAttuale) &&
      !assegnabili.includes(codiceRuoloAttuale));
  const conAttuale = (codici) =>
    bloccato ? attuale : [...new Set([...attuale, ...codici])];
  const declassa = assegnabili.includes(codiceRuoloAttuale) ? ["Utente"] : [];
  return {
    account: sonoIo || RUOLI_AMMINISTRATIVI.includes(ruolo),
    ruoliScheda: conAttuale([...assegnabili, ...declassa]),
    ruoliAttuatore: conAttuale(assegnabili.filter((codice) => RUOLI_ATTUATORE.includes(codice))),
  };
}
