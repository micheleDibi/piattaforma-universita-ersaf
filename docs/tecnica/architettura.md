# Architettura

La piattaforma gestisce sottoscrittori, attuatori, aziende, pratiche e prodotti
formativi. Lavora sul database di un gestionale già esistente. È composta da
un'API in Python e da un'interfaccia web a pagina singola.

Questo documento descrive i pezzi e il percorso di una richiesta. Per i dettagli
rimanda ai documenti specifici:

- elenco delle API: [riferimenti/api.md](riferimenti/api.md);
- pagine del frontend: [riferimenti/rotte-frontend.md](riferimenti/rotte-frontend.md);
- variabili di configurazione: [riferimenti/configurazione.md](riferimenti/configurazione.md);
- database e migrazioni: [database-e-migrazioni.md](database-e-migrazioni.md);
- sessione, CSRF, password e limiti: [sicurezza.md](sicurezza.md);
- convenzioni di codice: [convenzioni.md](convenzioni.md).

## Stack

| Parte | Tecnologia |
|---|---|
| API | Python, FastAPI, Pydantic 2, pydantic-settings, uvicorn |
| Accesso ai dati | SQLAlchemy 2 (ORM), driver PyMySQL |
| Database | MariaDB 10.11 |
| Sicurezza | bcrypt, `webauthn` per le passkey, `segno` per il codice QR, `cryptography` |
| Documenti PDF | Typst (pacchetto `typst`), Pillow per la firma |
| SMS | servizio Skebby, chiamato con `httpx` |
| Contenuti esterni | API pubblica di EduNews24, chiamata dal backend con `httpx` e tenuta in una cache in memoria |
| Frontend | React 19, Vite, Tailwind CSS 4, React Router (pacchetto `react-router`), React Compiler, icone Lucide |
| Esecuzione | container Docker: API, frontend servito da nginx, MariaDB |

Le versioni esatte stanno in `backend/requirements.txt` e in
`frontend/package.json`.

Le operazioni DB sono eseguite nel pool di thread. Le rotte asincrone gestiscono
stream di richiesta e WebSocket e spostano il lavoro sincrono nel pool.
Anche il React Compiler è
attivo nella build del frontend. Le due regole sono in
[convenzioni.md](convenzioni.md). Una chiamata lenta a un servizio esterno
occupa uno di quei thread: il modulo EduNews24 ne limita il numero (vedi
[EduNews24](#edunews24)).

## Struttura del backend

Il codice sta in `backend/src/`, diviso per dominio. Molti moduli hanno
`models.py`, `schemas.py`, `routers.py` e un servizio, ma non è una regola:
alcuni hanno solo i modelli.

| Modulo | Contenuto |
|---|---|
| `main.py` | Crea l'app: avvio con verifica della configurazione, CORS, middleware browser, router, gestori di errore, `/salute` |
| `config.py` | Impostazioni lette da `backend/.env` e verifica di avvio |
| `database.py` | Engine, sessioni (`get_db`), base dei modelli; due connessioni facoltative in più verso database amministrativi separati, non ancora usate |
| `database_secondari.py` | Inizializzazione su richiesta delle sessioni amministrative, errori senza valori sensibili e isolamento del database di test |
| `errori.py` | Eccezioni dell'applicazione, senza dipendenze |
| `logging_config.py` | Logging con redazione dei valori sensibili |
| `auth/` | Login, sessione, logout, recupero password, impersonificazione, limiti del login, dipendenze di sessione (`dipendenze.py`), controlli di ruolo (`autorizzazioni.py`) |
| `security/` | Cookie, CSRF e controlli sulle richieste del browser (`browser.py`), sessioni, impronte dei token, password, IP e User-Agent, orologio del database |
| `mfa/` | Secondo fattore (authenticator, passkey, scelta del metodo), al login e dal profilo |
| `otp/` | Codici via email o SMS, limiti di invio, verifica dei contatti di un cliente, attivazione dell'account |
| `notifiche/` | Composizione e invio delle email, invio degli SMS, configurazione SMS |
| `edunews24/` | Proxy di sola lettura verso l'API di EduNews24: client HTTP, cache in memoria, protezioni, cursori, normalizzazione e validazione di collegamenti, immagini e video, rotte `/edunews24/...` |
| `documenti/` | PDF delle pratiche con Typst e rotte di download; `ecampus/` contiene posizioni e regole dei campi di quei moduli |
| `clienti/` | Sottoscrittori e attuatori: elenco, scheda, creazione con utente, permessi sulle pratiche |
| `utenti/` | Account di accesso |
| `ruolo/` | Tabella dei ruoli |
| `profilo/` | Profilo personale dell'utente collegato |
| `aziende/` | Aziende e dettagli dell'aderente, con filtro di visibilità |
| `aziende_xcod/` | Gerarchia delle aziende, visibilità per ruolo, azzeramento delle percentuali |
| `universita/` | Curriculum formativo del cliente |
| `listini_testa/`, `listino_tipoCorso/` | Prodotti formativi e tipi di corso |
| `pratiche/` | Pratiche, filtri dell'elenco, opzioni di ricerca; include le rotte di `documenti/` |
| `esami/` | Solo modello: esami già sostenuti dal cliente, usati dal PDF |
| `comune/` | `flag_legacy.py` (convenzione booleana) e `backfill_contatti_storici.py` (script a riga di comando) |
| `listini_*`, `nome_universita/`, `pratiche_*` | Solo modelli di tabelle esistenti: decodifiche e dati collegati |

`main.py` importa i modelli prima dei router. Serve a registrare i mapper di
SQLAlchemy: togliere quegli import rompe le relazioni dichiarate per nome.

In `pratiche/`, `models.py` contiene solo la mappatura ORM e `schemi.py` i
contratti HTTP. `rinnovi.py` centralizza la scelta di un solo anno: gli schemi
normalizzano i flag legacy e controllano il payload; il router di modifica
controlla anche i valori già salvati, sotto lo stesso blocco della pratica.

Lo script `backfill_contatti_storici.py` copia nelle nuove tabelle OTP le
verifiche dei contatti registrate dal gestionale. Si lancia da `backend/` con
`python -m src.comune.backfill_contatti_storici`. Senza opzioni non scrive
nulla; con `--applica` scrive.

## Configurazione

La configurazione è a due strati (`backend/src/config.py`): uno permissivo,
costruito all'import, e una verifica severa all'avvio dell'app. La regola e i
passi per aggiungere un'impostazione sono in [convenzioni.md](convenzioni.md).

Quello che serve sapere qui:

- I valori arrivano da `backend/.env` e dalle variabili d'ambiente.
  `get_impostazioni()` li legge una volta sola.
- La configurazione SMS (`ConfigSMS`, in `notifiche/config_sms.py`) è separata
  e si legge quando serve. Anche questa viene verificata all'avvio.
- Se `DATABASE_URL` manca, l'engine usa SQLite in memoria. Serve solo a non far
  fallire l'import: l'avvio si ferma comunque.
- `TEST_DATABASE_URL`, se impostata, ha la precedenza su `DATABASE_URL`
  (`database.py`).
- `DATABASE_URL_GESTIONE_PAGAMENTI` e `DATABASE_URL_SYS_ADMIN` preparano due
  connessioni verso due database amministrativi separati, sullo stesso server
  del database principale (stesso utente e password, nome diverso). A
  differenza di `DATABASE_URL` sono facoltative: `get_db_gestione_pagamenti()`
  e `get_db_sys_admin()` creano engine e sessioni solo alla prima richiesta.
  Un valore assente o malformato produce un errore controllato al loro uso,
  senza mostrare l'indirizzo e senza impedire l'import del backend.
  In ambiente di test, o quando è impostato `TEST_DATABASE_URL`, ignorano gli
  indirizzi ordinari: gli override `TEST_DATABASE_URL_GESTIONE_PAGAMENTI` e
  `TEST_DATABASE_URL_SYS_ADMIN` devono puntare al solo database usa-e-getta
  descritto in [Test](test.md). Non c'è ancora nessuna funzionalità che li usa.

L'elenco delle variabili è in
[riferimenti/configurazione.md](riferimenti/configurazione.md).

## Percorso di una richiesta

### 1. Middleware del browser

Prima di ogni altra cosa, un middleware HTTP in `main.py` controlla le
scritture con `verifica_richiesta_browser` (`security/browser.py`): origine,
intestazione della richiesta e `Sec-Fetch-Site`. Se un controllo fallisce la
risposta è 403, senza arrivare alla rotta. Lo stesso middleware aggiunge
`Cache-Control: no-store` dove serve. Controlli, casi del `no-store` e CORS
sono descritti in [sicurezza.md](sicurezza.md).

### 2. Dipendenze di sessione

La sessione si richiede a livello di router, così una rotta nuova nasce già
protetta; le eccezioni e la regola sono in [convenzioni.md](convenzioni.md).
L'autenticazione di ogni rotta è in [riferimenti/api.md](riferimenti/api.md).

`get_sessione_corrente` (`auth/dipendenze.py`):

1. legge il cookie di sessione;
2. valida la sessione nel database;
3. carica l'utente;
4. sulle scritture verifica il token CSRF in `X-CSRF-Token`;
5. sposta avanti la scadenza e, se è cambiata, rimanda il cookie.

Una sessione non valida dà 401 con un messaggio unico. Un CSRF errato dà 403
con codice `csrf_non_valido`. I dettagli sono in [sicurezza.md](sicurezza.md).

### 3. Router e funzione

I controlli di ruolo non sono dipendenze: le funzioni li chiamano al loro
interno (`auth/autorizzazioni.py`). La sessione del database arriva da
`get_db` e si chiude a fine richiesta.

Le regole di visibilità per clienti e pratiche sono centralizzate in
`auth/visibilita.py`; quelle delle aziende in `aziende_xcod/servizi.py`. Anche
i documenti delle pratiche applicano il filtro per azienda. Limiti di ruolo
ancora aperti: [Limiti noti](sicurezza.md#limiti-noti).

### 4. Gestori di errore

| Eccezione | Risposta |
|---|---|
| `IntegrityError` (vincolo del database violato) | 409 con un messaggio generico; il dettaglio va nel log |
| `RequestValidationError` (dati non validi) | 422; `detail` è un unico testo con i messaggi dei validatori, senza il prefisso tecnico "Value error, ", senza doppioni, separati da "; " |
| `SQLAlchemyError` | 500 con un messaggio generico; l'eccezione va nel log |
| `HTTPException` sollevata dal codice | codice scelto dal codice, corpo `{"detail": ...}` |

Le altre eccezioni non gestite diventano un 500 del framework.

Le rotte EduNews24 usano 409 anche per un cursore non valido e 503 con
`Retry-After` per un servizio esterno che non risponde: vedi
[EduNews24](#edunews24).

## Notifiche

### Email

`EMAIL_BACKEND` sceglie come escono i messaggi (`notifiche/backend_invio.py`):

| Valore | Effetto |
|---|---|
| `smtp` | Invio reale; obbligatorio in produzione |
| `file` | Scrive un file `.eml` in `backend/var/email_dev` con la configurazione predefinita |
| `console` | Scrive nel log solo le intestazioni |
| `memoria` | Tiene i messaggi in una lista; serve ai test |

I testi stanno nei template della tabella `messaggi_email`. Layout, stile e
firma stanno nel codice. La tabella legacy `mail` non viene letta.

Come partono i messaggi:

- **Recupero password.** La mail parte in `BackgroundTasks`, dopo il commit e
  fuori dal tempo di risposta. Se l'invio fallisce, la richiesta viene
  registrata con esito di errore e il token resta valido.
- **Codici OTP.** L'invio avviene dentro la richiesta
  (`otp/invio.py`). Se fallisce, la sfida viene segnata come fallita e la
  risposta è 503 con `Retry-After`.
- **Credenziali di attivazione.** Partono dopo il commit che attiva l'account
  (`otp/contatti.py`). Se l'invio fallisce l'account resta attivo e la
  risposta lo dice.

Non esiste una outbox transazionale e nessun messaggio viene ritentato in
automatico.

- Per il recupero password e per i codici OTP si ripete l'operazione.
- Per le credenziali di attivazione non è possibile: l'attesa di attivazione
  viene cancellata e l'account è già attivo (`otp/attivazione.py`). L'utente
  deve passare dal recupero password o dal referente, come dice la risposta.

### SMS

`SMS_BACKEND` sceglie l'invio (`notifiche/sms.py`):

| Valore | Effetto |
|---|---|
| `skebby` | Invio reale tramite il servizio Skebby; obbligatorio in produzione |
| `memoria` | Lista in memoria; serve ai test |
| `file` | Scrive un file JSON in `backend/var/sms_dev` con la configurazione predefinita |
| `disabilitato` | Predefinito: ogni invio fallisce |

In produzione solo `skebby` è accettato, sia all'avvio sia al momento
dell'invio.

## EduNews24

Il modulo `backend/src/edunews24/` porta nella piattaforma notizie, interpelli
e annunci di selezione del personale del portale EduNews24, in sola lettura e
senza chiave. È la seconda integrazione HTTP esterna, dopo gli SMS, e segue il
modello di `notifiche/sms.py`: client `httpx` sincrono, trasporto iniettabile
nei test, timeout brevi, nessun redirect seguito, un'eccezione propria
sollevata con `from None`. Il funzionamento visto da chi usa la piattaforma è
in [EduNews24](../funzionale/edunews24.md).

**Percorso.** Il browser chiama solo il backend, con `apiFetch`. Le rotte
`GET /edunews24/notizie`, `/edunews24/interpelli`,
`/edunews24/selezione-personale` e `/edunews24/categorie` stanno su un router
con la sessione e senza controlli di ruolo, perché i contenuti sono uguali per
tutti. Parametri e risposte sono in [riferimenti/api.md](riferimenti/api.md).
Ogni risposta ha la forma `{attiva, elementi, meta}`: `meta` porta il cursore
della pagina successiva, l'istante dell'ultimo aggiornamento e `stantio`.

`EDUNEWS24_BACKEND` sceglie la fonte (`edunews24/servizio.py`):

| Valore | Effetto |
|---|---|
| `disabilitato` | Ogni rotta risponde 200 con `attiva: false`, `elementi` vuoti e `meta` nullo, senza chiamare nessuno. È il modo di spegnere la sezione |
| `http` | Predefinito: chiamate all'indirizzo di `EDUNEWS24_URL_BASE`. Per difetto indirizzo base e host dei media sono quelli pubblici di EduNews24 (valori in `config.py`) e il contatto è l'indirizzo generico dell'ente; l'avvio controlla URL base, contatto se c'è, host dei media e valori numerici (`edunews24/verifica.py`) |
| `memoria` | Dati inventati, per sviluppo e test: i media stanno su un host `.invalid`, i collegamenti sull'host di `EDUNEWS24_URL_BASE`, che in sviluppo e nei test si imposta su un host `.invalid`. Passano da cache, normalizzazione e cursori, non dalle protezioni. Rifiutato in produzione |

**Cache** (`edunews24/cache.py`). Il processo uvicorn è uno solo, quindi la
copia è unica per tutti gli utenti: è una cache condivisa nel senso della
RFC 9111.

- La chiave è la risorsa con i parametri in forma canonica; si salva solo la
  risposta già normalizzata.
- Una risposta resta fresca per `s-maxage` (o `max-age`) meno `Age`, al più
  un'ora. `EDUNEWS24_TTL_RIPIEGO_SECONDI` vale solo se mancano entrambi.
- `stale-while-revalidate` e `stale-if-error` sono estensioni che l'origine
  dichiara (RFC 5861): una copia scaduta si riusa mentre una sola richiesta la
  rinnova, oppure, se il rinnovo fallisce, entro `stale-if-error` e mai oltre
  `EDUNEWS24_STANTIO_MASSIMO_SECONDI`. `no-cache`, `must-revalidate` e
  `proxy-revalidate` le annullano. Se la risposta arriva già scaduta (`Age`
  oltre la freschezza), le due finestre si accorciano di altrettanto. Una copia
  servita oltre la finestra di rinnovo arriva con `stantio: true`.
- Il rinnovo manda `If-None-Match` con l'`ETag` salvato; un 304 senza
  `Cache-Control` conserva le direttive salvate (RFC 9111, sezione 4.3.4). Una
  copia di riserva che EduNews24 marca come stantia resta fresca per poco (il
  suo `s-maxage`, altrimenti 60 secondi), arriva con `stantio: true` e non
  accorcia la finestra già acquisita.
- Non si salvano le risposte `no-store` o `private`, né gli errori.
- LRU di 96 voci, al più 192 KiB ciascuna e 6 MiB in tutto, misurati come
  JSON: in memoria restano sotto i 32 MB anche nel caso peggiore.

**Protezione del pool di thread** (`edunews24/protezioni.py`,
`edunews24/servizio.py`). Una chiamata lenta occupa un thread per tutta la sua
durata, quindi:

- un semaforo non bloccante lascia al più 4 thread a chiamare o ad aspettare
  EduNews24; oltre, si risponde subito con la copia oppure con 503 e
  `Retry-After` di 5 secondi;
- una sola chiamata in volo per chiave: le altre richieste ricevono la copia
  ancora valida oppure aspettano al più 1,5 secondi, poi copia o 503. Lo stato
  del volo si toglie a fine chiamata, quindi non cresce. Senza copia, se la
  chiamata dura di più, chi aspetta riceve 503 con `Retry-After` di 5 secondi
  mentre la chiamata riesce: in produzione succede solo con richieste
  contemporanee sulla stessa chiave, in sviluppo anche al primo caricamento
  (vedi [Sviluppo locale](sviluppo-locale.md));
- un budget di 30 chiamate al minuto per tutta l'applicazione, configurabile
  fino a 40 (`EDUNEWS24_RICHIESTE_AL_MINUTO`): il limite di EduNews24 è per
  indirizzo IP e conta anche i 304. A budget esaurito, copia oppure 503 con
  l'attesa fino al posto successivo, al più un minuto;
- dopo un guasto (rifiuto con 429 o 503, timeout, rete, altri 5xx, 404,
  risposta non valida o troppo grande) le chiamate si sospendono. Il primo
  `Retry-After` valido si rispetta alla lettera; senza, vale
  `EDUNEWS24_PAUSA_RIPIEGO_SECONDI`. Ai guasti consecutivi la pausa di ripiego
  raddoppia, senza scendere sotto il `Retry-After` ricevuto, fino a un'ora; la
  prima risposta riuscita azzera il conteggio. Durante la pausa si serve la
  copia oppure 503 con i secondi che restano;
- un altro 400 di EduNews24 è una deriva del contratto, non un guasto: copia
  oppure 503, senza pausa;
- nessun thread in background e nessun nuovo tentativo in ciclo: il rinnovo lo
  fa la richiesta che trova la copia scaduta;
- la scadenza totale (`EDUNEWS24_TIMEOUT_TOTALE_SECONDI`) si controlla
  all'arrivo delle intestazioni e durante la lettura del corpo. Prima valgono
  solo il timeout di connessione e quello di lettura, che conta ogni singola
  attesa: intestazioni mandate a pezzi o una serie di risposte 1xx non hanno
  una scadenza complessiva, e la risoluzione dei nomi non ha un timeout di
  `httpx`. Il limite garantito è il semaforo.

Il filtro per categoria si controlla sull'elenco delle categorie, caricato con
le stesse protezioni: una categoria sconosciuta riceve 400, e senza elenco la
risposta è 503. A cache fredda la richiesta parallela di
`/edunews24/categorie` aspetta questa chiamata e può ricevere 503: dopo un
errore la pagina la ripete una volta sola all'arrivo delle notizie e a ogni
cambio di filtro o di scheda, mai in ciclo
(`frontend/src/hooks/useCategorieEduNews24.js`). Negli interpelli l'area `nazionale` riceve 400 senza chiamare
EduNews24, che per gli interpelli non ha un filtro nazionale
(`edunews24/servizio.py`): [riferimenti/api.md](riferimenti/api.md) la elenca
comunque, perché interpelli e selezione condividono l'elenco delle aree
(`Area` in `edunews24/schemi.py`).

**Cursori** (`edunews24/cursori.py`). Il backend accetta solo i cursori che ha
estratto da `links.next`, legati alla risorsa e ai filtri con cui sono nati, in
una LRU di 2048 voci; `links.next` non si segue mai. Un cursore sconosciuto o
fuori forma riceve 409 senza chiamare EduNews24; uno rifiutato a monte si
dimentica e riceve 409, e la pagina che l'aveva emesso perde la freschezza,
così la ripartenza la rilegge. Il frontend riparte dalla prima pagina una volta sola,
poi mostra l'errore. Nel resto dell'API il 409 è un vincolo del database: il
frontend lo interpreta in base alla rotta.

**Normalizzazione e log** (`edunews24/normalizza.py`, `edunews24/url.py`). Si
inoltrano solo i campi che l'interfaccia usa, con i testi ripuliti e troncati.
Collegamenti, immagini e video si validano e non si riscrivono: vedi
[sicurezza.md](sicurezza.md#contenuti-di-edunews24). Una voce che non passa i
controlli si scarta da sola; solo una forma sbagliata del corpo è un guasto. Il
logger `ersaf.edunews24` registra solo risorsa, esito, stato HTTP, durata e
secondi di pausa; `httpx` e `httpcore` stanno a WARNING.

**Rete.** In locale il backend esce direttamente verso Internet, quindi con i
predefiniti chiama l'API vera. In collaudo serve la rete dedicata, attiva per
impostazione predefinita: vedi [deploy.md](deploy.md#edunews24).

**Frontend.**

- `lib/edunews24.js`: date nel fuso Europe/Rome, stato delle scadenze, gruppi
  per giorno, aree, filtri, impaginazione e lettura delle risposte;
- `lib/edunews24Api.js` e `lib/edunews24Paginazione.js`: chiamate con testi
  d'errore propri, `Retry-After` letto con `secondiAttesa` di
  `lib/erroriApi.js`, 409 come cursore non più valido con una sola ripartenza
  dalla prima pagina;
- `lib/videoEsclusivo.js`: un solo video in riproduzione alla volta, e un
  player smontato che smette di scaricare il file;
- un hook per il riquadro della Dashboard (`useModuloEduNews24`) e uno a
  cursore per la pagina (`usePaginaEduNews24`), più quelli di supporto per
  categorie, esito della funzione, attesa prima di riprovare, scheletri e
  fascia scorrevole;
- i componenti in `components/edunews24/`. L'identità visiva
  (`config/tokens/edunews24.css`, `config/styles/edunews24.*`) vale solo dentro
  `.edunews24`.

## PDF delle pratiche

Il modulo `backend/src/documenti/` produce il documento stampabile di una
pratica.

**Rotte.** `GET /pratiche/{id}/documento/disponibile` e
`GET /pratiche/{id}/documento`. Sono incluse nel router delle pratiche, quindi
hanno la stessa autenticazione. Entrambe applicano anche
`condizione_azienda`: il Nazionale vede tutto, gli altri la propria azienda;
un documento fuori portata risponde 404 come una pratica inesistente.

**Scelta del modulo** (`documenti/modelli.py`). Il modulo dipende dall'ente e
dal tipo di corso del prodotto formativo della pratica. Il confronto usa le
descrizioni in forma normalizzata, non gli id, perché gli id delle decodifiche
possono cambiare fra il gestionale e le sue copie. I moduli registrati stanno
in `MODELLI`, con 13 moduli per eCampus, SSML, Link e Avatar4University.
La matrice è nella [guida alle pratiche](../funzionale/pratiche.md#quando-è-disponibile).
Non ci sono fallback per tipi senza un originale documentato.
I corsi speciali SSML sono associati esplicitamente a `ssml-formazione`,
condividendo la composizione dei corsi di formazione e alta formazione.

Se non c'è un modulo, la verifica risponde `disponibile: false` e il download
risponde 404.

**Dati** (`documenti/dati.py`). I valori arrivano al modulo come testo già
formattato:

- i segnaposto del gestionale (testi vuoti o "/", la data 31/12/1999)
  diventano testo vuoto;
- i caratteri di controllo e invisibili vengono tolti, perché il PDF/A li
  rifiuta;
- gli esami sostenuti arrivano dal modello `esami`;
- `corsi_richiesti.py` legge fino a sei insegnamenti dalla scheda
  `pratiche_corsisingoli` più recente per id, oppure i tre legami legacy della
  pratica se la scheda non esiste; non usa gli esami come corsi richiesti;
- la firma perde l'intestazione del gestionale e viene ritagliata sul tratto con
  Pillow (`documenti/firma.py`).

**Impaginazione centralizzata.** Le pagine originali sono immagini, i campi
sono dati dichiarativi. Non esiste un generatore separato per ogni ateneo.

- `impaginazione.py` definisce testo, griglia, casella, firma e copertura di una
  scritta prestampata obsoleta. Le coordinate sono millimetri sull'A4.
- `moduli.py` carica la sequenza da `modelli/<nome>/pagine.json` e i campi da
  `modelli/layout/*.json`; riusa le pagine già calibrate in `ecampus/pagine.py`.
- `valori_moduli.py` estende il mapping comune di `ecampus/valori.py` con date,
  titoli e insegnamenti richiesti. Le regole non vivono nei template Typst.
- Gli sfondi identici sono condivisi in `modelli/_comune/sfondi/`. Le tabelle
  SSML riusano un solo layout con CFU; le coordinate diverse degli altri
  originali restano specifiche del modulo.
- `modelli/_comune/impaginato.typ` è l'unico disegnatore: adatta il testo alla
  larghezza; una griglia troppo corta diventa testo completo sulla stessa riga.
  Non tronca i valori e non li manda a capo sopra altre etichette.
- `moduli.py` aggiunge una pagina senza sfondo per gli insegnamenti oltre le
  righe del modulo eCampus o Link. SSML contiene già sei righe.
- `modelli/fonti.json` conserva percorso nell'archivio e SHA-256 degli originali
  usati. Gli originali sono quelli forniti: il codice non ne aggiorna condizioni,
  privacy o coordinate di pagamento. Solo l'anno prestampato del modulo Link
  singoli è sostituito con quello della pratica.

**Un modulo nuovo** richiede sfondi, layout, sequenza di pagine e associazione
ente/tipo in `MODELLI`. Una regola nuova sui dati va nel mapping comune,
soltanto se non è già rappresentata. Il modulo eCampus lauree conserva la sua
sequenza verificata; usa lo stesso motore e le stesse primitive.

**Rateizzazione eCampus.** `Modello.compila` compone il modulo e gli allegati
previsti per l'ente in un unico punto. `documenti/dilazioni.py` mappa la tabella
legacy `dilazioni_pagamenti_ecampus`; `dati_pratica` la legge solo per eCampus,
dopo il controllo di visibilità della pratica. Include le righe con
`dilazione_tassa` zero o NULL, ordinate per data e ID, e formatta gli importi
Decimal senza ricalcolare il piano. I segnaposto delle date diventano vuoti.

`ecampus/rateizzazione.py` usa un solo JPG condiviso per tutti i moduli eCampus.
Le prime dodici rate occupano le colonne dispari/pari del modulo originale;
le ulteriori rate proseguono su pagine da 24 righe. Nessun accordo viene aggiunto
senza rate. Prezzo e data dell'accordo provengono dalla pratica; le tasse
prestampate non sono ricostruite dalle righe escluse. Il percorso legacy del
file e il flag dei dati mancanti non attivano né sostituiscono il piano.

Non sono richieste migrazioni, dipendenze o variabili di ambiente nuove:
la tabella delle dilazioni esiste già nel database legacy.
Le verifiche sono in `tests/unit/test_documenti_moduli.py`,
`tests/unit/test_documenti_rateizzazione.py` e
`tests/integration/test_documento_pratica.py`; si usano solo dati sintetici.

**Motore** (`documenti/motore.py`):

- un modulo è una cartella di `documenti/modelli/` con `modulo.typ` e le
  immagini delle pagine; il nome è in minuscolo con trattini;
- la cartella viene copiata una volta in una cache sotto la cartella
  temporanea, perché il container dell'API è in sola lettura tranne `/tmp`;
  a ogni composizione la cache si confronta con il modello, file per file con
  la dimensione, e se la pulizia dei temporanei ne ha tolto qualcuno si rifà
  in una copia nuova che prende il suo posto (quella incompleta va da parte;
  se un altro processo l'ha già rifatta, resta la sua);
- i dati arrivano a Typst come JSON; la firma arriva come file in una
  sottocartella cancellata alla fine;
- per i PDF, `esecuzione.py` avvia `compilatore.py` in un processo breve:
  le cache native vengono liberate alla sua uscita. Le compilazioni sono
  serializzate per processo API e limitate a 60 secondi; dati su stdin,
  risultato binario su stdout, nessun dato negli argomenti di processo;
- i font vengono solo da `documenti/font/`, mai dal sistema, così il PDF è
  uguale su ogni macchina;
- l'uscita è PDF/A-2b; `componi_png` produce le pagine in PNG per controllare a
  occhio la posizione dei campi.

**Errori.** Se la composizione fallisce la risposta è 500. Il log riporta solo
la pratica e il modulo, nessun dato personale. Per i PDF registra anche la
causa del compilatore ridotta a una categoria, per esempio «file mancante nella
cache del modello» o il tipo dell'errore, mai il testo dell'errore, che può
citare il modulo e i dati.

**Risposta.** Il PDF arriva come allegato, con nome `pratica-<numero>.pdf` e
`Cache-Control: no-store`.

**Frontend.** La scheda della pratica chiede se il documento è disponibile e
mostra il pulsante solo in quel caso
(`components/pratiche/AzioneDocumento.jsx`, `hooks/useDocumentoPratica.js`).
Il download usa la sessione, riceve il file e lo salva con il nome dato dal
server (`lib/documentoPratica.js`). Se la verifica fallisce, il pulsante resta
nascosto.

## Frontend

### Cartelle

`frontend/src/` contiene:

- `App.jsx`: le rotte. Le pagine pubbliche stanno fuori dal guscio; le altre
  stanno sotto `RichiediSessione` e `GuscioApplicazione`.
- `components/`: pagine e schede in radice, più le sottocartelle:
  - `shell/`: guscio, menu, guardie di sessione, pagina di dettaglio;
  - `accesso/`: login, secondo fattore, reimpostazione della password;
  - `profilo/`: profilo personale e sicurezza;
  - `shared/`: elementi comuni di elenchi e schede, dialoghi, stati di
    caricamento, avvisi;
  - `pratiche/`: sezioni della scheda pratica e pulsante del PDF;
  - `contatti/`: campo contatto e dialogo di verifica;
  - `dashboard/`: scorciatoie della Dashboard;
  - `edunews24/`: riquadro della Dashboard e pagina EduNews24.
- `config/`:
  - `routes/`: percorsi, voci di menu, parametri di query;
  - `testi/`: testi dell'interfaccia;
  - `styles/`: classi Tailwind e fogli CSS;
  - `tokens/` e `theme/`: palette, misure, movimento, colori, tipografia,
    importati da `index.css`;
  - `edunews24.js`: dati di EduNews24 (sezioni, regioni, costanti), compresi
    gli indirizzi dei profili social;
  - `icone.js`: unico punto di import di Lucide; ESLint lo impone. Le icone dei
    marchi social, che Lucide non ha, sono SVG in `assets/edunews24/` usati
    come maschera CSS: vedi [convenzioni.md](convenzioni.md#icone).
- `lib/`: logica senza React (chiamate API, sessione, errori, dati dei moduli,
  righe degli elenchi).
- `hooks/`: hook che collegano `lib/` ai componenti.
- `assets/`: immagini, il logo di EduNews24 e le icone dei marchi social.

### Sessione e chiamate

- Il token di sessione sta in un cookie HttpOnly. Il frontend non lo vede.
- In memoria restano solo id, ruolo, username, nome, cognome e token CSRF
  (`lib/sessione.js`).
  Niente `localStorage`: le chiavi di versioni precedenti vengono cancellate.
- Dopo un ricaricamento la sessione si rilegge da `GET /auth/session`
  (`lib/api.js`).
- `apiFetch` (`lib/api.js`) usa `VITE_API_BASE_URL` come base e
  `credentials: "include"`. Manda sempre `X-ERSAF-Request: 1` e, sulle
  scritture, `X-CSRF-Token`.
- Su un 401 pulisce la sessione, salva la pagina corrente e torna al login:
  dopo l'accesso si torna lì, altrimenti alla pagina d'arrivo `ROTTA_INIZIALE`,
  la Dashboard (`lib/ritornoAccesso.js`).
- `lib/erroriApi.js` traduce le risposte in messaggi. Per ogni 5xx mostra un
  messaggio generico; per il 429 usa `Retry-After`.
- Le chiamate a EduNews24 hanno testi d'errore propri, leggono `Retry-After`
  con `secondiAttesa` e trattano il 409 come cursore non più valido; il 401
  resta ad `apiFetch`.

### Pagine, menu e versione

- Pagine e voci di menu: [riferimenti/rotte-frontend.md](riferimenti/rotte-frontend.md).
- Nascondere una voce dal menu non protegge la pagina: vedi
  [Limiti noti](sicurezza.md#limiti-noti).
- Testi, stili, icone e durate hanno regole proprie: [convenzioni.md](convenzioni.md).
- Il numero di versione in fondo al menu viene da `VITE_VERSIONE` e
  `VITE_AGGIORNATA_IL` (`lib/versione.js`), impostate al deploy:
  [deploy.md](deploy.md).

## Database legacy

Il backend lavora sul database di un gestionale preesistente, costruito con la
piattaforma Instant Developer.

- Le tabelle esistenti sono mappate dai modelli così come sono.
- Le tabelle nuove (sessioni, recupero password, limiti del login, codici OTP,
  secondo fattore) nascono dalle migrazioni SQL.
- L'applicazione non crea tabelle da sola.

Nelle tabelle legacy il vero vale -1 (in alcune colonne 1) e il falso 0. La
conversione è centralizzata in `backend/src/comune/flag_legacy.py` e in
`frontend/src/lib/flagLegacy.js`. Le regole d'uso sono in
[convenzioni.md](convenzioni.md).

Schema, migrazioni e debito tecnico: [database-e-migrazioni.md](database-e-migrazioni.md).

## Deploy in breve

- **API.** Immagine da `backend/Dockerfile`: uvicorn sulla porta 8000, dietro
  proxy.
- **Frontend.** Immagine da `frontend/Dockerfile`: build di Vite con
  `VITE_API_BASE_URL=/api`, poi nginx serve i file statici e inoltra `/api/`
  all'API togliendo il prefisso.
- **Database.** MariaDB in un container.
- **Composizione.** I servizi sono descritti in `deploy/compose.yml`.
- **Uscite di rete.** L'API sta su reti interne; un'uscita verso Internet
  esiste solo con le notifiche reali o con l'uscita EduNews24, ciascuna su un
  bridge dedicato con regole di firewall installate dal deploy. L'uscita
  EduNews24 è attiva per impostazione predefinita e si collega dopo che il
  deploy ha installato le sue regole; ammette solo HTTPS verso indirizzi
  pubblici e il DNS verso i nameserver dell'host
  ([deploy.md](deploy.md#edunews24)).

La pubblicazione parte da Windows con `scripts/deploy.ps1` e usa gli script in
`deploy/remote/`. Le migrazioni si applicano prima dell'attivazione. Se
l'avvio o la verifica della nuova release falliscono, lo script prova a
riattivare la release precedente; le migrazioni già applicate restano.
Procedura completa: [deploy.md](deploy.md).


## Chat delle pratiche e firma

Il modulo `chat_pratiche` gestisce nativamente sessione, partecipanti, cifratura
e scrittura nell'archivio legacy condiviso della conversazione. HTTP e WebSocket sono limitati
alla pratica autorizzata; la firma usa il blob esistente e il generatore PDF comune.
Contratto, configurazione e decisioni sono in [chat e firma](chat-e-firma.md).

Il modulo `realtime` centralizza tutte le funzioni del servizio condiviso:
sessioni Bearer, conversazioni personali/pratiche/ticket, notifiche, presenza,
letture e consegne persistenti. La scrittura cookie delle pratiche è un
adattatore dello stesso dominio. Nessuna chiamata al servizio Java;
coordinamento fra worker su MariaDB, schemi legacy sullo stesso server.
Il servizio completo parte con il backend: preflight, API, WebSocket e lavori
periodici non dipendono da flag o dall'integrazione del client Universo.
Contratto, migrazioni 018/019 e configurazione in [realtime](realtime.md).
Il confronto dei meccanismi con il servizio precedente è tracciato nella
[matrice di parità](realtime-parita.md): esecutori limitati, invii serializzati,
quorum delle conferme, conservazione degli archivi e protezioni crittografiche.

`database_trasporto` centralizza le opzioni PyMySQL del DB principale e dei
secondari: pool di otto connessioni senza overflow, acquisizione e connessione
entro cinque secondi, lettura/scrittura entro dieci. In produzione richiede
TLS con CA esplicita e verifica dell'host; l'eccezione non cifrata è ammessa
solo con una scelta esplicita e indirizzi privati letterali. Le connessioni
secondarie restano lazy. La policy viene applicata prima dell'handshake,
senza includere credenziali nei messaggi d'errore. Dettagli in [deploy](deploy.md).
