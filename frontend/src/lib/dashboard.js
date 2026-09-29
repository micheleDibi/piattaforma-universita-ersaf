// Benvenuto e scorciatoie della Dashboard, derivati dalla sessione e dal menu.
import { ROTTE, vociMenuPerRuolo } from "../config/routes/rotte.js";
import { TESTI_DASHBOARD as testi } from "../config/testi/dashboard.js";

/** "Buon lavoro, Mario." con il solo nome della sessione; senza nome "Buon lavoro." */
export function salutoDashboard(sessione) {
  const nome = typeof sessione?.nome === "string" ? sessione.nome.replace(/\s+/g, " ").trim() : "";
  return nome ? testi.salutoConNome(nome) : testi.saluto;
}

/** Descrizione dell'intestazione: saluto e introduzione. */
export function descrizioneDashboard(sessione) {
  return `${salutoDashboard(sessione)} ${testi.introduzione}`;
}

/** Le voci del menu del ruolo, senza la Dashboard, con la descrizione per percorso. */
export function scorciatoieDashboard(ruolo) {
  return vociMenuPerRuolo(ruolo)
    .filter((voce) => voce.rotta !== ROTTE.dashboard)
    .map(({ rotta, etichetta, icona }) => ({ rotta, etichetta, icona, descrizione: testi.scorciatoie[rotta] ?? "" }));
}
