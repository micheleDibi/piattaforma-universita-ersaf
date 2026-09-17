# Prompt — Recupero password (piattaforma-universita-ersaf)

> Istantanea del 04/09/2026: è il prompt con cui è stato chiesto a un agente di costruire il recupero password. Non descrive lo stato attuale del progetto: per quello vedi la [documentazione](../README.md).

> I conteggi presi dal dump e il nome dello schema sono stati rimossi da questo testo, perché il repository è pubblico: al loro posto ci sono descrizioni qualitative. Le decisioni e i vincoli di allora non cambiano.

> Da incollare a un agente di sviluppo. Scritto dopo l'ispezione del codice e del
> dump: i nomi dei simboli sono reali, non vanno riverificati da zero.
> Analisi completa in `docs/ANALISI-progetto.md`.

> Nota (17/09/2026): `docs/ANALISI-progetto.md` non esiste più. Il suo contenuto, aggiornato, è distribuito nei documenti tecnici, a partire da [Sicurezza](../tecnica/sicurezza.md) e [Architettura](../tecnica/architettura.md).

---

## 0. Contesto già accertato — non riscoprirlo

Repo: FastAPI + SQLAlchemy 2.0 (`backend/`), React 19 + Vite + Tailwind
(`frontend/`), MariaDB 10.11 (`<schema>`, con molte tabelle ereditate da una
piattaforma Instant Developer ancora in produzione).
**Branch di partenza: `Login`.** Lavora su un branch nuovo che parte da lì.

> Nota (17/09/2026): il ramo `Login` era il punto di partenza di allora. Il flusso di lavoro attuale, con un ramo personale e una pull request verso `main`, è in [Convenzioni](../tecnica/convenzioni.md).

Quello che **non esiste** e che questa task deve costruire:

- **hashing**: le password in `utenti.utente_password` sono **in chiaro**;
  `utenti.utente_salt` è un UUID mai usato;
- **sessioni**: l'auth è l'header `x-utente-id`, un intero non firmato;
- **invio email**: nessun SMTP, nessuna libreria;
- **rate limiting**, **migrazioni**, **test**, **`requirements.txt`**.

> Nota (17/09/2026): oggi tutti questi elementi esistono: hash bcrypt (`backend/src/security/password.py`), sessioni revocabili (`backend/src/security/sessioni.py`), invio email (`backend/src/notifiche/`), limiti sui tentativi, migrazioni (`db/migrations/`), test e `backend/requirements.txt`. L'autenticazione non usa più `x-utente-id`: la sessione viaggia in un cookie HttpOnly e le richieste che modificano dati portano un token CSRF. Vedi [Sicurezza](../tecnica/sicurezza.md).

Convenzione legacy pervasiva: **`-1` = TRUE, `0` = FALSE** (es. `utente_attivoSN`).

### Le migrazioni SQL sono già scritte e verificate

`db/migrations/001..006` sono già pronte, applicate e annullate con successo su
MariaDB 10.11.14. Sono **solo DDL** (colonne, tabelle, indici) più due template
email: nessuna riga esistente viene modificata o cancellata. **Non riscriverle**: leggile, perché ognuna contiene in coda
le *query di riferimento* che l'applicazione deve usare (revoca, validazione,
consumo atomico, conteggio rate limit). Applicale in ordine su un DB di sviluppo
dopo aver eseguito `db/diagnostica/000_diagnostica_pre_migrazione.sql`.

> Nota (17/09/2026): le migrazioni oggi vanno oltre la 008 e non sono più solo DDL: la 009 aggiorna un flag degli utenti, la 011, la 012 e la 014 inseriscono o aggiornano modelli email. Elenco e anomalie in [Migrazioni](../tecnica/riferimenti/migrazioni.md); regole operative in [db/README.md](../../db/README.md).

Se ti servono altre modifiche allo schema, aggiungi `db/migrations/008_*.sql`
con il rispettivo `db/rollback/008_*_down.sql`. Non modificare le 001–006.

> Nota (17/09/2026): la 008 esiste (`db/migrations/008_esito_errore_interno.sql`) e dopo di lei ne sono state aggiunte altre. Vedi [Migrazioni](../tecnica/riferimenti/migrazioni.md).

### Decisioni già prese — non richiederle di nuovo

| Tema | Decisione |
|---|---|
| Campo identificativo | **solo email**, coerente con il messaggio a video |
| Hashing | **bcrypt cost 12** + **rehash pigro al login**. Vincolo esplicito: **nessuna operazione massiva sui dati esistenti** — si converte una riga alla volta, al login di quel singolo utente. Chi non accede resta intatto. |
| Sessioni | **si introducono in questa task** (token opaco, tabella `auth_sessione`) |
| "Attuatore" | `cliente_ruolo IN (1,2,3,5)` = Aderente, Regionale, Provinciale, Nazionale |
| Consulente (4) e Operatore (6) | trattati come i sottoscrittori: nessuna mail |
| TTL token | 60 minuti |
| Rate limit | 5/ora per IP **e** 5/ora per account |

---

## 1. Vincoli sui dati — determinano il comportamento, non sono note a margine

Misurati sul dump, non stimati. I conteggi sono stati rimossi da questo testo:
per rifarli serve il dump, che non sta nel repository.

- **una parte consistente degli utenti non ha alcuna riga `clienti`** → nessuna email raggiungibile.
  Sono anche le righe su cui `/auth/login` **restituisce oggi un 500**
  (`user.clienti.ruolo.ruolo_codice` su `clienti = None`). Vanno gestite.

  > Nota (17/09/2026): il 500 è stato corretto. Un utente senza riga `clienti` riceve lo stesso 401 delle credenziali errate (`backend/src/auth/accesso.py`).

- **`utenti.utente_username` NON ha `UNIQUE` nel DB** (alcuni username sono
  duplicati, e fra i valori c'è anche `/`), malgrado `models.py` dichiari
  `unique=True`. Non assumere mai che uno username identifichi un solo utente.

  > Nota (17/09/2026): il modello non dichiara più `unique=True` sullo username (`backend/src/utenti/models.py`). Il login rifiuta gli username presenti su più righe.

- **`clienti.cliente_email` non è univoca**: molti indirizzi sono condivisi fra
  più clienti, in qualche caso da parecchi. Fra questi ci sono **attuatori** che
  hanno l'email in comune con un altro cliente.
- Ci sono email **vuote** e email **malformate**, e c'è almeno un attuatore
  senza email valida.
- **Alcuni attuatori hanno `utente_attivoSN = 0`** (disattivati).
- `clienti` ha **solo la PRIMARY KEY**: la migrazione 005 aggiunge gli indici.
  La query deve confrontare la **colonna nuda** (`WHERE cliente_email = :param`)
  con il parametro normalizzato lato Python — `LOWER(TRIM(colonna))` annulla
  l'indice. La collation `utf8mb4_unicode_ci` è già case-insensitive.

  > Nota (17/09/2026): con la 005 applicata, `clienti` ha anche gli indici su email, utente e ruolo (`db/migrations/005_indici_e_integrita.sql`). Dal codice non si può sapere su quali database sia già applicata.

---

## 2. Cosa costruire

### 2.1 Fondamenta (senza queste il resto non sta in piedi)

**a) `backend/requirements.txt`** — oggi il progetto non è installabile. Almeno:
`fastapi`, `uvicorn[standard]`, `sqlalchemy>=2`, `pymysql`, `python-dotenv`,
`pydantic[email]`, `passlib[bcrypt]`, `bcrypt`, `aiosmtplib` (o `fastapi-mail`),
`pytest`, `httpx`.

> Nota (17/09/2026): `backend/requirements.txt` esiste e il progetto si installa. Il file esclude di proposito `passlib` (bcrypt si usa direttamente) e `aiosmtplib` (l'invio usa `smtplib` in un task in background). Vedi [Sviluppo locale](../tecnica/sviluppo-locale.md).

**b) `backend/src/security/password.py`**
- `hash_password(pw) -> str` — bcrypt, cost 12.
- `verify_password(pw, hashed) -> bool`.
- **bcrypt tronca silenziosamente oltre 72 byte**: rifiuta esplicitamente gli
  input più lunghi (o pre-hasha con SHA-256+base64). Documenta la scelta.
- `needs_rehash(hashed) -> bool` per un futuro aumento del cost.

**c) Rehash pigro in `/auth/login`** — riscrivi la verifica così:
1. se `utente_password_hash` è valorizzato → `verify_password`;
2. altrimenti confronta il legacy in chiaro **in tempo costante**
   (`secrets.compare_digest`) e, se corretto, scrivi `utente_password_hash`,
   `utente_password_algo='bcrypt'` e svuota `utente_password` **nella stessa
   transazione**;
3. se l'utente non esiste, esegui comunque un `verify_password` fittizio contro
   un hash costante, così il tempo di risposta non rivela l'esistenza
   dell'account.

**d) Sessioni** — token opaco `secrets.token_urlsafe(32)`, nel DB solo
`SHA-256(token || SESSION_TOKEN_PEPPER)` (tabella `auth_sessione`, migrazione
004). Riscrivi `get_current_utente` perché legga `Authorization: Bearer <token>`
invece di `x-utente-id`, e applichi la query [B] della 004 — che scarta anche le
sessioni nate **prima** dell'ultimo cambio password, come difesa in profondità
se la revoca massiva fallisse.
Aggiorna `Login.jsx`: oggi salva `utente_id` in `localStorage`.

> Nota (17/09/2026): niente `Authorization: Bearer` e niente `localStorage`. Il token di sessione viaggia in un cookie HttpOnly. Il login restituisce un token CSRF, che l'interfaccia tiene solo in memoria e rimanda nelle richieste che modificano dati. Vedi [Sicurezza](../tecnica/sicurezza.md).

**e) `backend/src/notifiche/email.py`** — invio SMTP da variabili `.env`
(`SMTP_HOST/PORT/USER/PASSWORD/FROM`, `TLS`). **Non** leggere le credenziali
dalla tabella `mail`, che le contiene in chiaro. I template vivono in
`messaggi_email` (codici `password_reset_richiesta` e `password_reset_eseguito`,
migrazione 006), segnaposto `{{nome}}`; ogni valore dinamico va escapato in HTML.
**L'invio deve essere fuori dal ciclo di richiesta** (BackgroundTasks): il tempo
di consegna SMTP non deve entrare nel tempo di risposta.

**f) `.env.example`** — aggiungi tutte le nuove variabili con valori fittizi:
`PASSWORD_RESET_TOKEN_PEPPER`, `SESSION_TOKEN_PEPPER`,
`PASSWORD_RESET_TOKEN_TTL_MINUTES=60`, `PASSWORD_RESET_RATE_LIMIT_PER_HOUR=5`,
`SESSION_TTL_HOURS=12`, `FRONTEND_BASE_URL`, `SMTP_*`.
I due pepper devono essere ≥32 byte casuali. **L'app deve rifiutarsi di
partire** se mancano o sono i valori di esempio.

> Nota (17/09/2026): `SESSION_TTL_HOURS` non esiste più. La sessione è scorrevole e la regolano `SESSION_INATTIVITA_GIORNI` e `SESSION_DURATA_MASSIMA_GIORNI` (14 e 90 giorni con la configurazione predefinita). I segreti controllati all'avvio sono tre: i due pepper e `TOTP_CHIAVE`, tutti diversi fra loro. Vedi [Configurazione](../tecnica/riferimenti/configurazione.md).

### 2.2 Endpoint

**`POST /auth/password-reset/request`** — body `{ "email": "..." }`

Ordine obbligatorio delle operazioni:
1. normalizza: `email.strip().lower()`; se non è formalmente valida, tratta come
   sconosciuta (stessa risposta);
2. controlla il rate limit (query di riferimento nella 003) **prima** di
   qualsiasi lookup;
3. risolvi l'email → utenti idonei:
   `clienti.cliente_email = :email AND cliente_ruolo IN (1,2,3,5)`, join `utenti`
   con `utente_attivoSN = -1`;
4. determina l'esito interno e registra **sempre** una riga in
   `password_reset_richiesta`:

   | Situazione | `prr_esito` | Mail |
   |---|---|---|
   | 1 attuatore attivo | `email_inviata` | sì |
   | nessun cliente con quell'email | `identificativo_sconosciuto` | no |
   | cliente non attuatore (ruoli 0, 4, 6) | `ruolo_non_abilitato` | no |
   | attuatore con `utente_attivoSN = 0` | `utente_disattivato` | no |
   | **>1 utente idoneo** sulla stessa email | `identificativo_ambiguo` | **no** |
   | limite superato | `rate_limited_ip` / `rate_limited_account` | no |

   L'esito ambiguo è obbligatorio: con più attuatori che condividono l'email,
   inviare a tutti significa mandare a Tizio il link di reset di Caio.
5. solo su `email_inviata`: revoca i token precedenti e inserisci il nuovo
   (query [A] della 002), **nella stessa transazione**; poi accoda l'invio.

Risposta: **sempre** `200` con
`{"message": "Se l'indirizzo è associato a un account riceverai una mail"}`.
Mai un codice diverso, mai un campo diverso, **mai un 429**: un 429 direbbe
all'attaccante che quell'indirizzo vale la pena insistere.

**`GET /auth/password-reset/validate?token=...`** — query [B] della 002, in
**sola lettura**. Non marcare nulla: il prefetch di un client di posta o un
crawler brucerebbe il token. Risposta `{"valido": true}` oppure
`{"valido": false, "motivo": "scaduto|non_valido|gia_usato"}`.

**`POST /auth/password-reset/confirm`** — body `{token, password, password_conferma}`

In un'unica transazione:
1. valida la policy lato server (§2.3) e la corrispondenza delle due password;
2. **consuma il token con la UPDATE condizionale** (query [C] della 002) e
   verifica `ROW_COUNT() == 1`; se è 0 → errore, password **non** cambiata.
   Due richieste concorrenti: una sola vince;
3. scrivi `utente_password_hash`, `utente_password_algo='bcrypt'`,
   `utente_password_changed_at=NOW()`, `utente_password_changed_via='reset_email'`,
   e svuota `utente_password`;
4. revoca gli altri token dell'utente (query [D] della 002);
5. revoca **tutte** le sessioni (query [A] della 004);
6. commit, **poi** accoda la mail `password_reset_eseguito`.

Non autenticare l'utente: la risposta porta al login (requisito 16).

> Nota (17/09/2026): i "requisiti" numerati citati qui e più sotto non sono elencati in nessun documento del repository.

### 2.3 Policy password

Allineata a NIST SP 800-63B: **lunghezza, non composizione obbligatoria**.

- minimo **12** caratteri, massimo **72 byte** (limite bcrypt — è un vincolo
  tecnico reale, non una preferenza);

  > Nota (17/09/2026): il minimo oggi è di 8 caratteri con la configurazione predefinita (`PASSWORD_MIN_LENGTH`, che l'avvio non accetta sotto 8); il massimo resta di 72 byte. Vedi [Sicurezza](../tecnica/sicurezza.md).

- rifiuta le password uguali all'username o all'email;
- rifiuta una blocklist minima (`password`, `ersaf`, `123456789012`, …);
- **stesse regole lato client e lato server**, con le regole visibili a schermo
  e uno stato per regola che si aggiorna mentre l'utente digita;
- **niente** obbligo di maiuscola/cifra/simbolo, niente scadenza periodica.

### 2.4 Frontend

Due rotte nuove in `App.jsx`: `/password-dimenticata` e `/reimposta-password`.
Il link in `Login.jsx` è oggi uno stub con `console.log`: collegalo.

> Nota (17/09/2026): il link non è più uno stub: porta alla pagina di recupero password.

**Pagina di richiesta** — campo email + "Invia" + "Torna al login". Dopo l'invio
mostra il messaggio generico **e disabilita il pulsante**, sempre, anche in
errore di rete: un pulsante che resta attivo solo in certi casi è un oracolo.

**Pagina di reimpostazione**:
- legge il token dalla query string, chiama `validate`;
- se non valido: messaggio d'errore + link per rifare la richiesta, **e nessun
  form** (requisito 9);
- se valido: "Nuova password" + "Conferma password", regole visibili, controllo
  di corrispondenza, indicatore di robustezza;
- **`<meta name="referrer" content="no-referrer">`** sulla pagina, e subito dopo
  aver letto il token esegui `window.history.replaceState()` per toglierlo
  dall'URL: altrimenti finisce nella cronologia del browser e nell'header
  `Referer` verso ogni risorsa esterna della pagina;
- al successo: redirect a `/` con banner di conferma del cambio.

### 2.5 Indistinguibilità — il punto su cui la feature si gioca

Il messaggio identico non basta se qualcos'altro differisce:

- **tempo di risposta**: l'invio SMTP deve essere in background; il ramo
  "utente inesistente" deve costare come quello "utente esistente" (esegui
  comunque l'hash fittizio);
- **codice HTTP e forma del body**: sempre `200`, sempre lo stesso JSON;
- **header**: nessun header condizionale (niente `Retry-After` sul rate limit);
- **log applicativi**: nessun token, nessun hash di token, nessuna email in
  chiaro nei log. Aggiungi un filtro di logging che redige i pattern dei token;
- **`prr_utente_id` NULL** quando l'identificativo è sconosciuto: non ricreare
  nel log l'oracolo che l'endpoint evita.

---

## 3. Fix obbligatori nel perimetro

Non sono extra: senza il primo, il lavoro sull'indistinguibilità è inutile.

1. **`/auth/login` restituisce 500 sugli utenti senza riga `clienti`** — gestisci
   `clienti = None` e restituisci lo stesso 401 di una password sbagliata.
2. **Il login non controlla `utente_attivoSN`** — gli utenti disattivati
   accedono. Blocca, con lo stesso 401 generico.
3. **`PUT /utenti/{id}` scrive `utente_password` in chiaro** via `setattr`
   ciclico. Togli la password da quello schema: si cambia solo dai flussi
   dedicati.
4. **`Login.jsx` naviga a `/nazionale`**, rotta non registrata → pagina bianca.
5. **`Login.jsx` non gestisce `requires_2fa`** e scrive `"undefined"` in
   `localStorage`.

> Nota (17/09/2026): i cinque punti sono stati corretti. Gli utenti senza riga `clienti` e quelli disattivati ricevono lo stesso 401 delle credenziali errate; lo schema di `PUT /utenti/{id}` non contiene più la password; il login non porta più a `/nazionale` e un indirizzo sconosciuto mostra una pagina "non trovata"; il login gestisce `requires_2fa` e non scrive nulla in `localStorage`.

---

## 4. Test

Nel repo non esiste nulla: crea `backend/tests/` con `pytest` + `httpx`, DB di
test separato (SQLite non basta — servono `INET6_ATON` e il comportamento
MariaDB: usa un DB MariaDB dedicato o marca i test che lo richiedono).

> Nota (17/09/2026): oggi i test esistono: `backend/tests/` con pytest, dove i test che richiedono MariaDB sono marcati `mariadb` e usano un database usa-e-getta, e `frontend/tests/` con il test runner di Node. Vedi [Test](../tecnica/test.md).

Casi che devono esistere:

**Indistinguibilità** — email inesistente / sottoscrittore / attuatore
disattivato / attuatore valido producono **byte per byte** la stessa risposta;
la varianza dei tempi resta sotto una soglia dichiarata.

**Token** — validazione ok; scaduto; già consumato; revocato; inesistente;
manomesso di un carattere; **consumo concorrente** (due richieste, una sola
vince); una nuova richiesta invalida la precedente.

**Rate limit** — la sesta richiesta dallo stesso IP non invia; la sesta sullo
stesso account non invia; entrambe rispondono `200` col messaggio generico.

**Password** — troppo corta; oltre 72 byte (rifiutata, non troncata);
non corrispondenti; uguale all'email; caso valido.

**Effetti collaterali** — dopo il reset: hash bcrypt presente e chiaro svuotato,
`utente_password_changed_at` valorizzato, **tutte** le sessioni revocate, la
mail di notifica accodata e **priva del token e della password**.

**Ambiguità** — email condivisa da 2 attuatori: nessun invio, esito
`identificativo_ambiguo`, stessa risposta a video.

**Rehash pigro** — login con password legacy corretta → hash scritto, chiaro
svuotato; il login successivo passa dal ramo bcrypt.

---

## 5. Fuori perimetro

Non toccare: la tabella legacy `utente_session` (la usa la piattaforma Instant
Developer); il flusso 2FA per il ruolo Nazionale; tutte le altre tabelle ereditate.

> Nota (17/09/2026): il secondo fattore per il ruolo Nazionale oggi esiste (`backend/src/mfa/`). La tabella `utente_session` resta esclusa. Vedi [Sicurezza](../tecnica/sicurezza.md).

**Non** eseguire migrazioni contro un database di produzione.

**Non scrivere nessuno script che modifichi in blocco le password esistenti**,
in nessuna forma: né un `UPDATE` massivo, né un job di conversione, né un
comando manuale. L'unica scrittura ammessa su `utenti.utente_password` è quella
della singola riga dell'utente che ha appena fatto login con successo (§2.1c) o
completato un reset (§2.2). Se pensi che serva altro, chiedi.

---

## 6. Criteri di accettazione

- [ ] Il branch parte da `Login`.

  > Nota (17/09/2026): vedi la nota sul ramo di partenza al §0.

- [ ] `pip install -r backend/requirements.txt` e l'app parte con un `.env` nuovo.
- [ ] L'app **si rifiuta di partire** se i pepper mancano o sono i valori d'esempio.
- [ ] Le migrazioni 001–006 girano su un DB pulito, sono idempotenti e i rollback
      riportano allo stato iniziale.

  > Nota (17/09/2026): oggi la suite applica e riesegue tutte le migrazioni, poi esegue i rollback presenti (`backend/tests/db/test_migrazioni.py`). La 014 non ha un rollback e quello della 009 non fa nulla. Vedi [Migrazioni](../tecnica/riferimenti/migrazioni.md).

- [ ] I quattro scenari di richiesta producono risposte identiche byte per byte.
- [ ] Un token consumato due volte cambia la password una volta sola.
- [ ] Dopo il reset, ogni sessione preesistente riceve 401.
- [ ] `grep -riE "token|password" backend/logs/` non trova valori sensibili.
- [ ] Nessuna password in chiaro scritta da nessun percorso di codice.
- [ ] Nessuno script o comando che modifichi in blocco le righe di `utenti`.

  > Nota (17/09/2026): la migrazione 009 aggiorna in blocco `utente_attivoSN` sulle righe che valevano 1. Le password restano escluse da ogni aggiornamento in blocco, e un test lo sorveglia.

- [ ] Un utente che non fa login mantiene la riga invariata e continua ad accedere.
- [ ] La suite `pytest` passa; i casi del §4 sono tutti presenti.
- [ ] `docs/ANALISI-progetto.md` aggiornato con ciò che è stato effettivamente fatto.

  > Nota (17/09/2026): `docs/ANALISI-progetto.md` non esiste più: vedi la [documentazione](../README.md).

---

## 7. Se qualcosa non torna

Le decisioni del §0 sono chiuse. Se durante l'implementazione trovi un vincolo
del codice o dei dati che le rende impraticabili, **fermati e chiedi** invece di
scegliere da solo — indicando cosa hai trovato e quali sono le alternative.

## 8. Prima di scrivere qualsiasi codice

`dump.sql` è untracked ma **non ignorato**, e pesa parecchi gigabyte. Contiene
password in chiaro, codici fiscali, numeri di documento e date di nascita di
tutte le persone in anagrafica.
Aggiungilo a `.gitignore` e verifica con `git status` che non compaia. Un
`git add -A` distratto lo committa in modo permanente.

> Nota (17/09/2026): `dump.sql` oggi è ignorato: `.gitignore` esclude tutti i file `.sql`, tranne quelli sotto `db/`.
