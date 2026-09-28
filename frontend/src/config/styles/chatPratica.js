import { campo } from "./campo.js";
export const STILI_CHAT = {
  sezione: "chat-pratica", testata: "flex flex-wrap items-start justify-between gap-3",
  titolo: "text-base font-semibold text-testo", nota: "text-sm text-testo-tenue",
  storico: "chat-pratica__storico", elenco: "space-y-5", messaggio: "chat-pratica__messaggio",
  mio: "chat-pratica__messaggio chat-pratica__messaggio--mio",
  metadati: "flex flex-wrap items-baseline gap-x-3 gap-y-1 text-xs text-testo-tenue",
  autore: "font-semibold text-testo", testo: "whitespace-pre-wrap break-words text-sm text-testo mt-1",
  compositore: "space-y-3 border-t border-divisore pt-4", campo: `${campo()} min-h-24 resize-y`,
  azioni: "flex flex-wrap items-center justify-between gap-3", icona: "size-icona-piccola",
  pendente: "border-l-2 border-attenzione pl-3 space-y-2", errore: "text-sm text-negativo",
};
