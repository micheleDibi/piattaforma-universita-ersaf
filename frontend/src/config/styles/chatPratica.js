import { pulsanteIcona } from "./pulsante.js";
import { campo } from "./campo.js";
export const STILI_CHAT = {
  sezione: "chat-pratica", titolo: "sr-only", nota: "text-sm text-testo-tenue",
  storico: "chat-pratica__storico", elenco: "chat-pratica__elenco", messaggio: "chat-pratica__messaggio",
  mio: "chat-pratica__messaggio chat-pratica__messaggio--mio",
  metadati: "chat-pratica__metadati text-xs text-testo-tenue",
  autore: "inline-flex items-center gap-1.5 font-semibold text-testo", presenza: "chat-pratica__presenza",
  testo: "chat-pratica__testo whitespace-pre-wrap text-sm text-testo mt-1",
  compositore: "grid grid-cols-[minmax(0,1fr)_auto] items-end gap-2 min-w-0",
  campo: `${campo()} chat-pratica__campo`, etichettaCampo: "sr-only",
  invia: `${pulsanteIcona("primario", "grande")} self-end`, icona: "size-icona",
  erroreCompositore: "col-span-full text-sm text-negativo",
  pendente: "chat-pratica__messaggio chat-pratica__messaggio--mio border border-attenzione space-y-2", errore: "text-sm text-negativo",
};
