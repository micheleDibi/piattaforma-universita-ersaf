import { pulsante } from "./pulsante.js";
import { scheda, titoloSezione } from "./superficie.js";
import { contenutoPagina, descrizionePagina, titoloPagina } from "./pagina.js";
export const STILI_PRATICA = {
  modulo: `${scheda()} p-6 sm:p-8 space-y-8`,
  sezione: "min-w-0 space-y-5", colonne: "grid grid-cols-1 gap-6 md:grid-cols-2",
  scelteRinnovo: "flex flex-col gap-2",
  titolo: titoloSezione(), separatore: "border-divisore",
  azioni: "flex flex-wrap justify-end gap-3 border-t border-bordo pt-6",
  valore: "text-sm text-testo-forte break-words", nota: "text-sm text-testo-tenue",
  // Download del PDF nell intestazione della scheda.
  azioneDocumento: pulsante("secondario"),
  iconaAzione: "size-icona-piccola shrink-0",
  iconaAttesa: "size-icona-piccola shrink-0 animate-spin",
  // Elenco dei corsi di una pratica Corsi Singoli (ElencoCorsiPratica.jsx):
  // tabella che scorre in orizzontale su schermi stretti, non la pagina.
  tabellaCorsi: "-mx-3 overflow-x-auto",
  tabella: "w-full min-w-[40rem] text-sm",
  intestazione: "px-3 py-2 text-left text-etichetta uppercase tracking-wider text-testo-tenue",
  intestazioneNumero: "px-3 py-2 text-right text-etichetta uppercase tracking-wider text-testo-tenue",
  rigaCorso: "border-t border-divisore",
  cella: "px-3 py-2.5 align-middle text-testo-forte",
  cellaTenue: "px-3 py-2.5 align-middle text-testo-tenue",
  // Il codice ("SECS-P/12") non va a capo sul trattino.
  cellaCodice: "whitespace-nowrap px-3 py-2.5 align-middle text-testo-tenue",
  cellaNumero: "px-3 py-2.5 align-middle text-right tabular-nums text-testo-forte",
  cellaAzione: "w-px py-1.5 pr-1 pl-3 text-right align-middle",
};

// Pagina Pratiche (/pratiche senza universita'): la larghezza del design
// comprende i margini. Striscia, schede e tabelle stanno in
// pannelloPratiche.css, con le soglie del contenitore.
export const STILI_PANNELLO_PRATICHE = {
  pagina: `${contenutoPagina("pagina", { marginiInclusi: true })} pannello-pratiche`,
  titolo: titoloPagina(),
  descrizione: descrizionePagina(),
};

// Selezioni nel Dialogo condiviso: dimensioni e focus centralizzati.
export const STILI_MODALE_TABELLA = {
  contenuto: "dialogo__selezione",
  titolo: "text-lg font-semibold text-testo",
  // relative: i testi sr-only delle righe (position absolute) devono restare
  // dentro il corpo scorrevole; senza, il loro contenitore e' il <dialog>, che
  // diventava a sua volta scorrevole (doppio scroll all'apertura).
  corpo: "relative mt-4 min-h-0 flex-1 overflow-y-auto",
  intestazioneColonna: "px-3 py-2 text-left text-etichetta uppercase tracking-wider text-testo-tenue",
  cella: "px-3 py-2.5 align-top",
  cellaAzione: "w-px text-right align-middle",
  riga: "border-t border-divisore",
  rigaSelezionabile: "cursor-pointer hover:bg-riga-hover",
  rigaScelta: "cursor-pointer bg-primario/10 hover:bg-primario/15",
  rigaBloccata: "opacity-50",
  // Riepilogo dei corsi scelti (selezione multipla), fisso sotto l'elenco:
  // pillole compatte che vanno a capo; oltre ~3 righe il riquadro scorre per
  // conto suo, per non togliere spazio all'elenco.
  riepilogo: "mt-3 shrink-0 border-t border-divisore pt-3",
  titoloRiepilogo: "text-etichetta uppercase tracking-wider text-testo-tenue",
  elencoRiepilogo: "mt-2 flex max-h-[6.75rem] flex-wrap content-start gap-1.5 overflow-y-auto",
  voceRiepilogo:
    "inline-flex h-7 max-w-full items-center gap-1 rounded-full border border-primario/25 " +
    "bg-primario/10 pr-0.5 pl-3 text-dettaglio text-testo-forte",
  testoVoceRiepilogo: "min-w-0 max-w-[16rem] truncate",
  togliVoceRiepilogo:
    "inline-flex size-6 shrink-0 cursor-pointer items-center justify-center rounded-full " +
    "text-testo-tenue transition-colors hover:bg-primario/15 hover:text-testo-forte " +
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-fuoco [&_svg]:size-3.5",
  riepilogoVuoto: "mt-2 text-sm text-testo-tenue",
  // Piede della selezione multipla: conteggio/totale a sinistra, Conferma a destra.
  piede: "mt-3 flex shrink-0 items-center justify-between gap-3 border-t border-divisore pt-3",
  totale: "text-sm text-testo-forte",
  // Conferma in linea (avviso + pulsanti), come STILI_AZIENDA.conferma.
  conferma: "flex flex-wrap items-center gap-3",
  messaggioConferma: "min-w-0 flex-[1_1_16rem]",
  pulsantiConferma: "flex shrink-0 gap-3",
};
