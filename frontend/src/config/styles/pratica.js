import { pulsante } from "./pulsante.js";
import { scheda, titoloSezione } from "./superficie.js";
import { contenutoPagina, descrizionePagina, titoloPagina } from "./pagina.js";
export const STILI_PRATICA = {
  modulo: `${scheda()} p-6 sm:p-8 space-y-8`,
  sezione: "min-w-0 space-y-5", colonne: "grid grid-cols-1 gap-6 md:grid-cols-2",
  titolo: titoloSezione(), separatore: "border-divisore",
  azioni: "flex flex-wrap justify-end gap-3 border-t border-bordo pt-6",
  valore: "text-sm text-testo-forte break-words", nota: "text-sm text-testo-tenue",
  // Download del PDF nell intestazione della scheda.
  azioneDocumento: pulsante("secondario"),
  iconaAzione: "size-icona-piccola shrink-0",
  iconaAttesa: "size-icona-piccola shrink-0 animate-spin",
  // Un corso scelto per Corsi Singoli (RelazioniPratica.jsx): stesso stile
  // del riquadro del padre in anagrafica.js, qui con un pulsante per toglierlo.
  elencoCorsi: "space-y-1",
  rigaCorso: "flex items-center justify-between gap-2.5 rounded-controllo border border-bordo bg-superficie-tenue py-1.5 pr-1 pl-3.5",
};

// Pagina Pratiche (/pratiche senza universita'): la larghezza del design
// comprende i margini. Striscia, schede e tabelle stanno in
// pannelloPratiche.css, con le soglie del contenitore.
export const STILI_PANNELLO_PRATICHE = {
  pagina: `${contenutoPagina("pagina", { marginiInclusi: true })} pannello-pratiche`,
  titolo: titoloPagina(),
  descrizione: descrizionePagina(),
};

// Modale con tabella di selezione: stesso velo/finestra del modale di
// creazione azienda (config/styles/azienda.js). Usato sia per lo studente
// (selezione singola) sia per il percorso formativo (singola, o multipla
// per Corsi Singoli: vedi ModaleSelezionePercorso.jsx), quindi ha anche gli
// stili per la riga gia' scelta e il piede con il totale e il pulsante Conferma.
export const STILI_MODALE_TABELLA = {
  velo: "fixed inset-0 z-50 flex items-center justify-center bg-testo-forte/30 p-4 backdrop-blur-xs",
  // Altezza fissa e non massima: senza, la finestra cambia dimensione a ogni
  // ricerca, seguendo il numero di righe trovate.
  finestra: `${scheda()} flex h-[600px] w-full max-w-3xl flex-col p-6 shadow-xl sm:p-8`,
  // Il percorso formativo ha una colonna in piu' (Prezzo, CFU) e denominazioni
  // spesso lunghe (es. "SCIENZE DELL'ECONOMIA - LM56 - CURRICULUM..."): piu'
  // largo dello studente, stessa altezza fissa.
  finestraLarga: `${scheda()} flex h-[600px] w-full max-w-5xl flex-col p-6 shadow-xl sm:p-8`,
  titolo: "text-lg font-semibold text-testo",
  corpo: "mt-4 min-h-0 flex-1 overflow-y-auto",
  intestazioneColonna: "px-3 py-2 text-left text-etichetta uppercase tracking-wider text-testo-tenue",
  cella: "px-3 py-2.5 align-top",
  riga: "border-t border-divisore",
  rigaSelezionabile: "cursor-pointer hover:bg-riga-hover",
  rigaScelta: "cursor-pointer bg-primario/10 hover:bg-primario/15",
  rigaBloccata: "opacity-50",
  // Piede della selezione multipla: conteggio/totale a sinistra, Conferma a destra.
  piede: "mt-3 flex items-center justify-between gap-3 border-t border-divisore pt-3",
  totale: "text-sm text-testo-forte",
};
