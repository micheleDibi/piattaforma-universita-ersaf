import { scheda, titoloSezione } from "./superficie.js";
export const STILI_PRATICA = {
  modulo: `${scheda()} p-6 sm:p-8 space-y-8`,
  sezione: "min-w-0 space-y-5", colonne: "grid grid-cols-1 gap-6 md:grid-cols-2",
  titolo: titoloSezione(), separatore: "border-bordo",
  azioni: "flex flex-wrap justify-end gap-3 border-t border-bordo pt-6",
  valore: "text-sm text-testo-forte break-words", nota: "text-sm text-testo-tenue",
};
