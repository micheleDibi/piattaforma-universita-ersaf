---
incompatibile: true
---

## Novità e correzioni

- aggiunto: Codice automatico per le nuove pratiche SSML e A4U, con progressivi distinti per tipo di corso.
- modificato: La creazione pratica propone studenti verificati e percorsi validi, con scelta multipla per i corsi singoli e relativo totale.
- corretto: Le finestre di selezione usano la gestione condivisa di focus ed Escape e si adattano all'altezza disponibile.
- corretto: Il totale dei corsi mantiene i decimali esatti; la nuova pratica collega il creatore anche ai permessi della conversazione.

## Dettagli tecnici

- modificato: Integrato il commit `41665a5` di Login con chat, firma e realtime completo; la migrazione dei contatori diventa `020_contatori_codice_pratica.sql` per conservare la 017 della chat.
- aggiunto: Migrazione `021_capienza_notifiche.sql` per il ciphertext nel corpo delle notifiche legacy; il rollback conserva la capienza per non perdere dati.
- sicurezza: Overlay `compose.tls.yml` per la CA e i certificati del clone; `verify-full` verifica la connessione dell'API al database.
- modificato: Lo staging del realtime richiede anche l'archivio ticket clonato sullo stesso MariaDB, il keyring storico e una configurazione privata completa. Il client Universo e il servizio Java restano indipendenti dal rilascio.
