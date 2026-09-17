# Variabili di configurazione

> Pagina generata da `python scripts/documentazione/genera.py` a partire da `backend/src/config.py`, `backend/src/notifiche/config_sms.py`, i file `.env.example` e gli script di `deploy/`.
> Non modificarla a mano: rilancia il comando dopo aver cambiato le fonti.

Nomi, valori predefiniti e obbligatorietà delle variabili. I valori reali non compaiono mai: i segreti sono indicati con "—". Come preparare l'ambiente: [sviluppo locale](../sviluppo-locale.md) e [deploy](../deploy.md).

## Backend (`backend/.env`)

Letto da `backend/src/config.py`. "Obbligatoria" indica le variabili senza le quali la verifica di avvio rifiuta di partire, ricavate dal codice: "sì" in ogni ambiente, "in produzione" solo con `ERSAF_ENV=produzione`. La verifica controlla anche coerenza e formato di altri valori.

| Variabile | Tipo | Predefinito | Obbligatoria | Descrizione |
|---|---|---|---|---|
| `ERSAF_ENV` | sviluppo \| test \| produzione | `sviluppo` | no | sviluppo \| test \| produzione In "produzione" la verifica di avvio diventa piu' severa: pretende EMAIL_BACKEND=smtp, FRONTEND_BASE_URL in https e nessun '*' nei CORS. |
| `DATABASE_URL` | testo | (vuoto) | sì | Nessun valore di default nel codice: prima c'era un fallback con credenziali di prova cablate che, in assenza di .env, faceva connettere l'app senza dirlo a nessuno. La verifica di avvio rifiuta ancora quel valore. |
| `PASSWORD_RESET_TOKEN_PEPPER` | testo | (vuoto) | sì | Nel database non finisce mai un token in chiaro: solo SHA-256(token\|\|pepper). Il pepper sta qui e NON nel database, cosi' chi legge un backup non puo' derivare i token. PASSWORD_RESET_TOKEN_PEPPER, SESSION_TOKEN_PEPPER e TOTP_CHIAVE devono essere diversi fra loro e lunghi almeno 32 byte. |
| `SESSION_TOKEN_PEPPER` | testo | (vuoto) | sì | Nel database non finisce mai un token in chiaro: solo SHA-256(token\|\|pepper). Il pepper sta qui e NON nel database, cosi' chi legge un backup non puo' derivare i token. PASSWORD_RESET_TOKEN_PEPPER, SESSION_TOKEN_PEPPER e TOTP_CHIAVE devono essere diversi fra loro e lunghi almeno 32 byte. |
| `TOTP_CHIAVE` | testo | (vuoto) | sì | Cifra a riposo i segreti degli authenticator (secondo fattore del Nazionale). Diversa dai pepper. Se si perde, tutti devono riattivare l'app: va nel backup dei segreti insieme alle altre due. |
| `PASSWORD_RESET_TOKEN_TTL_MINUTES` | intero | `60` | no | Durata del link di reset, in minuti. |
| `PASSWORD_RESET_RATE_LIMIT_PER_HOUR` | intero | `5` | no | Richieste di reset ammesse in un'ora, contate per indirizzo IP e per email. |
| `PASSWORD_RESET_BUDGET_MS` | intero | `900` | no | Durata minima garantita della risposta di /auth/password-reset/request, in millisecondi. Serve all'indistinguibilita': senza, il ramo "email inviata" (che fa cinque statement) e' sistematicamente piu' lento di quello "indirizzo sconosciuto" (che ne fa tre), e bastano poche decine di campioni per separarli. Va tenuto sopra il tempo reale del ramo piu' lento: se viene superato, nei log compare un warning. |
| `FRONTEND_BASE_URL` | testo | `http://localhost:5173` | in produzione | Base dell'URL del frontend: entra nel link della mail di reset. |
| `SESSION_INATTIVITA_GIORNI` | intero | `14` | no | Scorrevole: ogni uso sposta la scadenza avanti di SESSION_INATTIVITA_GIORNI e rimanda il cookie con lo stesso Max-Age; senza attivita' per quella finestra si rientra. SESSION_DURATA_MASSIMA_GIORNI e' il tetto assoluto dalla creazione: oltre, si rientra anche se si e' attivi. Il cambio password revoca comunque tutte le sessioni. |
| `SESSION_DURATA_MASSIMA_GIORNI` | intero | `90` | no | Scorrevole: ogni uso sposta la scadenza avanti di SESSION_INATTIVITA_GIORNI e rimanda il cookie con lo stesso Max-Age; senza attivita' per quella finestra si rientra. SESSION_DURATA_MASSIMA_GIORNI e' il tetto assoluto dalla creazione: oltre, si rientra anche se si e' attivi. Il cambio password revoca comunque tutte le sessioni. |
| `LOGIN_FINESTRA_SECONDI` | intero | `900` | no | Finestra entro cui si contano i tentativi, in secondi. |
| `LOGIN_TENTATIVI_ACCOUNT` | intero | `5` | no | Tentativi per account prima delle attese progressive; si azzera a ogni accesso riuscito. |
| `LOGIN_TENTATIVI_IP` | intero | `50` | no | Tentativi per indirizzo IP; include anche gli accessi riusciti. |
| `LOGIN_ATTESA_MASSIMA_SECONDI` | intero | `60` | no | Attesa massima in secondi: dopo la soglia si parte da 1 secondo e si raddoppia fino a qui. |
| `BCRYPT_COST` | intero | `12` | no | Costo bcrypt. 12 e' il valore di produzione (~250 ms per hash). Nei test viene abbassato a 4, altrimenti la suite diventa inutilizzabile. |
| `PASSWORD_MIN_LENGTH` | intero | `8` | no | Politica NIST SP 800-63B: lunghezza, non composizione. Il massimo (72 byte) non e' configurabile: e' il limite tecnico di bcrypt. |
| `WEBAUTHN_RP_ID` | testo | `localhost` | no | RP ID = il dominio senza schema ne' porta. Le passkey registrate restano legate a questo valore: cambiarlo dopo il rilascio le rende tutte inutili. Le origini ammesse (separate da virgole) devono stare sotto quel dominio e usare HTTPS fuori da localhost. In collaudo: <dominio-collaudo> e https://<dominio-collaudo>. |
| `WEBAUTHN_ORIGINI` | testo | `http://localhost:5173` | no | Origini ammesse, separate da virgole: devono stare sotto il dominio di WEBAUTHN_RP_ID e usare HTTPS fuori da localhost. |
| `WEBAUTHN_NOME` | testo | `Piattaforma Università` | no | Nome che il browser mostra quando si registra o si usa una passkey. |
| `CORS_ORIGINS` | testo | `http://localhost:5173` | no | Origini ammesse per le chiamate dal browser, separate da virgole. Con le sessioni a cookie devono essere esplicite: '*' non e' accettato. |
| `LOG_LEVEL` | testo | `INFO` | no | Livello minimo dei messaggi: DEBUG, INFO, WARNING o ERROR. |
| `LOG_FILE` | testo | `logs/app.log` | no | File di log, percorso relativo a backend/; vuoto per scrivere solo a schermo. La cartella logs/ e' esclusa da git. Un filtro di redazione toglie token, impronte, hash bcrypt ed email prima della scrittura, tracciamenti compresi. |
| `EMAIL_BACKEND` | smtp \| file \| console \| memoria | `file` | in produzione | smtp invio reale (obbligatorio in produzione) file scrive un .eml in EMAIL_FILE_DIR, per lo sviluppo console stampa solo le intestazioni memoria tiene i messaggi in memoria, per i test |
| `EMAIL_FILE_DIR` | testo | `var/email_dev` | no | Deliberatamente FUORI da logs/: in sviluppo il link contiene il token e deve restare leggibile, mentre i log non devono contenere valori sensibili. backend/var/ e' escluso da git. |
| `SMTP_HOST` | testo | (vuoto) | in produzione | Server SMTP. Le credenziali stanno qui e non nella tabella della posta della piattaforma legacy, che le tiene in chiaro e che questa applicazione non legge. |
| `SMTP_PORT` | intero | `587` | no | Porta del server SMTP. |
| `SMTP_USER` | testo | (vuoto) | no | Utente SMTP, se il server lo richiede. |
| `SMTP_PASSWORD` | testo | (vuoto) | no | Password SMTP. |
| `SMTP_FROM` | testo | (valore nel codice) | no | Mittente. Il dominio di esempio va sostituito con quello dell'ambiente. |
| `SMTP_TLS` | starttls \| ssl \| nessuno | `starttls` | no | Cifratura del canale: starttls \| ssl \| nessuno. |
| `SMTP_TIMEOUT_SECONDS` | intero | `10` | no | Timeout della connessione SMTP, in secondi. |

## SMS (`backend/.env`)

Letto da `backend/src/notifiche/config_sms.py`.

| Variabile | Tipo | Predefinito | Obbligatoria | Descrizione |
|---|---|---|---|---|
| `SMS_BACKEND` | skebby \| memoria \| file \| disabilitato | `disabilitato` | in produzione (skebby) | Canale degli SMS: skebby \| memoria \| file \| disabilitato. In produzione deve essere skebby; file e memoria servono a sviluppo e test. |
| `SKEBBY_USER_KEY` | testo segreto | (vuoto) | con SMS_BACKEND=skebby | Chiave utente Skebby: obbligatoria con SMS_BACKEND=skebby. |
| `SKEBBY_ACCESS_TOKEN` | testo segreto | (vuoto) | con SMS_BACKEND=skebby | Token di accesso Skebby: obbligatorio con SMS_BACKEND=skebby. |
| `SKEBBY_MESSAGE_TYPE` | GP \| TI | `GP` | no | GP = Classic+ con ricevuta; TI = Classic. Un solo SMS per codice. |
| `SKEBBY_SENDER` | testo | (vuoto) | no | Vuoto usa il mittente predefinito Skebby; altrimenti un alias autorizzato. |
| `SMS_FILE_DIR` | testo | `var/sms_dev` | no | Cartella in cui finiscono gli SMS quando SMS_BACKEND=file. |

## Altre variabili lette dal backend

| Variabile | Dove |
|---|---|
| `TEST_DATABASE_URL` | `backend/src/database.py` |

## Deploy (`compose.env` sul server)

Gestito dagli script di deploy; non contiene segreti. Le variabili senza descrizione non compaiono in `deploy/compose.env.example`: le scrivono gli script quando servono, e il loro significato è in [deploy](../deploy.md).

| Variabile | Dove | Descrizione |
|---|---|---|
| `ESPOSIZIONE` | `deploy/remote/00-lib.sh`, `deploy/remote/25-esposizione.sh` |  |
| `NOTIFICHE_REALI` | `deploy/remote/00-lib.sh`, `deploy/remote/26-notifiche.sh` |  |
| `RELEASE_DIR` | `deploy/compose.env.example`, `deploy/compose.yml`, `deploy/remote/70-deploy.sh` | Cartella della release attiva sul server, ricavata da RELEASE_TAG. |
| `RELEASE_TAG` | `deploy/compose.env.example`, `deploy/compose.yml`, `deploy/remote/00-lib.sh`, `deploy/remote/30-release.sh`, `deploy/remote/70-deploy.sh`, `deploy/remote/80-status.sh` | Identificativo della release attiva, scritto dallo script all'attivazione. |
| `TZ` | `deploy/compose.env.example`, `deploy/compose.yml` | Fuso orario dei container. |
| `VERSIONE_AGGIORNATA` | `deploy/compose.yml` |  |
| `VERSIONE_NUMERO` | `deploy/compose.yml` |  |
| `WEB_LAN_IP` | `deploy/compose.esposizione.yml`, `deploy/remote/25-esposizione.sh` |  |
| `WEB_PORT` | `deploy/compose.env.example`, `deploy/compose.esposizione.yml`, `deploy/compose.yml`, `deploy/remote/00-lib.sh`, `deploy/remote/10-preflight.sh` | Porta su cui ascolta il server web del collaudo. |

Variabili d'ambiente facoltative degli script sul server:

| Variabile | Dove |
|---|---|
| `ERSAF_DEPLOY_BASE` | `deploy/remote/00-lib.sh` |
| `ERSAF_DEPLOY_DOCKER_DIR` | `deploy/remote/00-lib.sh` |
| `ERSAF_DEPLOY_WAIT_LIMIT` | `deploy/remote/00-lib.sh` |
| `ERSAF_DEPLOY_WAIT_STEP` | `deploy/remote/00-lib.sh` |

## Frontend (build e sviluppo)

Le variabili `VITE_` finiscono nel codice pubblicato: non devono mai contenere segreti.

| Variabile | Dove | Descrizione |
|---|---|---|
| `ERSAF_API_PROXY` | `frontend/vite.config.js` |  |
| `VITE_AGGIORNATA_IL` | `deploy/compose.yml`, `frontend/Dockerfile`, `frontend/src/lib/versione.js` |  |
| `VITE_API_BASE_URL` | `deploy/compose.yml`, `frontend/.env.example`, `frontend/Dockerfile`, `frontend/src/lib/api.js` | URL di base dell'API FastAPI. In sviluppo il backend gira sulla porta 8000. ATTENZIONE: tutto cio' che inizia con VITE_ viene incorporato nel bundle ed e' quindi PUBBLICO. Qui ci va un indirizzo, mai una chiave o un segreto. |
| `VITE_VERSIONE` | `deploy/compose.yml`, `frontend/Dockerfile`, `frontend/src/lib/versione.js` |  |
