import { TESTI_UTENTE } from "../config/testi/anagrafica.js";

/*
 * Logica della scheda di sottoscrittori e attuatori, fuori dai componenti
 * perche' si possa provare con node --test.
 */

/**
 * Stato dell'account letto con l'anagrafica. Convenzione legacy: -1 e'
 * attivo, qualunque altro valore disattivo.
 * @param {number|string|null|undefined} attivoSN
 * @returns {{ attivo: boolean, tono: "positivo"|"negativo" } | null}
 *   null se l'anagrafica non ha un utente
 */
export function statoAccount(attivoSN) {
  if (attivoSN === null || attivoSN === undefined || attivoSN === "") return null;
  const attivo = Number(attivoSN) === -1;
  return { attivo, tono: attivo ? "positivo" : "negativo" };
}

/**
 * Verifica di un recapito (email o cellulare) nella sua scheda. Il recapito
 * e' verificato solo se il valore nel campo e' ancora quello salvato e non e'
 * vuoto (un campo vuoto non si dichiara verificato, anche se il server lo
 * segnala); finche' non lo e', al posto della pillola c'e' il pulsante
 * "Verifica", attivo solo sul valore salvato e non vuoto.
 * @param {{ disponibile?: boolean, stato?: { valore?: string, verificato?: boolean, verificato_il?: string } } | undefined} verifica
 * @param {string} valore  valore corrente del campo
 */
export function statoRecapito(verifica, valore) {
  const disponibile = Boolean(verifica?.disponibile);
  const salvato = verifica?.stato?.valore === valore;
  const verificato = Boolean(salvato && valore && verifica?.stato?.verificato);
  return {
    verificato,
    verificatoIl: verificato ? verifica?.stato?.verificato_il ?? null : null,
    mostraVerifica: disponibile && !verificato,
    verificaDisabilitata: !salvato || !valore,
    daSalvare: disponibile && !salvato && Boolean(valore),
  };
}

/** Data e ora della verifica di un recapito: "12/09/2024, 17:24". */
export function dataVerifica(valore) {
  return new Date(valore).toLocaleDateString("it-IT", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Data della cronologia dell'utente: "31/12/1999, 01:00:00"; "" se assente. */
export function dataCronologia(valore) {
  return valore ? new Date(valore).toLocaleString("it-IT") : "";
}

/**
 * Nome di un utente collegato (padre, autore dell'ultimo aggiornamento).
 * `padre` e `aggiornato_da` sono utenti, non clienti: il nome della persona
 * sta nel cliente annidato, e lo username resta come ripiego per gli utenti
 * che una riga clienti non ce l'hanno.
 * @param {{ utente_id?: number, utente_username?: string, cliente?: { cliente_nome?: string, cliente_cognome?: string } } | null | undefined} utente
 * @param {number|null|undefined} idNumerico  identificativo grezzo, se l'utente non e' stato caricato
 */
export function nomeUtente(utente, idNumerico) {
  if (!utente) {
    return idNumerico ? TESTI_UTENTE.identificativo(idNumerico) : TESTI_UTENTE.nessuno;
  }
  const persona = `${utente.cliente?.cliente_nome || ""} ${
    utente.cliente?.cliente_cognome || ""
  }`.trim();
  return persona || utente.utente_username || TESTI_UTENTE.identificativo(utente.utente_id);
}
