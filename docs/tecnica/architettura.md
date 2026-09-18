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
| Frontend | React 19, Vite, Tailwind CSS 4, React Router (pacchetto `react-router`), React Compiler, icone Lucide |
| Esecuzione | container Docker: API, frontend servito da nginx, MariaDB |

Le versioni esatte stanno in `backend/requirements.txt` e in
`frontend/package.json`.

Le rotte dell'API sono funzioni sincrone, eseguite da FastAPI in un pool di
thread condiviso, con una sola eccezione asincrona. Anche il React Compiler è
attivo nella build del frontend. Le due regole sono in
[convenzioni.md](convenzioni.md).

## Struttura del backend

Il codice sta in `backend/src/`, diviso per dominio. Molti moduli hanno
`models.py`, `schemas.py`, `routers.py` e un servizio, ma non è una regola:
alcuni hanno solo i modelli.

| Modulo | Contenuto |
|---|---|
| `main.py` | Crea l'app: avvio con verifica della configurazione, CORS, middleware browser, router, gestori di errore, `/salute` |
| `config.py` | Impostazioni lette da `backend/.env` e verifica di avvio |
| `database.py` | Engine, sessioni (`get_db`), base dei modelli |
| `errori.py` | Eccezioni dell'applicazione, senza dipendenze |
| `logging_config.py` | Logging con redazione dei valori sensibili |
| `auth/` | Login, sessione, logout, recupero password, impersonificazione, limiti del login, dipendenze di sessione (`dipendenze.py`), controlli di ruolo (`autorizzazioni.py`) |
| `security/` | Cookie, CSRF e controlli sulle richieste del browser (`browser.py`), sessioni, impronte dei token, password, IP e User-Agent, orologio del database |
| `mfa/` | Secondo fattore (authenticator, passkey, scelta del metodo), al login e dal profilo |
| `otp/` | Codici via email o SMS, limiti di invio, verifica dei contatti di un cliente, attivazione dell'account |
| `notifiche/` | Composizione e invio delle email, invio degli SMS, configurazione SMS |
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
- i dati arrivano a Typst come JSON; la firma arriva come file in una
  sottocartella cancellata alla fine;
- i font vengono solo da `documenti/font/`, mai dal sistema, così il PDF è
  uguale su ogni macchina;
- l'uscita è PDF/A-2b; `componi_png` produce le pagine in PNG per controllare a
  occhio la posizione dei campi.

**Errori.** Se la composizione fallisce la risposta è 500. Il log riporta solo
la pratica e il modulo, nessun dato personale.

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
  - `contatti/`: campo contatto e dialogo di verifica.
- `config/`:
  - `routes/`: percorsi, voci di menu, parametri di query;
  - `testi/`: testi dell'interfaccia;
  - `styles/`: classi Tailwind e fogli CSS;
  - `tokens/` e `theme/`: palette, misure, movimento, colori, tipografia,
    importati da `index.css`;
  - `icone.js`: unico punto di import di Lucide; ESLint lo impone.
- `lib/`: logica senza React (chiamate API, sessione, errori, dati dei moduli,
  righe degli elenchi).
- `hooks/`: hook che collegano `lib/` ai componenti.
- `assets/`: immagini.

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
- Su un 401 pulisce la sessione, salva la pagina corrente e torna al login.
- `lib/erroriApi.js` traduce le risposte in messaggi. Per ogni 5xx mostra un
  messaggio generico; per il 429 usa `Retry-After`.

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

La pubblicazione parte da Windows con `scripts/deploy.ps1` e usa gli script in
`deploy/remote/`. Le migrazioni si applicano prima dell'attivazione. Se
l'avvio o la verifica della nuova release falliscono, lo script prova a
riattivare la release precedente; le migrazioni già applicate restano.
Procedura completa: [deploy.md](deploy.md).
