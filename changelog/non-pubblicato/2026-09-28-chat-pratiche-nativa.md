---
incompatibile: true
---

## Novità e correzioni

- modificato: Le chat delle pratiche sono gestite dal backend della piattaforma, mantenendo lo storico condiviso con Universo.
- corretto: I tentativi ripetuti dopo un'interruzione della connessione non duplicano messaggi e notifiche.

## Dettagli tecnici

- modificato: Dominio FastAPI comune a sessione cookie e token Universo esistente; rimossi sessioni delegate e trasporto verso Java.
- aggiunto: Migrazione additiva 017, grant storici, coda durevole, limite per utente e verifiche di revoca.
- modificato: Attivazione coordinata tramite configurazione e delta Flutter; nessuna migrazione automatica tra dataset e nessun deploy implicito.
- aggiunto: Blocco configurabile del vecchio writer Java per un passaggio senza due percorsi di inserimento attivi.
