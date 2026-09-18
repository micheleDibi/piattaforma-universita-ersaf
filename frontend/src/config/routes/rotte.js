/**
 * Rotte dell'applicazione e voci del menu: unica fonte per percorsi e
 * navigazione, cosi' nessun componente scrive un indirizzo a mano.
 */

import {
  Building2,
  FileText,
  GraduationCap,
  LayoutDashboard,
  UserCog,
  Users,
} from "../icone.js";

export const NOME_APPLICAZIONE = "Piattaforma Università";

import { ROTTE } from "./percorsi.js";
export { ROTTE, ROTTA_INIZIALE } from "./percorsi.js";

/** Visibilita comune a menu desktop e mobile. */
export const VOCI_MENU = [
  { rotta: ROTTE.dashboard, etichetta: "Dashboard", icona: LayoutDashboard },
  { rotta: ROTTE.sottoscrittori, etichetta: "Sottoscrittori", icona: Users },
  {
    rotta: ROTTE.attuatori,
    etichetta: "Attuatori",
    icona: UserCog,
    soloNazionale: true,
  },
  {
    rotta: ROTTE.aziende,
    etichetta: "Aziende",
    icona: Building2,
    nascondiAderente: true,
  },
  {
    rotta: ROTTE.pratiche,
    etichetta: "Pratiche",
    icona: FileText,
    soloNazionale: true,
  },
  {
    rotta: ROTTE.prodotti,
    etichetta: "Prodotti formativi",
    icona: GraduationCap,
    soloNazionale: true,
  },
];

/** Riceve il ruolo gia normalizzato dalla sessione; condiviso da desktop e mobile. */
export function vociMenuPerRuolo(ruoloCodice) {
  const nazionale = ruoloCodice === "nazionale";
  const aderente = ruoloCodice === "aderente";
  return VOCI_MENU.filter((voce) => {
    if (voce.soloNazionale && !nazionale) return false;
    if (voce.nascondiAderente && aderente) return false;
    return true;
  });
}
