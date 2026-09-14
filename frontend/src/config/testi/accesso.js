// Catalogo italiano del flusso di accesso; il nome del prodotto resta in routes/rotte.
export const TESTI_ACCESSO = {
  titolo: "Accedi all’area riservata",
  descrizione: "Usa le credenziali del tuo account ERSAF.",
  username: "Nome utente",
  password: "Password",
  entra: "Accedi",
  accessoInCorso: "Accesso in corso…",
  recupera: "Hai dimenticato la password?",
  torna: "Torna all’accesso",
  scaduta: "La sessione è scaduta o non è più valida. Accedi di nuovo per riprendere dalla pagina che avevi aperto.",
  aggiornata: "Password aggiornata. Accedi con le nuove credenziali.",
  attesa: (secondi) => `Puoi riprovare tra ${secondi} s.`,
  attesaTerminata: "Ora puoi riprovare ad accedere.",
  verificaSessione: "Verifica dell’accesso",
  verificaInCorso: "Verifica della sessione in corso…",
  riprova: "Riprova",
};

export const TESTI_PASSWORD = {
  azioneVisibilita: (visibile, etichetta) => `${visibile ? "Nascondi" : "Mostra"} ${etichetta === "Conferma la password" ? "password di conferma" : etichetta.toLowerCase()}`,
  capsLock: "Bloc Maiusc attivo",
  nuova: "Nuova password",
  conferma: "Conferma la password",
  coincidono: "Le password coincidono.",
  diverse: "Le password non coincidono.",
  forza: "Robustezza indicativa",
  lettura: { ok: "requisito soddisfatto", ko: "requisito non soddisfatto", neutro: "requisito da soddisfare", non_verificabile: "verificato al salvataggio" },
  alSalvataggio: "Verificata al salvataggio",
  riepilogo: (soddisfatte, totale, forza) => `${soddisfatte} requisiti su ${totale} soddisfatti. Robustezza: ${forza}.`,
};

export const TESTI_RECUPERO = {
  titolo: "Recupera la password",
  descrizione: "Inserisci l’email associata al tuo account. Ti invieremo un link per scegliere una nuova password.",
  email: "Indirizzo email",
  durata: "Il link è valido per 60 minuti e può essere usato una sola volta.",
  invia: "Invia il link di recupero",
  invioInCorso: "Invio in corso…",
  inviato: "Richiesta inviata",
  // Contratto esistente: stessa frase anche senza risposta dal servizio.
  esito: "Se l'indirizzo è associato a un account riceverai una mail",
  dopoInvio: "Controlla anche la cartella spam. Il link è valido per 60 minuti dalla richiesta.",
};

export const TESTI_RESET = {
  titolo: "Scegli una nuova password",
  descrizione: "Imposta una password personale e confermala per completare il recupero.",
  verifica: "Verifica del link in corso…",
  linkNonValido: "Link non disponibile",
  nuovoLink: "Richiedi un nuovo link",
  istruzioniLink: "Puoi richiedere un nuovo link: quello precedente verrà annullato. Se hai ricaricato questa pagina, riapri il link dalla mail.",
  salva: "Salva la nuova password",
  salvataggio: "Salvataggio in corso…",
  errore: "Non è stato possibile cambiare la password. Richiedi un nuovo link.",
  rete: "Connessione non riuscita. Riprova.",
  motivi: {
    scaduto: "Il link è scaduto: era valido per 60 minuti dalla richiesta.",
    gia_usato: "Questo link è già stato usato: la password è già stata cambiata.",
    non_valido: "Il link non è valido. Può essere stato copiato male, oppure una richiesta più recente lo ha sostituito.",
    rete: "Non è stato possibile verificare il link. Controlla la connessione e riapri il link dalla mail.",
  },
};
