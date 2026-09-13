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
} from "lucide-react";

export const NOME_APPLICAZIONE = "Piattaforma Università";

export const ROTTE = {
  accesso: "/",
  dashboard: "/dashboard",
  sottoscrittori: "/sottoscrittori",
  attuatori: "/attuatori",
  aziende: "/aziende",
  pratiche: "/pratiche",
  prodotti: "/prodotti",
};

/** Dove si arriva dopo l'accesso e dalle rotte storiche /home ed /elenco. */
export const ROTTA_INIZIALE = ROTTE.sottoscrittori;

/**
 * Voci del menu. `soloAderente` replica la regola della barra laterale
 * precedente; `prefissi` tiene evidenziata la sezione anche nelle pagine di
 * dettaglio che le appartengono.
 */
export const VOCI_MENU = [
  { rotta: ROTTE.dashboard, etichetta: "Dashboard", icona: LayoutDashboard },
  { rotta: ROTTE.sottoscrittori, etichetta: "Sottoscrittori", icona: Users },
  {
    rotta: ROTTE.attuatori,
    etichetta: "Attuatori",
    icona: UserCog,
    soloAderente: true,
  },
  {
    rotta: ROTTE.aziende,
    etichetta: "Aziende",
    icona: Building2,
    soloAderente: true,
    prefissi: ["/nuova-azienda", "/modifica-azienda"],
  },
  {
    rotta: ROTTE.pratiche,
    etichetta: "Pratiche",
    icona: FileText,
    soloAderente: true,
  },
  {
    rotta: ROTTE.prodotti,
    etichetta: "Prodotti formativi",
    icona: GraduationCap,
    soloAderente: true,
    prefissi: ["/inserimentoprodotto"],
  },
];
