import { useEffect, useState, useSyncExternalStore } from "react";
import { ConversazionePratica } from "../lib/conversazionePratica.js";
import { apriSocketPratica, leggiMessaggi, preparaMessaggio } from "../lib/chatPratica.js";

export function useChatPratica(id) {
  const [chat] = useState(() => new ConversazionePratica(id, {
    leggi: leggiMessaggi, prepara: preparaMessaggio, socket: apriSocketPratica,
  }));
  useEffect(() => { chat.start(); return () => chat.stop(); }, [chat]);
  return { ...useSyncExternalStore(chat.subscribe, chat.snapshot), chat };
}
