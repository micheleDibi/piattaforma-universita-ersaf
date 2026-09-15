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

export const ROTTE = {
  accesso: "/",
  recuperoPassword: "/password-dimenticata",
  reimpostaPassword: "/reimposta-password",
  dashboard: "/dashboard",
  profilo: "/profilo",
  sottoscrittori: "/sottoscrittori",
  attuatori: "/attuatori",
  aziende: "/aziende",
  pratiche: "/pratiche",
  prodotti: "/prodotti",
};

/** Dove si arriva dopo l'accesso e dalle rotte storiche /home ed /elenco. */
export const ROTTA_INIZIALE = ROTTE.sottoscrittori;

/**
 * Voci del menu. `soloNazionale` riserva gli elenchi gestionali al Nazionale;
 * `prefissi` tiene evidenziata la sezione anche nelle pagine di
 * dettaglio che le appartengono.
 */
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
    soloNazionale: true,
    prefissi: ["/nuova-azienda", "/modifica-azienda"],
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
    prefissi: ["/inserimentoprodotto"],
  },
];

/** Riceve il ruolo gia normalizzato dalla sessione; condiviso da desktop e mobile. */
export function vociMenuPerRuolo(ruoloCodice) {
  const nazionale = ruoloCodice === "nazionale";
  return VOCI_MENU.filter((voce) => !voce.soloNazionale || nazionale);
}
