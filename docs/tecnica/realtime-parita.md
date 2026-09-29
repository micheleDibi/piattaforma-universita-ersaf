# Parità funzionale e hardening del realtime

Confronto del 28 settembre 2026 tra il servizio Java di Universo e il modulo
FastAPI. Il perimetro comprende tutte le funzioni realtime, i contratti dei
dati e le protezioni. Non comprende benchmark, RTT o throughput. Scadenze,
quote, timeout e limiti di memoria restano requisiti verificabili.

## Riferimento e metodo

Riferimento letto senza modificarlo: `Universo/realtime_lab/realtime-service`,
con inventario delle 76 classi di test e hash dei 312 file sorgente/test.
Una compilazione isolata di 16 classi originali ha prodotto la fixture
`backend/tests/support/realtime_java_vectors.json`: 44 casi crittografici,
otto casi JSON, due hash canonici, un cursore e quattro date legacy.
La fixture contiene soltanto chiavi e dati sintetici e registra gli hash delle
classi usate. Il gate ordinario legge questi vettori, senza richiedere Java.

Le prove del nuovo backend combinano questi vettori con test su MariaDB
usa-e-getta e con un server Uvicorn effettivo su loopback. Il test di trasporto
isola il database: autorizzazioni e persistenza sono provate separatamente
sul MariaDB. Una suite verde non costituisce un collaudo del client Flutter
pubblicato o di una configurazione di produzione.

## Funzioni e invarianti

Nella colonna prove, i file con prefisso `test_` sono in `backend/tests/`;
`realtime_completo` e `realtime_isolamento` sono le suite di integrazione.

| Meccanismo del riferimento Java | Implementazione nel backend | Prove |
|---|---|---|
| Login, JWT, refresh, recover e logout; credenziali mai inoltrate | `accesso`, `sessioni`, `token`; verifica password comune | `integration/test_realtime_completo.py`, test login/sessioni dell'app |
| Identità corrente, ID cliente/utente distinti, ruolo e dispositivo vincolati | `identita`, `sessioni`, query presenza | `realtime_isolamento`, `test_chat_universo.py` |
| Refresh monouso, replay revoca tutta la famiglia, limite 10000, recupero solo IDLE | lock e retry dell'intera transazione, storico hash | `integration/test_realtime_hardening.py`: refresh concorrente e limite; `realtime_completo`: recovery/logout |
| Inattività non prorogata dai frame WS; expiry indipendente dai messaggi | HTTP/handshake toccano attività; watchdog JWT e controllo prima dell'invio | `integration/test_realtime_hardening.py`, `unit/test_realtime_trasporto.py` |
| ACL PERSON, PRACTICE, TICKET pubblico e privato, audience massima 256 | `conversazioni`, ACL pratiche condivisa; letture bloccanti prima della scrittura | `realtime_completo`, `realtime_isolamento`, `test_chat_nativa.py` |
| Chiavi storiche PERSON/PRACTICE con grant; TICKET con appartenenza corrente | `crypto.autorizza_storico`, ACL ripetuta sul ticket | `integration/test_realtime_hardening.py`, `realtime_isolamento` |
| HKDF, u2/u3, AAD, contesti, sender, CID, versione/epoca, max 1000 byte UTF-8 | `crypto`, derivazione condivisa; archivio u3 vincolato al record | `unit/test_realtime_parita_java.py`: 44 vettori accettati/rifiutati |
| Pulizia buffer sensibili e chiusura delle chiavi | buffer mutabili, `finally` e svuotamento keyring nel lifespan anche dopo errore di preflight | vettori crypto e `unit/test_realtime_risorse.py` |
| Scrittura atomica di messaggio, grant, orario, ricevuta, notifiche e outbox | `scrittura`, `notifiche_scrittura`, unica transazione; retry 1062/1205/1213 | `realtime_completo`, `realtime_isolamento`, `test_chat_nativa.py` |
| Deduplicazione semantica compatibile con ricevute Java | hash sullo stesso ordine e JSON canonico | due hash differenziali; retry concorrenti e conflitto payload nelle integrazioni |
| ACK di tutte le socket attive; nessuna conferma anticipata o di altro utente | `quorum`, migrazione 019, marcatura prima dell'invio; retry 5–300 secondi per socket | `integration/test_realtime_hardening.py`, replay dopo disconnessione in `realtime_isolamento` |
| Ordine per utente, code limitate, lavoro fallito non blocca la coda | `esecutore`: worker fissi, limiti globale/per chiave, cancellazione e drain | `unit/test_realtime_hardening.py`, `unit/test_realtime_risorse.py` |
| Quote connessioni globale/utente/sessione, senza corse in ammissione | mutex SQL e lease; 2000/8/4 predefiniti | `integration/test_realtime_hardening.py` |
| Backpressure, invii seriali, budget memoria anche durante invio | `uscita`: 64 frame, 128 KiB/socket, 128 MiB/processo; batch inclusi | `unit/test_realtime_hardening.py`, `unit/test_realtime_risorse.py` |
| Limiter globale e per tipo, burst, tre violazioni consecutive | `limite_ingresso`, valori del riferimento | `unit/test_realtime_hardening.py` |
| Ping/pong, scadenza JWT, frame massimi, compressione disabilitata | Uvicorn/WebSocket configurato nel Dockerfile, versione fissata | `unit/test_realtime_trasporto.py` su una vera porta loopback |
| JSON rigoroso, profondità 32, rifiuto duplicati e campi/tipi impropri | `contratti`, `comandi`, validatori notifiche e query | vettori Java, `test_realtime_contratti.py`, `test_realtime_risorse.py` |
| Errori correlati solo a CHAT/TYPING; un errore ordinario non chiude la socket | `socket.errore` e ciclo ricezione | `test_realtime_trasporto.py`, ACK non ricevuto in `realtime_isolamento` |
| Storico e conversazioni per tutti i domini; chiavi e cursori separano pubblico/privato | `lettura`, SQL dedicato, `paginazione` | `realtime_completo`, `realtime_isolamento`; cursore firmato differenziale |
| UTC esatto per nuovi messaggi; convenzioni Europe/Rome dei record legacy | overlay `realtime_message_time`, conversione coerente col Java | quattro vettori delle date, incluse transizioni DST |
| Conteggi globali, letto/visto distinti, lettura per utente, niente modifiche ai messaggi legacy | `attenzione`, query visibili e stato dedicato | `realtime_completo`, `realtime_isolamento` |
| Snapshot di ID esatti, ACL ricontrollata all'applicazione, quota/expiry/tombstone | max 60 snapshot/utente, 50000 ID, 10 minuti; parsing rigoroso degli ID persistiti | snapshot/nuovi arrivi nelle integrazioni; revoca ACL e input corrotti nelle suite hardening |
| Produttore notifiche autenticato, idempotenza, destinatario unico, creatore attivo | `api_notifiche`, `notifiche_scrittura`; token separato | produttore concorrente in `realtime_isolamento`, bridge in `realtime_completo` |
| Bridge legacy con baseline, commit tardivi e righe non valide terminali | `bridge_notifiche`, scansione incrementale e audit | `realtime_completo`, validatori testuali in `test_realtime_risorse.py` |
| Presenza primo/ultimo collegamento, visibilità e typing, invalidazioni fra dispositivi | lease e stato SQL corrente; invii serializzati, nessun retry di stati presenza obsoleti | `realtime_completo`, `test_chat_nativa.py` |
| Retention limitata a metadati scaduti; messaggi, grant e letture conservati | `manutenzione`; ricevute/outbox 30 giorni, sessioni solo dopo revoca e scadenza | `test_realtime_conservazione.py` e migrazioni su MariaDB |
| TLS DB verificato con CA esplicita, eccezione privata opt-in, timeout e pool limitati | `database_trasporto` comune: CA senza trust store implicito; RFC1918 letterale; pool 8, acquisizione 5 s | `unit/test_database_trasporto.py`, incluso rifiuto downgrade prima dell'autenticazione |

## Adattamenti espliciti

- Il namespace è `/realtime` (pubblico `/api/realtime`). Il vecchio ponte che
  emetteva una sessione delegata da Università verso Java è sostituito dall'API
  cookie nativa, che usa lo stesso dominio di scrittura. Non serve un endpoint
  per autenticare un backend presso l'altro.
- Gli interruttori Java per servizio/read-only/writer non sono riproposti,
  per scelta esplicita: API e socket partono con il backend configurato.
- Login e protezione dei tentativi usano il servizio centrale Università:
  prenotazione SQL per account/IP, attese progressive, rehash e reset atomico.
  La policy è comune all'app, non una seconda mappa Java in memoria.
- Registrazione, presenza, eventi e quorum usano SQL per coordinare processi.
  L'ordine dell'esecutore in memoria è per processo; transazioni e ricevute
  garantiscono integrità fra processi. L'outbox resta la fonte per il replay.
- Il watchdog di trasporto usa Uvicorn: la mancanza di pong chiude con 1011
  (Java usava 1001); la scadenza di autenticazione chiude con 1008 in entrambi.
  La connessione viene comunque rimossa e le consegne non confermate restano
  recuperabili. Le soglie sono regole di sicurezza, non benchmark.
- Le credenziali DB restano nella configurazione privata SQLAlchemy esistente,
  con parametri nascosti nei log. I parametri URL non possono sovrascrivere
  host, credenziali o opzioni TLS. La policy TLS è comune al backend.
- La pulizia dei buffer controllati dal codice è verificata. Le copie interne
  dell'interprete e del provider crittografico non consentono una garanzia di
  azzeramento fisico dell'intera memoria del processo.

## Verifica e rilascio

Comandi: `scripts/verify-local.ps1 -Gate Backend` e `-Gate Docs`.
Il gate esclude i test marcati `timing`. Nessun test di questa attività invia
email/SMS, usa archivi reali o misura prestazioni. Le prove MariaDB sono
esclusivamente su `127.0.0.1:3307/ersaf_test`.

Prima di un rilascio servono migrazioni 017, 018 e 019, gli archivi legacy
coerenti e le chiavi dello stesso ambiente. In produzione occorre anche
configurare il trasporto DB: CA verificata oppure scelta esplicita della rete
privata legacy. Il passaggio di client e writer, un collaudo fra applicazioni
e il deploy non sono effettuati da questa verifica. Non è stata modificata
l'applicazione Universo né il servizio Java.
