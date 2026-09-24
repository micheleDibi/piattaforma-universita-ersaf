import { pulsante } from "./pulsante.js";
import { scheda, titoloSezione } from "./superficie.js";
import { schedaElenco } from "./tabella.js";
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
};

// Pannello delle universita' (/pratiche senza universita'): corpo della scheda
// sotto la testata, un blocco per ateneo separato dai divisori. I pulsanti non
// vanno a capo: le colonne crescono con lo spazio (una, due, tre).
export const STILI_PANNELLO_PRATICHE = {
  corpo: `${schedaElenco("corpo")} p-5 sm:px-6`,
  contenuto: "space-y-10",
  // first-of-type: anche con l'avviso sopra, il primo ateneo non ha la riga.
  sezione: "border-t border-divisore pt-4 first-of-type:border-t-0 first-of-type:pt-0",
  titolo: titoloSezione(),
  riga: "flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-6",
  logo: "size-24 object-contain shrink-0",
  tipologie: "grid w-full min-w-0 flex-1 gap-3 md:grid-cols-2 xl:grid-cols-3",
  tipologia: pulsante("secondario"),
};
