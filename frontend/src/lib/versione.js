import { TESTI_VERSIONE as testi } from "../config/testi/versione.js";

// L'ora si legge sempre come in sede, qualunque sia il fuso del dispositivo.
const FUSO = "Europe/Rome";

/**
 * Progressivo e istante della release, incorporati nel bundle dal deploy
 * (build-arg VITE_VERSIONE e VITE_AGGIORNATA_IL, vedi Dockerfile). Fuori dal
 * deploy mancano entrambi: e' la versione di sviluppo.
 */
export function leggiVersione(ambiente = import.meta.env ?? {}) {
  const grezzo = String(ambiente.VITE_VERSIONE ?? "").trim();
  const numero = /^\d+$/.test(grezzo) ? Number(grezzo) : null;
  const data = ambiente.VITE_AGGIORNATA_IL ? new Date(ambiente.VITE_AGGIORNATA_IL) : null;
  return { numero, aggiornataIl: data && !Number.isNaN(data.getTime()) ? data : null };
}

/** Le due righe da mostrare: "Versione 117" e "Aggiornata il 16/09/2026 alle 19:30". */
export function descriviVersione({ numero, aggiornataIl }) {
  if (numero === null) return { versione: testi.sviluppo, aggiornamento: null };
  if (!aggiornataIl) return { versione: testi.versione(numero), aggiornamento: null };
  const giorno = aggiornataIl.toLocaleDateString("it-IT", { timeZone: FUSO, day: "2-digit", month: "2-digit", year: "numeric" });
  const ora = aggiornataIl.toLocaleTimeString("it-IT", { timeZone: FUSO, hour: "2-digit", minute: "2-digit" });
  return { versione: testi.versione(numero), aggiornamento: testi.aggiornata(giorno, ora) };
}

export const VERSIONE_APPLICAZIONE = descriviVersione(leggiVersione());
