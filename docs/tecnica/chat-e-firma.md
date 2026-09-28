# Chat condivisa delle pratiche e firma

FastAPI gestisce direttamente le conversazioni delle pratiche: partecipanti,
chiavi, storico, invio e socket. Non richiede sessioni a Java e non inoltra
richieste HTTP o WebSocket a quel servizio. L'archivio resta la tabella legacy
`messaggi`, condivisa con Universo; non esiste una seconda copia dello storico.
Configurazione e limiti operativi sono descritti nelle sezioni seguenti.

## Sessione e autorizzazione della chat

Università usa la propria sessione cookie HttpOnly e il CSRF comune. La socket
verifica Origin, cookie e sottoprotocolli `ersaf.pratiche.v1` e
`csrf.<csrf_token>`; nessun token nell'URL. La sessione e i partecipanti vengono
ricontrollati prima degli invii e durante l'attesa degli eventi.

Universo usa il token di accesso che possiede già, senza un nuovo login o una
sessione delegata: FastAPI verifica HS256, issuer, audience, scadenza, identità
e revoca nella tabella condivisa `realtime_auth_session`. Il namespace
`/chat-universo/` accetta solo tale identità, mai il cookie Università.
Le sue origini CORS non ottengono accesso alle API cookie. La socket esterna
usa `universo.realtime.v1` e `jwt.<token>`, con Origin esplicita per il browser.
L'assenza di Origin è ammessa per il client nativo autenticato. Queste rotte
non emettono token né rinnovano sessioni: il login globale Universo resta
sul servizio attuale, insieme a chat personali, ticket e notifiche globali.

La partecipazione replica la regola Universo: utente referente o consulente
della pratica, oppure cliente studente, aderente o consulente. Servono account
attivi, un solo cliente per utente e almeno due partecipanti validi. Il ruolo
Nazionale da solo non concede accesso alla conversazione. ID utente e cliente
restano distinti; pratiche e utenti non vengono associati per somiglianza.

## Contratto HTTP e WebSocket

| Percorso FastAPI | Operazione |
|---|---|
| `GET /pratiche/{id}/messaggi?cursor=…` | storico decifrato, pagine da 30 |
| `POST /pratiche/{id}/messaggi/prepara` | valida 1000 byte UTF-8 e prepara u2 |
| `WS /pratiche/{id}/messaggi/socket` | invio ed eventi della sola pratica |
| `GET /chat-universo/api/v1/messages` | storico cifrato nel contratto Universo, solo PRACTICE |
| `POST /chat-universo/crypto/key` | chiave derivata per una pratica autorizzata |
| `WS /chat-universo/ws` | eventi PRACTICE e conferme di consegna |
| `GET /pratiche/{id}/firma` | anteprima e versione della firma |
| `PUT /pratiche/{id}/firma` | salvataggio PNG con controllo versione |

Il proxy pubblico mantiene il prefisso `/api`; Nginx lo rimuove prima di
inoltrare a FastAPI e gestisce Upgrade/Connection. I frame sono limitati a
4096 byte. I cursori sono firmati e legati a utente e pratica.

`partecipanti.py`, `chiavi.py`, `scrittura.py` e `storico.py` sono il dominio
comune ai due trasporti. Una sola transazione salva messaggio u3, ricevuta
idempotente, orario UTC, grant, consegne e notifiche legacy. La notifica contiene
il ciphertext, mai il testo in chiaro; il distributore notifiche Universo
esistente la rileva. Le API globali di notifiche, elenchi conversazioni e
lettura restano Java e leggono le medesime tabelle. Lo storico nativo rispetta
anche gli stati di lettura in `realtime_message_state`.

I retry conservano **ID e ciphertext**. Quattro invii simultanei dello stesso
comando producono una sola scrittura; un ID riutilizzato con contenuto diverso
è rifiutato. Le ricevute si conservano quanto i messaggi, anche dopo la pulizia
della coda di consegna. Il limite persistente è 20 nuovi messaggi per utente
al minuto; i retry validi non consumano la quota. La pratica viene bloccata in
scrittura per ordinare commit ed eventi della conversazione.

Il risveglio locale è immediato; processi diversi recuperano gli eventi dal DB
ogni 500 ms. Il ritardo tra processi include quindi questa finestra: non viene
promesso un RTT misurato. La coda `realtime_delivery` recupera le consegne non
confermate dopo una riconnessione. L'ACK è idempotente, legato all'utente e agli
ID consegnati sulla connessione; non equivale a una ricevuta di lettura.
I client deduplicano per ID messaggio e ricaricano lo storico dopo il reconnect.

Cifratura: ingresso u2, archivio u3, lettura u3/u2, legacy v1 e testo precedente.
HKDF-SHA256 e AES-GCM usano gli stessi contesti/AAD di Universo. Le chiavi
storiche richiedono i grant esistenti: una chiave mancante non autorizza a
mostrare il testo. Il browser Università non riceve chiavi master o token Java.
Il client Universo riceve soltanto le chiavi di conversazione autorizzate.

Bozze e invii pendenti Università restano in memoria, mai nel localStorage.
Ricaricare o abbandonare la pagina perde una bozza non confermata. Le schede
interne Dati/Firma conservano la bozza. Solo dopo `key_epoch_stale`, quando il
server ha escluso una precedente scrittura, Riprova può ricifrare con la chiave
corrente mantenendo l'ID.

## Firma

Il componente canvas usa Pointer Events per mouse, touch e penna. La tela ha
dimensioni logiche costanti e coordinate proporzionali, indipendenti dal
layout mobile/desktop. Annulla e Cancella il disegno non modificano il database.

Il backend accetta soltanto PNG a singolo fotogramma entro 350 KB, lato massimo
2048 pixel e area massima 2097152 pixel. Rifiuta una tela vuota, normalizza il
tratto su fondo bianco e rimuove metadati. Una transazione con lock confronta
l'impronta SHA-256 della firma letta dal client: una modifica concorrente
restituisce 409. Nessuna nuova migrazione è necessaria.

La firma nuova aggiorna il blob esistente e il relativo flag di mancanza.
Il generatore PDF continua a leggere la stessa sorgente, applicandole la
pulizia e il ritaglio comuni. I documenti già scaricati non cambiano.

## Configurazione e pubblicazione

Attivazione esplicita, disabilitata di default. La firma è indipendente.

| Variabile | Significato |
|---|---|
| `CHAT_ABILITATA` | abilita dominio chat e preflight dello schema |
| `CHAT_CHIAVI_FILE` | elenco `versione=/run/secrets/chat/file`, separato da virgole |
| `CHAT_CHIAVE_VERSIONE` | versione usata per i nuovi messaggi |
| `CHAT_UNIVERSO_JWT_FILE` | chiave di verifica del token Universo dello stesso ambiente |
| `CHAT_UNIVERSO_ISSUER`, `CHAT_UNIVERSO_AUDIENCE` | emittente e destinatario attesi |
| `CHAT_UNIVERSO_ORIGINI` | origini HTTPS ammesse, separate da virgole |
| `CHAT_UNIVERSO_INATTIVITA_SECONDI` | stessa soglia di inattività del servizio Universo |

I file contengono Base64 standard: 32 byte per ciascuna chiave master, almeno
32 byte per la chiave JWT. Riutilizzare tutte le versioni storiche del dataset,
senza generare nuove chiavi per leggere messaggi esistenti. Montare in sola
lettura con permessi limitati all'utente del container. I segreti reali non
entrano nella release o nei log. Le vecchie variabili `CHAT_JAVA_*` e
`CHAT_DATASET` non sono più utilizzate.

La migrazione **017** è additiva: metadati, stato lettura e coda interoperabile,
più ricevute e limite degli invii nativi. Non ricrea `messaggi` né le notifiche
legacy. Il preflight richiede le colonne testo capaci di contenere il formato
cifrato e, per Universo, la tabella delle sessioni esistente. Non amplia né
popola automaticamente tabelle legacy. La coda può essere ripulita eliminando
solo le righe con `expires_at < UTC_TIMESTAMP(6)`; conservare grant, ricevute,
orari e stato lettura insieme allo storico. Nessun rollback con DROP delle
tabelle condivise.

Il deploy include `compose.chat.yml` solo con `CHAT_NATIVA=si` in
`shared/compose.env`: monta `shared/chat-secrets` in `/run/secrets/chat`.
Le variabili applicative vanno in `shared/api.env`. Non apre connessioni al
Java né modifica l'indirizzo del database.

Passaggio coordinato:

1. Scegliere un unico dataset dell'ambiente: identità, clienti, pratiche,
   messaggi, grant, sessioni e notifiche devono essere gli stessi nelle due
   applicazioni. Il clone isolato di collaudo non è automaticamente tale archivio.
2. Eseguire backup, applicare 017 e verificare schema, chiavi e identità su dati
   sintetici. Configurare mount e origini, quindi pubblicare il backend.
3. Distribuire il client Universo con
   `--dart-define=PRACTICE_REALTIME_BASE_URL=https://universita.example.org`
   sostituendo l'origine con quella dell'ambiente. Il valore vuoto mantiene
   il vecchio percorso finché il passaggio non è coordinato.
4. Pubblicare il controllo del writer Java incluso nel delta, impostare
   `PRACTICE_CHAT_NATIVE=true` nel Compose Java e ricreare il servizio. Far
   ricaricare i client: i nuovi invii PRACTICE passano solo dal backend nativo. Non esiste
   fallback automatico in scrittura verso Java. Le altre chat restano lì.
5. Verificare con due account autorizzati: invio in entrambe le direzioni,
   storico precedente, modifica/revoca dei permessi, logout, reconnect,
   notifica e lettura. Le notifiche globali continuano a richiedere il Java.

Il delta Flutter è descritto in [integrazione Universo](../../integrazioni/universo-realtime/istruzioni.md).
Un rollback richiede il ritorno coordinato di entrambi i client/servizi,
conservando archivio e chiavi. Non ripristinare solo il backend mentre i client
puntano al nuovo namespace. Nessuna attivazione reale è stata eseguita durante
l'implementazione del 28 settembre.

## Verifiche

- Gate FastAPI/React `scripts/verify-local.ps1 -Gate All`, sul MariaDB locale
  usa-e-getta: firma/PDF, ACL, CSRF, invio, storico, concorrenza, limite,
  rollback atomico, revoca, grant, cursori e interoperabilità HTTP/WS.
- Derivazione delle chiavi confrontata con il vettore crittografico sintetico
  già validato da Java; nessuna richiesta HTTP al Java durante l'invio nativo.
- Suite Flutter `test/realtime`, instradamento selettivo, stesso token, nessun
  fallback e chiusura delle connessioni dopo errori.
- Gate documentazione e sintassi del bundle di deploy. Le prove locali non
  sostituiscono il collaudo bidirezionale sull'ambiente condiviso pubblicato.
