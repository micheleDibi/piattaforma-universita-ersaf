---
---

## Novità e correzioni

- modificato: Nella chat delle pratiche i propri messaggi compaiono a destra e quelli ricevuti a sinistra.
- aggiunto: Un pallino verde accanto agli altri autori indica quando sono online.
- rimosso: La chat non mostra più descrizioni superflue o lo stato generico di connessione.
- modificato: Il campo messaggio cresce con il testo e il pulsante d'invio resta esterno a destra, allineato in basso.
- modificato: Le schede mostrano solo l'indicatore della selezione, senza un divisore continuo.

## Dettagli tecnici

- aggiunto: Presenza condivisa fra socket cookie delle pratiche e sessioni realtime, con verifica dei partecipanti e dei criteri comuni di revoca.
- modificato: Quote e ordine dei lock delle connessioni sono comuni ai due trasporti; le lease cookie sono escluse dal quorum ACK Bearer.
- modificato: Il composer gestisce crescita limitata, invio desktop, nuova riga mobile e composizione IME senza duplicare gli invii o cancellare nuove bozze.
- aggiunto: Prove di presenza, revoca, cleanup delle connessioni, quorum e tastiera. Nessuna nuova migrazione o configurazione.
