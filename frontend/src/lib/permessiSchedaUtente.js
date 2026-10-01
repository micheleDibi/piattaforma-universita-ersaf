// Cosa puo' modificare l'utente collegato sulla scheda Utente di una persona.
// Rispecchia i controlli del server, cosi' i campi non ammessi si presentano
// bloccati invece di finire in un errore al salvataggio:
// - nome utente, stato e utente padre: solo sulla propria scheda, oppure
//   Regionale o Nazionale (PUT /utenti/{id}, e_amministrativo);
// - ruolo: chi non e' Nazionale non cambia il proprio e non assegna
//   Nazionale a nessuno (verifica_ruolo_assegnabile).

const RUOLI_AMMINISTRATIVI = ["nazionale", "regionale"];
export const CODICE_RUOLO_NAZIONALE = "Nazionale";

export function permessiSchedaUtente(sessione, utenteIdScheda) {
  const ruolo = sessione?.ruoloCodice ?? "";
  const nazionale = ruolo === "nazionale";
  const sonoIo =
    utenteIdScheda != null && sessione?.utenteId === Number(utenteIdScheda);
  return {
    account: sonoIo || RUOLI_AMMINISTRATIVI.includes(ruolo),
    ruolo: nazionale || !sonoIo,
    assegnaNazionale: nazionale,
  };
}
