---
incompatibile: true
---

## Dettagli tecnici

- aggiunto: Servizio realtime FastAPI completo per sessioni, chat personali, pratiche, ticket pubblici e privati, notifiche, presenza, letture e recupero delle consegne.
- modificato: Il namespace `/realtime` sostituisce `/chat-universo`; la scrittura delle pratiche con cookie riusa il medesimo dominio. L'integrazione del client e il passaggio dal servizio precedente richiedono un rilascio coordinato.
- aggiunto: Migrazione `018_realtime_completo.sql`, additiva e senza rollback distruttivo degli archivi condivisi; applicarla dopo la 017 e prima del backend aggiornato.
- aggiunto: Configurazione `REALTIME_SCHEMA_TICKET`, `REALTIME_ACCESSO_SECONDI`, `REALTIME_REFRESH_GIORNI`, `REALTIME_PRODUCER_TOKEN_FILE` e `REALTIME_MANUTENZIONE_SECONDI`. API, WebSocket, invio e lavori periodici partono con il backend senza flag applicativi; schema e chiavi sono richiesti all'avvio, indipendentemente dall'integrazione di Universo.
- sicurezza: Sessioni revocabili, rotazione del refresh con rilevamento del riuso, ACL condivise, limiti persistenti e snapshot di lettura immutabili; cookie applicativi e token realtime restano distinti.
- aggiunto: Migrazione `019_realtime_consegne_connessioni.sql`, da applicare dopo la 018, per le conferme di consegna di ogni connessione. Una conferma non interrompe il recapito agli altri dispositivi attivi; chiusure e nuovi collegamenti aggiornano il quorum.
- sicurezza: Ripresi limiti per tipo di comando, ammissione dei collegamenti, code limitate, invii serializzati, watchdog, rotazioni limitate e conservazione degli archivi. Validazione UTF-8/JSON e snapshot rigorosa; compatibilità crittografica e dei dati verificata con vettori Java sintetici.
- sicurezza: Policy DB comune con pool e timeout limitati. In produzione `DATABASE_TRASPORTO=verify-full` richiede `DATABASE_CA_FILE`; l'eccezione `rete-privata` richiede IPv4 RFC1918 letterali. Predisporre la configurazione privata prima del rilascio: nessun fallback TLS silenzioso.
