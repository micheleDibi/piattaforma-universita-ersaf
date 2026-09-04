# Analisi del progetto — piattaforma-universita-ersaf

Data: 2026-09-04 · Branch: `recupero-password` (parte da `Login`, commit `289af57`)
Fonti: `backend/`, `frontend/`, `dump.sql` (5,3 GB, MariaDB 10.11, 171 tabelle)

> Il documento è scritto al presente e viene **riportato al presente** a ogni
> lavoro, invece di essere allungato con un changelog: chi lo legge fra sei mesi
> deve trovarci lo stato di oggi, non la stratificazione di ciò che è stato.
> Le sezioni 1–6 descrivono la situazione **dopo** l'implementazione del
> recupero password; i numeri misurati sul dump restano quelli, perché
> descrivono i dati di produzione e non sono stati toccati.

---

## 1. Dove siamo

Le fondamenta che mancavano ci sono. L'autenticazione non è più l'header
`x-utente-id` — un intero non firmato con cui chiunque poteva impersonare
qualsiasi utente — ma un token di sessione opaco, revocabile, di cui nel
database esiste solo l'impronta. L'hashing bcrypt c'è, e le password si
convertono **una riga alla volta**, al primo accesso riuscito di ciascun utente.

Il debito che resta è dichiarato e misurabile: finché esiste
`utenti.utente_password`, il database contiene password in chiaro per ogni
utente che non ha ancora rifatto login. È una scelta consapevole — la
conversione è graduale e non chiude fuori nessuno — e l'avanzamento si legge
con `db/diagnostica/010_stato_migrazione_password.sql`. Cosa fare di chi resta
indietro è una decisione da prendere con i numeri davanti, e in `db/` non
esiste nessuno script che la esegua.

`dump.sql` (5,3 GB) era **untracked ma non ignorato**: un `git add -A`
distratto lo avrebbe committato in modo permanente, con password in chiaro,
codici fiscali, numeri di documento e date di nascita di ~3.900 persone. Ora è
escluso da `.gitignore` (regola `*.sql` più la riammissione di `db/`), ed è
verificato che non sia mai entrato nella history: non serve riscriverla.

---

## 2. Architettura attuale

**Backend** — FastAPI + SQLAlchemy 2.0 (`Mapped`/`mapped_column`), organizzato
per dominio: `clienti`, `utenti`, `ruolo`, `aziende`, `auth`, `notifiche`. Ogni
modulo ha `models.py` / `schemas.py` / `routers.py`, più `servizio_*.py` dove la
logica non sta comodamente in una funzione di rotta. `src/security/` raccoglie
le primitive trasversali: password, token, indirizzi IP, sessioni, orologio.

La configurazione è a due strati, ed è la scelta centrale di `config.py`:
`Impostazioni` è permissiva e non solleva mai — `database.py` chiama
`create_engine` a import-time, e un'eccezione lì renderebbe impossibile perfino
la raccolta dei test — mentre `verifica_configurazione()` è severa e gira nel
lifespan, elencando **tutti** i problemi in una volta.

Le route sono `def` sincrone, tranne `POST /auth/password-reset/request`: è
`async def` perché il pavimento temporale deve attendere senza occupare uno dei
40 thread condivisi da tutta l'applicazione. Il lavoro sul database resta
sincrono, dentro `run_in_threadpool`.

**Frontend** — React 19 + Vite + Tailwind 4 + `react-router` v8 (non
`react-router-dom`). Sei componenti — `Login`, `Sidebar`,
`ElencoSottoscrittori`, `NuovoSottoscrittore`, `PasswordDimenticata`,
`ReimpostaPassword` — più `src/lib/` con l'unico punto d'uscita verso l'API, la
sessione, la policy delle password e la lettura del token.

**Database** — MariaDB 10.11, 171 tabelle ereditate da una piattaforma
**Instant Developer** ancora in produzione (`aderenti.ersaf.it`). Il backend
mappa 4 tabelle su 171. Convenzione legacy pervasiva: **`-1` = TRUE, `0` = FALSE**.

**Stato delle fondamenta:**

| | |
|---|---|
| Hashing password | bcrypt costo 12, `backend/src/security/password.py`; rehash pigro al login |
| Sessioni / token | token opaco in `auth_sessione`, `Authorization: Bearer`; nel DB solo l'impronta |
| Invio email | `smtplib` in `BackgroundTasks`, template in `messaggi_email`; quattro backend (smtp, file, console, memoria) |
| Rate limiting | 5/ora per IP **e** per account, su `password_reset_richiesta` |
| Migrazioni | `db/migrations/001–008` + rollback; nessun Alembic, e il perché è in `db/README.md` |
| Test | `backend/tests/`, 179 casi (103 richiedono MariaDB) |
| `requirements.txt` | presente; il progetto si installa con un venv |
| Logging | configurato, con redazione di token, impronte, hash ed email — tracce di stack comprese |

---

## 3. Sicurezza — stato dei rilievi

**S1 · Password in chiaro — risolto per chi accede, aperto per gli altri.**
Il login converte la riga del singolo utente che si autentica: scrive
l'hash bcrypt e svuota `utente_password` con `''` (la colonna è `NOT NULL`).
Nessuna operazione massiva, mai. Le righe di chi non accede restano intatte e
continuano a funzionare come prima. `utenti.utente_salt` resta dov'è, inutile e
non usato: bcrypt genera e incorpora il proprio salt.

**S2 · Autenticazione falsificabile — risolto.** `Authorization: Bearer` con
validazione contro `auth_sessione` (query [B] della migrazione 004), che scarta
anche le sessioni di utenti disattivati e quelle nate prima dell'ultimo cambio
password. **Resta aperta l'autorizzazione per ruolo**: nessuna rotta la
verifica, e `/clienti/` è ancora completamente non autenticato.

**S3 · Stato account al login — risolto.** `utente_attivoSN` viene controllato,
con lo stesso 401 generico di una password sbagliata.

**S4 · 500 come oracolo — risolto.** Gli 869 utenti senza riga `clienti`
ricevono lo stesso 401 di una password errata. La riga `clienti` si prende con
una query esplicita e ordinata, non tramite la relazione `uselist=False`, che
con 4 utenti a due righe non era deterministica.

**S5 · Credenziali SMTP nel DB — invariato, e per scelta.** La tabella `mail`
contiene ancora host, porta e password in chiaro della casella di invio: è
un'impostazione della piattaforma legacy e non viene toccata. La nuova
applicazione non la legge: le credenziali stanno in `.env`.

**S6 · Credenziali di default nel codice — risolto.** Il fallback `root:1234` è
sparito da `database.py`, e la verifica di avvio rifiuta esplicitamente una
`DATABASE_URL` che le contenga.

**S7 · CORS — parzialmente risolto, resta aperto.** L'elenco delle origini
arriva da `CORS_ORIGINS` in `.env` invece che dal codice, e in produzione la
verifica di avvio rifiuta un `*`. Ma `allow_credentials=True` e
`allow_methods=["*"]` restano, e vanno rivisti prima di un deploy vero.

---

## 4. Qualità dei dati — quello che rompe il recupero password

Misurato sul dump, non stimato.

| Rilievo | Numero | Conseguenza |
|---|---:|---|
| Utenti totali | 4.771 | |
| Clienti totali | 3.906 | |
| **Utenti senza riga `clienti`** | **869** | nessuna email → irraggiungibili |
| Utenti con >1 riga `clienti` | 4 | relazione `uselist=False` non deterministica |
| **Username duplicati** | **6 gruppi** | include il valore `/`; il `.first()` del login è arbitrario |
| Email vuote | 43 | |
| Email malformate | 10 | es. `elgacecere@@hotmail.it`, `/` |
| **Valori email condivisi** | **40 su 105 clienti** | max 11 clienti sullo stesso indirizzo |
| Attuatori (ruoli 1,2,3,5) | 168 | perimetro della feature |
| Attuatori senza email valida | 1 | non recupererà mai la password |
| Attuatori con email condivisa | 20 | richiesta **ambigua**: non si invia |
| Attuatori disattivati | 19 | |

**Indici.** `clienti` (3.906 righe) ha **solo la PRIMARY KEY**: nessun indice su
`cliente_email`, `utente_id`, `cliente_ruolo`. La lookup centrale del recupero
password sarebbe un full scan — e un full scan è anche un canale laterale sui
tempi di risposta.

**Vincoli dichiarati ma inesistenti.** `models.py` dichiara `unique=True` su
`utente_username` e `ForeignKey` su `clienti.utente_id`, `cliente_ruolo`,
`azienda_id`. Nel DB reale **non c'è nessuno di questi vincoli**. Il codice non
può assumerli.

---

## 5. I ruoli: "attuatore" non esiste in tabella

```
0 Utente   1 Aderente   2 Regionale   3 Provinciale
4 Consulente   5 Nazionale   6 Operatore
```

Il prompt parla di *attuatori* e *sottoscrittori* come se fossero due valori.
Non lo sono. L'unico posto dove la piattaforma definisce "attuatore" è il filtro
`solo_attuatori` in `backend/src/clienti/routers.py`, che seleziona
`{Aderente, Regionale, Provinciale, Nazionale}` → **168 clienti**.

Restano scoperti **Consulente (9)** e **Operatore (0 clienti)**: non sono
attuatori e non sono sottoscrittori. Decisione presa: trattati come i
sottoscrittori — nessuna mail, stesso messaggio a video.

---

## 6. Bug funzionali

**Chiusi**

1. `auth/routers.py` → 500 sugli 869 utenti orfani: ora 401 generico.
2. `utenti/routers.py::aggiorna_utente` → lo schema del PUT non ha più
   `utente_password` né `utente_salt`, usa `exclude_unset` (prima azzerava i
   campi non inviati) e richiede autenticazione: era aperto a chiunque.
4. `Login.jsx` → il ramo `/nazionale` era **codice morto**, non solo una rotta
   mancante: per quel ruolo il backend esce prima con `requires_2fa`, quindi
   `ruolo_codice === "nazionale"` non poteva mai essere vero. Il ramo è stato
   rimosso e `App.jsx` ha un `path="*"`, perché il difetto vero era che una
   rotta assente non produce alcun segnale.
5. `Login.jsx` → il ramo `requires_2fa` viene intercettato prima di qualunque
   scrittura: niente più `"undefined"` in `localStorage`.

**Aggiunto in corso d'opera, perché il criterio "nessuna password in chiaro"
non era soddisfatto sistemando solo il PUT**

3-bis. `utenti/routers.py::crea_utente` scriveva la password in chiaro
   esattamente come il PUT. Ora applica la policy, salva l'hash e genera
   `utente_salt` lato server invece di accettarlo dal chiamante.

**Aperti**

3. `crea_utente` forza ancora `utente_padre = current_utente.utente_id`
   ignorando il valore dello schema. Se è voluto, il campo va tolto da
   `UtenteCreate`.
6. `models.py::Utente` → `utente_ultimo_login`/`_logout` sono `Date` nel modello
   e `date` nel DB, ma `UtenteResponse` li tipizza `datetime`.
7. `Utente.clienti` → `cascade="all, delete-orphan"`: cancellare un utente
   cancella il cliente. Con 4 utenti che hanno 2 righe, il comportamento è
   imprevedibile. Le tabelle nuove evitano di proposito ogni `relationship`
   verso `Utente` e si affidano ai vincoli del database.
8. Nessuna rotta `DELETE` da nessuna parte: coerente, ma la disattivazione
   logica via `utente_attivoSN` non è esposta da nessun endpoint.
9. `POST /clienti/` accetta `utente_id` dal corpo **senza autenticazione**:
   chiunque può creare un cliente attribuito a qualunque utente. Fuori dal
   perimetro di questo lavoro, ma va sistemato.

---

## 7. Cosa è stato prodotto

**Database** — `db/diagnostica/000` e `010` in sola lettura;
`db/migrations/001–008` con i rispettivi rollback; `db/test/schema_base.sql`,
che ricrea le cinque tabelle preesistenti che le migrazioni presuppongono e che
nessuna migrazione crea, più `docker-compose.test.yml` con MariaDB 10.11.
Serve MariaDB e non MySQL: le migrazioni usano `ADD COLUMN IF NOT EXISTS`
dentro `ALTER TABLE`, sintassi che su MySQL 8/9 è un errore.

La **008** è l'unica migrazione aggiunta: introduce l'esito `errore_interno`
nell'ENUM `prr_esito`. Serve perché l'endpoint di richiesta risponde 200 anche
quando qualcosa fallisce — un 500 sarebbe un oracolo — e senza quel valore la
riga di audit andrebbe persa proprio nel caso in cui serve di più.

**Backend** — `config.py` (verifica di avvio), `logging_config.py` (redazione),
`security/{password,tokens,rete,sessioni,tempo}.py`, `auth/{dipendenze,
schemas,servizio_login,servizio_reset}.py`, `notifiche/{email,backend_invio}.py`,
i modelli delle tabelle nuove e `requirements.txt`.

**Frontend** — `lib/{api,sessione,passwordPolicy,resetToken}.js`, le pagine
`PasswordDimenticata.jsx` e `ReimpostaPassword.jsx`, `.env.example`, e la
riscrittura di `Login.jsx`.

**Test** — `backend/tests/`, 179 casi. Girano su due livelli: quelli unitari
ovunque, senza Docker e senza rete; i 103 che dipendono da MariaDB vengono
saltati con un riepilogo rosso che elenca cosa **non** è stato verificato, e la
CI usa `--require-mariadb`, perché uno skip lì è un errore. Il rischio numero
uno di una suite così è essere verde per skip.

Verifiche eseguite, non solo dichiarate:

- migrazioni 001–008 su database pulito, idempotenti alla riesecuzione, e
  rollback che riporta allo stato iniziale confrontando colonne, indici,
  vincoli ed eventi;
- i quattro scenari di richiesta con **uvicorn e curl reali**: stesso codice,
  stesso MD5 del corpo, 73 byte, tempi fra 0,9033 e 0,9044 s;
- le nove mediane dei rami, misurate interlacciate: fra 156,7 e 157,9 ms;
- consumo concorrente su quattro livelli, **controllo negativo compreso** — una
  UPDATE senza le guardie nella WHERE deve consumare due volte, e lo fa: è ciò
  che rende non vacuo il test positivo;
- flusso completo in un browser reale, dal link nella mail al login con la
  nuova password.

---

## 8. Cosa resta

**Prima di andare in produzione**
1. Backup completo **verificato** — provare il restore, non fidarsi del dump.
2. Eseguire `db/diagnostica/000` sulla copia e confrontarne l'output con i
   numeri della sezione 4.
3. Applicare `001`–`008`, poi rieseguire la diagnostica.
4. Generare i due pepper e completare `.env`: senza, l'applicazione **non
   parte** (uvicorn esce con codice 3, verificato).
5. Configurare il fallback SPA sul server statico: il link della mail è un deep
   link a una rotta gestita dal browser, e senza fallback restituisce 404 —
   la feature non funzionerebbe per nessuno.
6. Dietro reverse proxy, avviare uvicorn con `--proxy-headers
   --forwarded-allow-ips=<ip del proxy>`: senza, tutte le richieste
   risulterebbero dallo stesso IP e il limite orario le bloccherebbe insieme.
   Nella configurazione di nginx, per la rotta di validazione, usare `$uri` al
   posto di `$request` nel `log_format`: la query string contiene il token, e
   nginx logga per conto suo.

**Poi**
7. Bonifica dei sei gruppi di username duplicati → `UNIQUE` (procedura nella
   migrazione 005). Finché non è fatta, quegli account **non possono accedere**:
   il login rifiuta un'identità ambigua.
8. Chiavi esterne su `clienti` (sezione facoltativa della 005).
9. Autorizzazione per ruolo e autenticazione su `/clienti/`.
10. Bonifica dell'attuatore senza email valida e dei 20 con email condivisa: per
    i primi il recupero password non funzionerà mai, per i secondi funziona ma
    il link arriva in una casella che qualcun altro legge.

**Mai**
- Nessuna riscrittura massiva delle password. La conversione a bcrypt avviene
  una riga alla volta, al login del singolo utente. Chi non accede resta
  intatto e continua a entrare come prima. L'avanzamento si legge con
  `db/diagnostica/010_stato_migrazione_password.sql`; cosa fare degli utenti
  rimasti indietro è una decisione da prendere quando i numeri saranno noti.
  Un test della suite fallisce se qualcuno introduce un `UPDATE utenti SET
  utente_password` senza un `WHERE utente_id`.

---

## 9. Decisioni che il codice non spiega da solo

Sono le cose che un lettore futuro non può dedurre leggendo i file, e che
qualcuno "semplificherebbe" rompendole.

**Il rehash pigro non tocca `utente_password_changed_at`.** Quel campo è il
cut-off della query [B] della migrazione 004, che scarta le sessioni nate prima
dell'ultimo cambio password. Valorizzarlo al login invaliderebbe la sessione
appena emessa — `DATETIME` ha risoluzione al secondo, basta che i due `NOW()`
cadano sullo stesso confine — e tutte quelle sugli altri dispositivi, al primo
accesso post-migrazione di ognuno dei 4.771 utenti. Un rehash converte il
formato, non cambia la password.

**Le tre condizioni nella `WHERE` della query [C] sono portanti.** SQLAlchemy
attiva sempre `CLIENT.FOUND_ROWS` sui dialetti MySQL — è documentato come
*hardcoded* — quindi `rowcount` conta le righe **trovate**, non quelle
modificate. Una UPDATE senza quelle guardie restituirebbe 1 anche al secondo
tentativo e il controllo di stato finirebbe fuori dall'atomicità. Un test di
controllo negativo lo dimostra.

**Il confronto della password legacy ha una guardia sulla stringa vuota.**
`utente_password` è `NOT NULL`, quindi `''` esiste davvero, e
`compare_digest("", "")` è `True`: senza la guardia si entrerebbe con la
password vuota su ogni riga già convertita.

**L'IP si impacchetta in Python, non con `INET6_ATON`.** I byte sono identici,
ma un valore non interpretabile non diventa `NULL` — e `prr_ip` è `NOT NULL` —
e gli indirizzi IPv4-mapped finiscono nello stesso contenitore degli IPv4 nudi,
mentre `INET6_ATON` ne produrrebbe due e chi passa da un proxy dual-stack
raddoppierebbe il proprio limite orario.

**Il campo `email` dello schema è `str` e non `EmailStr`.** Con `EmailStr` un
indirizzo malformato produrrebbe un 422 con il dettaglio della validazione: è
il modo più banale di bucare l'indistinguibilità, proprio nel caso che la
specifica nomina.

**Il pavimento temporale, e perché quegli endpoint sono `async def`.** I rami
differiscono di pochi millisecondi ma in modo sistematico, e poche decine di
campioni con una mediana li separano. Il ritardo sta in un `finally`, quindi
vale anche sulle eccezioni: un 500 più veloce di un 200 sarebbe esso stesso
l'oracolo. Usa `anyio.sleep` e non `time.sleep` perché esiste un solo
threadpool da 40 slot condiviso da **tutte** le route sync: quaranta richieste
concorrenti congelerebbero anche `/clienti/` e `/auth/login`.

**Il token si legge con una memoizzazione a livello di modulo, non con un
`useRef`.** Sotto `StrictMode` React invoca due volte initializer ed effetti, e
alla seconda invocazione l'URL è già stato ripulito.

**Il `<meta name="referrer">` è in `index.html` e non in un effetto.** Le
sottorisorse del documento partono durante il parsing dell'`<head>`, prima che
React monti, e una referrer policy non è retroattiva.

**La policy delle password è duplicata di proposito.** Un endpoint che la
esponesse regalerebbe l'elenco delle password vietate su una rotta non
autenticata e introdurrebbe un giro di rete su una pagina che deve disegnare le
regole subito. La deriva è sorvegliata da un test che esegue davvero il modulo
JavaScript con node e confronta gli esiti, non solo le costanti.

**La regola "diversa dall'email" non è verificabile nel browser.** Su
`/reimposta-password` il client non sa a chi appartenga il token, e farlo dire
a `validate` costruirebbe un oracolo perfetto: chiunque intercettasse un link
scoprirebbe a chi appartiene. Compare come "verificata al salvataggio".

**Il deposito della sessione è isolato in una riga.** `src/lib/sessione.js`,
costante `DEPOSITO`. Le tre chiavi devono restare nello stesso deposito: se
`utente_id` sopravvivesse al token, `NuovoSottoscrittore` salverebbe clienti
attribuiti a una sessione morta.

---

## 10. Limiti noti

Vanno detti, perché sono le prime cose che verranno segnalate come difetti.

- **Gli utenti con ruolo Nazionale non possono accedere.** Il backend esce con
  `requires_2fa` e il flusso 2FA è fuori perimetro. Non è una regressione —
  prima finivano su una pagina bianca — ma ora lo schermo lo dice.
- **I sei gruppi di username duplicati non accedono più.** È deliberato: prima
  entravano "a caso", il che era peggio. Si sblocca con la bonifica della 005.
- **Un attuatore che condivide la casella con un sottoscrittore riceve
  comunque il link**, e chi legge quella casella può reimpostargli la password.
  È la regola del §2.2 della specifica presa alla lettera: ambiguo significa
  più di un utente *idoneo*. Riguarda parte dei 20 attuatori con email
  condivisa.
- **Il token viaggia nella query string.** Nel fragment (`#token=...`) non
  verrebbe mai inviato al server né in un `Referer`, ed è strettamente meglio;
  la specifica prescrive la query string, quindi resta una proposta.
- **Nessuna route guard nel frontend.** Ogni URL è raggiungibile senza
  sessione: il token serve solo per le chiamate all'API.
- **Nessun rinnovo della sessione**: a 12 ore si viene disconnessi senza
  preavviso.
- **Il token di sessione sta in `localStorage`**, quindi è esposto a un XSS. Un
  cookie `HttpOnly` sarebbe più solido ma è incompatibile con
  `Authorization: Bearer` e porterebbe CSRF e modifiche a CORS.
- **Il rate limit non è atomico**: conteggio e inserimento sono due statement,
  quindi richieste davvero simultanee possono far passare la sesta. È un limite
  di frequenza, non un confine di sicurezza.
- **Nessuna outbox transazionale**: se il processo muore fra il commit e
  l'invio, la mail di reset si perde.
- **Un indirizzo con uno spazio iniziale è irraggiungibile.** La collation
  `utf8mb4_unicode_ci` è PAD SPACE: ignora gli spazi in coda ma non quelli in
  testa, e normalizzare la colonna annullerebbe l'indice. Va bonificato a mano
  su `clienti`.
- **Il frontend non ha test automatici.** Non esiste un test runner nel
  progetto: introdurre vitest e testing-library è una task a sé. I requisiti
  dell'interfaccia sono stati verificati a mano in un browser reale.
- **`POST /clienti/con-utente` scrive una password in chiaro, e un test
  fallisce apposta.** L'endpoint, aggiunto dopo questo lavoro, crea l'utente con
  `utente_password = f"{nome[:3]}{cognome[:3]}{utente_id}"`: la password finisce
  in chiaro nella colonna ed è **indovinabile da chiunque conosca nome e
  cognome della persona**. `test_scritture_su_utente_password_solo_dove_previsto`
  lo segnala, e resta rosso di proposito: è il segnale, non un difetto del test.
  Va sistemato passando da `hash_password()` e generando la password con
  `secrets`, restituendola una sola volta nella risposta.
- **Lo stesso endpoint imposta `utente_attivoSN = 1`**, mentre la convenzione
  legacy è `-1` = attivo e `0` = disattivo. Finché il login non controllava quel
  campo la cosa non si notava; ora che lo controlla, **gli utenti creati da lì
  non riescono ad accedere**. È una regressione che nasce dalla combinazione dei
  due lavori, non da uno dei due preso da solo.
- **L'indicatore di robustezza è un'euristica**, non una stima dell'entropia, e
  non blocca mai l'invio: NIST prescrive lunghezza, non composizione.
