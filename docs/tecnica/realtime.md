# Servizio realtime condiviso

Il modulo `backend/src/realtime/` porta nel backend FastAPI tutte le funzioni
del servizio realtime Java: sessioni, chat personali, pratiche, ticket pubblici
e privati, notifiche, letture, presenza e recupero delle consegne. Non chiama
il servizio Java. La chat delle pratiche di Università usa lo stesso dominio
di scrittura attraverso l'adattatore `chat_pratiche/scrittura.py`.

API, WebSocket e lavori periodici sono parte dell'avvio normale del backend,
senza interruttori di abilitazione. Il collegamento del client Universo e la
dismissione del servizio precedente sono attività successive e indipendenti
dall'avvio di FastAPI. Il rilascio di collaudo usa un clone isolato. I vecchi delta per
il solo trasporto delle pratiche non sono il piano di integrazione corrente.

Le otto query in `backend/src/realtime/sql/` sono risorse applicative versionate,
distinte dai dump ignorati da Git. L'avvio verifica che siano tutte presenti e
non vuote: una release incompleta si ferma prima di dichiararsi pronta.

## Responsabilità

| Parte | Moduli |
|---|---|
| Router HTTP e socket | `rotte`, `accesso`, `api_lettura`, `api_chiavi`, `api_notifiche`, `socket` |
| Identità e sessioni persistenti | `identita`, `sessioni`, `token` |
| Permessi e cifratura | `conversazioni`, `crypto`; partecipazione pratiche e derivazione chiavi riusano `chat_pratiche` |
| Scrittura atomica | `scrittura`, `archivio`, `notifiche_scrittura` |
| Letture e contatori | `lettura`, `notifiche_lettura`, `attenzione`, `paginazione`, query in `sql/` |
| Distribuzione e recupero | `eventi`, `consegne`, `quorum`, `socket_operazioni`, `presenza` |
| Risorse e limiti | `esecutore`, `risorse`, `uscita`, `limite_ingresso`, `transazioni` |
| Lavori periodici | `bridge_notifiche`, `manutenzione`, `avvio` |

Configurazione unica in `chat_pratiche/configurazione.py`, condivisa con la
chat Università. I router validano il contratto e orchestrano il dominio;
ogni invio commette messaggio, ricevuta, grant, orario, notifiche e coda in
un'unica transazione MariaDB. Il namespace generale sostituisce
`/chat-universo/`, che non è più esposto.

## Autenticazione

Le API Università mantengono cookie HttpOnly, CSRF e secondo fattore del login.
Il contratto realtime esterno usa Bearer JWT HS256 e refresh token per
conservare il protocollo del client esistente. Login, verifica delle credenziali
e limiti ai tentativi girano nello stesso backend; nessuna password viene
inoltrata a un secondo servizio. Il login realtime è limitato a questo
namespace: non produce cookie applicativi e non sostituisce il secondo
fattore richiesto dal login Università.

Un access token è valido solo con firma, issuer, audience e scadenza corretti,
una sessione persistente non revocata e un'identità ancora corrispondente a
utente, cliente unico, azienda, ruolo e dispositivo. Disattivazione, cambio
identità o password rendono inutilizzabile la sessione. Una revoca rilevata
viene conservata anche quando la richiesta termina con 401.

Il refresh ruota sotto lock. Riutilizzare un refresh già consumato revoca
l'intera sessione; il recupero accetta soltanto una sessione inattiva, sullo
stesso dispositivo ed entro la scadenza assoluta. Logout e altre revoche non
sono recuperabili. Il traffico socket, compresi chat, typing, ACK e presenza,
non prolunga l'inattività. La aggiornano handshake, richieste HTTP autenticate,
login e rotazioni. Ogni famiglia ammette al massimo 10000 rotazioni; il
superamento revoca la famiglia senza consumare un altro refresh.

Le origini browser sono HTTPS esplicite. La socket accetta i sottoprotocolli
`universo.realtime.v1` e `jwt.<accessToken>`; nessun token in query. Un client
nativo può omettere Origin. Il namespace realtime non accetta il cookie come
sostituto del token, e il token realtime non autorizza le API cookie.

## API

Prefisso interno FastAPI: **`/realtime`**. Con il proxy dell'applicazione il
percorso pubblico è `/api/realtime`. Risposte e chiavi conservano il lessico
del contratto Java, incluso `messaggioId` nei frame e `messageId` nello storico.

| Metodo e percorso relativo | Funzione / dati principali |
|---|---|
| `POST /auth/login` | `username`, `password`, `deviceId`; token e identità |
| `POST /auth/refresh` | rotazione di `refreshToken` |
| `POST /auth/recover` | recupero con `refreshToken` e `deviceId` |
| `POST /auth/logout` | revoca della sessione Bearer, 204 |
| `POST /crypto/key` | chiave derivata per `PERSON`, `PRACTICE` o `TICKET` |
| `GET /api/v1/conversations` | `destinationType`, `q`, `limit`, `cursor`, `includeReadState=1` |
| `GET /api/v1/messages` | `destinationType`, `conversationId`, `isPublic` per ticket, paginazione |
| `GET /api/v1/messages/read` | stato di una lista di `ids` nel dominio richiesto |
| `POST /api/v1/messages/read` | segna letto `messageId` del dominio richiesto |
| `GET /api/v1/messages/attention` | contatori di conversazioni non lette / non viste |
| `POST /api/v1/messages/attention` | `action=prepare/seen` e `snapshotId` |
| `GET /api/v1/notifications` | pagina raggruppata, filtro `operations`, contatore globale |
| `POST /api/v1/notifications` | segna letta la propria `notificationId` |
| `GET /api/v1/notifications/attention` | contatori delle notifiche non lette / non viste |
| `POST /api/v1/notifications/attention` | snapshot immutabili `prepare/seen` |
| `POST /internal/notifications` | ingresso con token produttore separato e `producerEventId` idempotente |
| `WS /ws` | chat, notifiche, presenza, typing, invalidazioni e ACK |
| `GET /health`, `GET /ready` | processo vivo; schema/lavori periodici/DB pronti |

I POST di lettura e attenzione ricevono i parametri nella query e rifiutano
un body. I cursori v2 sono firmati e legati a utente, cliente, dominio e filtri.
Le pagine hanno limite predefinito 10, massimo 100. Gli errori del namespace
usano il campo `error`; token e chiavi hanno risposte non memorizzabili in cache.

## Permessi e archivi

| Dominio | Partecipazione | Archivio esistente |
|---|---|---|
| `PERSON` | contatto esplicito non revocato, due utenti attivi con cliente unico | schema ticket, tabella `messaggio` |
| `PRACTICE` | referente/consulente oppure cliente studente/aderente/consulente; almeno due partecipanti | database principale, `messaggi` |
| `TICKET` pubblico | proprietario o uditore attivo | schema ticket, `ticket_messaggio` |
| `TICKET` privato | uditore attivo con ruolo abilitato; il proprietario da solo non basta | stessa tabella, canale distinto |

Il Nazionale non ottiene automaticamente accesso a ogni conversazione.
Le medesime ACL proteggono chiavi, invio, storico, typing e consegne pendenti.
Presenza e lista utenti si limitano ai contatti e gruppi condivisi.

Lo schema ticket è configurabile, sullo **stesso server MariaDB**: i tre
archivi partecipano alla stessa transazione. La 018 non crea né copia le
tabelle legacy e non concede contatti automaticamente. Servono archivi,
identità, permessi e metadati coerenti dello stesso ambiente; un clone isolato
non si sincronizza automaticamente con l'originale.

## Messaggi e consegne

Il client scrive solo sul canale `chat`: `CHAT`, `TYPING`, `LIST_USERS`.
`notification` è riservato al server; `system` accetta soltanto `DELIVERY_ACK`.
I frame e i body JSON sono limitati a 16 KiB (4 KiB per chiavi e recupero), con
profondità massima 32; vengono rifiutate chiavi duplicate, numeri non finiti e
tipi errati. Il contenuto in chiaro è limitato a 1000 byte
UTF-8. Nessuna API restituisce le chiavi master.

Ingresso cifrato u2, archivio u3 con ID messaggio nell'AAD: HKDF-SHA256 e
AES-256-GCM mantengono contesti, epoca, versione e distinzione pubblico/privato.
Le chiavi storiche personali e delle pratiche richiedono il grant appropriato.
Per i ticket valgono i partecipanti correnti, inclusi quelli aggiunti dopo
l'invio, sempre con ACL distinte pubblico/privato. Lo storico restituisce
anche i formati precedenti senza riscriverli. Gli orari nuovi hanno un overlay
UTC; quelli legacy usano Europe/Rome e la stessa convenzione Java: primo offset
nell'ora autunnale ripetuta, traslazione in avanti nel salto primaverile.

`clientMessageId` e ciphertext identici producono la stessa ricevuta, con la
medesima serializzazione canonica Java per l'hash. La quota di 20 nuovi
messaggi/minuto rimane propria dell'adattatore cookie delle pratiche; il
protocollo generale applica i bucket per socket del servizio originale.
Ricevute e consegne hanno conservazione di 30 giorni, coerente con il servizio
precedente; oltre questo intervallo l'ID non garantisce deduplicazione.
I messaggi, i grant, gli orari e gli stati di lettura restano conservati.

La coda SQL recupera le consegne dopo una disconnessione. L'ACK è legato a
utente e ID effettivamente inviato sulla connessione: non è una ricevuta di
lettura. Serve la conferma di tutte le connessioni attive del destinatario;
quelle nuove entrano nel quorum, quelle disconnesse ne escono. Una conferma
parziale non blocca nuove consegne. La pianificazione è per connessione, con
retry esponenziale da 5 a 300 secondi e recupero dopo riavvio.

I comandi sono ordinati per utente, anche con più socket: due worker, 256
operazioni totali ammesse, otto per utente. Le connessioni sono limitate a
2000 complessive, otto per utente e quattro per sessione di autenticazione.
Ogni socket ha un budget di 64 frame/128 KiB, con 128 MiB globali per processo;
anche i batch estratti dal DB e gli invii in corso restano conteggiati.
Il timeout di invio è 10 secondi. Un consumatore lento viene disconnesso e
recupera dall'outbox. Thread, code, lease e buffer vengono chiusi nel lifespan.

I bucket ingresso conservano capacità/ricarica Java: globale 100/50 al
secondo, CHAT 20/10, TYPING 30/15, LIST_USERS 5/1, ACK 60/30, altri 10/2.
Tre violazioni consecutive chiudono la socket; un comando ammesso azzera la
sequenza. Un errore di formato o permesso ordinario restituisce un frame di
errore e lascia utilizzabile la connessione. La scadenza JWT chiude anche una
socket silenziosa. Il container configura ping ogni 30 secondi e timeout pong
100 secondi, frame massimi 16 KiB, coda ingresso 16, compressione disattivata.

Gli snapshot di attenzione registrano gli ID esatti al momento di apertura,
così un nuovo arrivo non viene segnato visto da un'apertura precedente.
Scadono dopo dieci minuti; sono limitati a 60 attivi e 50000 elementi e lasciano
una ricevuta per 30 giorni. Gli ID sono verificati anche rileggendoli dal DB;
le ACL sono ricontrollate quando lo snapshot viene applicato.
Notifiche e letture generano invalidazioni anche
per gli altri dispositivi dello stesso utente.

Il bridge delle notifiche legacy registra una baseline iniziale, scorre batch
da 32 righe e ricontrolla anche ID precedenti, per recuperare commit arrivati
in ritardo. Gli eventi malformati vengono marcati come rifiutati. La
manutenzione elimina soltanto metadati scaduti in batch limitati.

## Configurazione e passaggio successivo

| Variabile | Impiego |
|---|---|
| `REALTIME_SCHEMA_TICKET` | archivio personale/ticket sullo stesso MariaDB |
| `CHAT_CHIAVI_FILE`, `CHAT_CHIAVE_VERSIONE` | keyring storico e versione corrente |
| `CHAT_UNIVERSO_JWT_FILE` | chiave Base64 HS256, almeno 32 byte |
| `CHAT_UNIVERSO_ISSUER`, `CHAT_UNIVERSO_AUDIENCE` | valori del protocollo condiviso |
| `CHAT_UNIVERSO_ORIGINI` | origini HTTPS ammesse per il client |
| `CHAT_UNIVERSO_INATTIVITA_SECONDI` | scadenza per inattività, predefinita un giorno |
| `REALTIME_ACCESSO_SECONDI`, `REALTIME_REFRESH_GIORNI` | 900 secondi e 30 giorni predefiniti |
| `REALTIME_PRODUCER_TOKEN_FILE` | token produttore in testo; vuoto disabilita solo l'ingresso interno |
| `REALTIME_MANUTENZIONE_SECONDI` | intervallo della pulizia/audit, predefinito 60 secondi |
| `REALTIME_MAX_CONNECTIONS*` | limiti complessivi, per utente e famiglia |
| `REALTIME_COMMAND_*`, `REALTIME_COMMANDS_PER_USER` | worker e quote della coda ordinata |
| `REALTIME_OUTBOUND_*`, `REALTIME_SEND_TIMEOUT_MILLIS` | budget uscita e timeout |
| `DATABASE_TRASPORTO`, `DATABASE_CA_FILE` | TLS MariaDB verificato; eventuale eccezione privata esplicita |

La 018 aggiunge i metadati mancanti e conserva le tabelle compatibili già
presenti. Non ha rollback distruttivo. Si applica dopo la 017 e prima di usare
il backend aggiornato, seguita dalla **019** per il quorum persistente delle
connessioni. All'avvio il preflight verifica sempre schema e chiavi,
rifiutando configurazione incompleta e colonne legacy troppo corte per il
ciphertext. API, socket e invio messaggi sono disponibili con la normale
configurazione del backend; autenticazione e permessi restano obbligatori.
Chiavi e token sono file privati montati in sola lettura; non vanno inclusi
in Git, negli esempi o nei log.

In ogni ambiente servono migrazioni, archivi e chiavi coerenti prima dell'avvio
del backend. In locale si usa un archivio isolato. La successiva integrazione
di Universo richiederà backup e scelta dell'archivio condiviso, verifica delle
chiavi storiche, client sul solo `/api/realtime` e passaggio coordinato di tutti
i writer e dei produttori di notifiche. Il rollback dovrà conservare dati e
chiavi e riportare insieme client e servizio alla versione precedente.
Il collaudo fra applicazioni pubblicate resta separato dalle prove locali.
Tempi di risposta, RTT e throughput sono esclusi dal confronto richiesto;
le scadenze di sicurezza e i limiti di risorse fanno invece parte del contratto.

## Verifiche riproducibili

`scripts/verify-local.ps1 -Gate All` esegue la suite FastAPI/React sul solo
MariaDB locale usa-e-getta. Le suite `test_realtime_completo.py`,
`test_realtime_isolamento.py`, `test_realtime_contratti.py`,
`test_chat_universo.py` e `test_chat_nativa.py` coprono domini, isolamento,
revoca, replay, crypto, invii concorrenti, snapshot, bridge e recupero via WS.
Le migrazioni vengono provate da zero, riapplicate e controllate nel rollback
conservativo. Le fixture contengono esclusivamente dati sintetici.

La [matrice di parità](realtime-parita.md) collega i meccanismi Java alle prove
del porting. Le suite di hardening coprono quorum, replay concorrente, code,
memoria, shutdown e TLS. `test_realtime_parita_java.py` confronta vettori
ottenuti eseguendo le classi Java originali; `test_realtime_trasporto.py` prova
il trasporto Uvicorn su loopback senza chiamare servizi esterni.

`scripts/verify-local.ps1 -Gate Docs` verifica contratto generato, configurazione,
migrazioni e documenti. Questi gate non distribuiscono nulla e non attestano
il collegamento del client Universo al nuovo backend.
