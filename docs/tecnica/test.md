# Test

Questo documento descrive i test del backend, del frontend e degli strumenti
della documentazione, e come lanciarli. La preparazione del PC è in
[sviluppo-locale.md](sviluppo-locale.md).

## Struttura

I test del backend stanno in `backend/tests/`:

| Cartella | Cosa contiene |
|---|---|
| `unit/` | Logica senza database: configurazione, password, token, authenticator, IP, SMS, layout delle email, dati dei clienti, PDF delle pratiche, EduNews24 (client, cache, pause, cursori, validazione di collegamenti e media, dati inventati, allineamento delle regioni) |
| `integration/` | Flussi completi con l'API e MariaDB: login, sessioni, recupero password, codici OTP, secondo fattore, clienti, filtri, conteggi e documento delle pratiche, rotte EduNews24 per i quattro ruoli |
| `security/` | Proprietà di sicurezza: rotte protette, cookie e CSRF, impersonificazione, risposte indistinguibili, log senza segreti, nessuna password in chiaro, profilo, autorizzazioni. Molti richiedono MariaDB, alcuni no |
| `db/` | Migrazioni e rollback |
| `support/` | Aiuti comuni (vedi sotto) |

`backend/tests/conftest.py` prepara ambiente e fixture per tutti.

In `support/`:

- `factories.py`: costruisce gli scenari con dati sintetici e domini riservati
  agli esempi;
- `scenari.py`: accesso di prova per i test della visibilità. Ogni aiuto svuota
  i cookie del client dopo il login e restituisce le intestazioni esplicite
  della sessione: con più utenti nello stesso test, un cookie rimasto farebbe
  partire la richiesta a nome dell'ultimo che ha fatto login;
- `sessioni.py`: cookie e CSRF per le richieste di prova;
- `sqlrunner.py`: esegue un file `.sql` intero in una sola chiamata, con più
  istruzioni;
- `autenticatore_virtuale.py`: passkey software per i test WebAuthn;
- `immagini.py`: immagini minime;
- `edunews24.py`: risposte finte di EduNews24, orologio finto e fonte finta
  per i test del modulo, su host inventati;
- `modelli/prova/`: modulo Typst di prova per il motore dei PDF.

Altri test:

- frontend: `frontend/tests/*.test.js`;
- strumenti della documentazione: `scripts/documentazione/tests/`.

## Configurazione di pytest

`backend/pytest.ini`:

- `pythonpath = .` e `testpaths = tests`: si lancia da `backend/`;
- `--import-mode=importlib` e `consider_namespace_packages`: le cartelle del
  backend in genere non hanno `__init__.py`, e due file di test con lo stesso
  nome in cartelle diverse non vanno in conflitto;
- `--strict-markers` e `--strict-config`: un marker non dichiarato o un errore
  di configurazione fermano la suite;
- `filterwarnings = error`: ogni warning è un errore. L'unica eccezione è una
  deprecazione interna a una dipendenza.

### Marker

| Marker | Significato |
|---|---|
| `mariadb` | Richiede MariaDB. Senza database il test viene saltato, salvo `--require-mariadb` |
| `timing` | Misura i tempi di risposta. Escluso per difetto (`-m "not timing"` in `addopts`); si lancia con `-m timing` |
| `lento` | Dura più di due secondi. È solo un'etichetta: non esclude nulla |

Il marker si mette sul file (`pytestmark`) o sul singolo test. Alcuni test non
marcati usano la fixture `client`: senza MariaDB vengono saltati comunque.

## conftest.py

### Ambiente preparato prima di importare `src`

L'ordine del file è vincolante. `backend/src/database.py` crea l'engine quando
viene importato, quindi l'ambiente si prepara nelle prime righe, prima di ogni
import di `src`.

Il conftest imposta:

- `TEST_DATABASE_URL`, con il container di test come valore predefinito, e la
  copia in `DATABASE_URL`;
- segreti di test, diversi dai segnaposto di `backend/.env.example`;
- `BCRYPT_COST=4`, per non rallentare la suite;
- `EMAIL_BACKEND=memoria`;
- `SMS_BACKEND=memoria`, sempre, anche se la shell ha un altro valore;
- tutte le variabili `EDUNEWS24_*`, **assegnate** e non solo proposte:
  backend `memoria`, URL base e host dei media su host `.invalid`, contatto su
  `example.org`, numeri ai predefiniti; così `backend/.env` non le porta nei
  test e nessun test chiama l'API vera, che è il predefinito del codice. I test
  dei valori predefiniti tolgono queste variabili dall'ambiente e costruiscono
  `Impostazioni(_env_file=None)`;
- frontend, CORS e WebAuthn su un dominio di esempio, un host SMTP che non
  risolve, un pavimento temporale ridotto, nessun file di log,
  `ERSAF_ENV=test`.

Tranne `SMS_BACKEND`, `DATABASE_URL` e le variabili `EDUNEWS24_*`, i valori
sono predefiniti: se la shell ha già la variabile, vince la shell. Per questo i
comandi più sotto le impostano in modo esplicito.

Anche durante i test `backend/.env` viene comunque letto
(`backend/src/config.py`). Le variabili che il conftest non imposta, per
esempio quelle delle password, delle sessioni, dei limiti del login e del
livello di log, prendono il valore di quel file. Per una suite riproducibile
conviene lasciarle ai valori del file d'esempio.

### Vincolo sull'URL del database

La suite cancella e ricrea tabelle. Per questo `TEST_DATABASE_URL` deve avere:

- schema `mysql+pymysql`;
- host di loopback;
- porta 3307;
- database `ersaf_test`;
- nessun parametro di query.

Altrimenti la raccolta si ferma con `RuntimeError`.

### MariaDB assente e `--require-mariadb`

Durante la raccolta il conftest prova una connessione, con un timeout di 3
secondi.

- **Senza MariaDB e senza opzione.** I test `mariadb` vengono saltati. A fine
  esecuzione compare un avviso rosso con il numero di test saltati: la suite
  può risultare verde senza aver verificato nulla sul database.
- **Con `--require-mariadb`.** Se MariaDB non risponde, la sessione si
  interrompe subito con codice di uscita 3.

### Fixture principali

| Fixture | Cosa fa |
|---|---|
| `schema` | Una volta per sessione applica `db/test/schema_base.sql` e poi tutte le migrazioni in ordine. Non è automatica: i test unitari non la usano |
| `db_pulito` | Prima di ogni test svuota le tabelle di stato con `TRUNCATE`. Ruoli e template restano. Non usa una transazione annullata, perché il test di consumo concorrente ha bisogno di vedere i commit fra due connessioni |
| `db` | Sessione di osservazione con isolamento `READ COMMITTED`, per vedere ciò che l'API ha scritto |
| `client`, `client_da` | Client HTTP di prova con un IP valido (`client_da` lo sceglie), base https su un dominio di esempio, `X-ERSAF-Request: 1`. Un errore 500 resta una risposta, non un'eccezione |
| `mailer`, `sms` | Automatiche: spie in memoria, svuotate a ogni test. Nessun test può spedire davvero |
| `stato_edunews24` | Automatica: prima e dopo ogni test azzera il servizio EduNews24 (cache, pause, budget, cursori) |
| `spia_sql` | Raccoglie gli statement SQL eseguiti mentre è attiva. Si registra dopo il listener della visibilità, quindi li vede già con il prefisso `SET STATEMENT`: è così che si verifica dove il prefisso compare |
| `tabella_pratiche` | Crea `pratiche` dai modelli e la svuota prima e dopo, e prepara le tabelle contabili sintetiche di `tests/support/contabilita.py`. Non sta fra le tabelle troncate, e il `TRUNCATE` di `aziende` riusa gli id: una pratica rimasta finirebbe "nell'azienda 1" del test successivo |

Altri comportamenti da conoscere:

- Lo schema base non contiene le tabelle delle pratiche e dei prodotti
  formativi. I test che ne hanno bisogno le creano dai modelli con
  `Base.metadata.create_all`.
- `tests/db/test_migrazioni.py` cancella e ricrea il database `ersaf_test`;
  alla fine riapplica schema base e migrazioni.

## Database di test

`db/test/docker-compose.test.yml` avvia un MariaDB usa e getta:

- immagine MariaDB 10.11, container `ersaf-db-test`;
- porta 3307 sull'host, per non scontrarsi con un MariaDB locale;
- dati in `tmpfs`: spariscono quando il container si ferma;
- `event_scheduler` attivo, `sql_mode` severo, attesa sui lock ridotta;
- healthcheck.

`db/test/init/01_database.sql` crea anche il database `ersaf_dev` per lo
sviluppo e dà all'utente di test i permessi sui database che iniziano con
`ersaf_`.

Dalla radice del repository:

```bash
docker compose -f db/test/docker-compose.test.yml up -d     # avvio
docker compose -f db/test/docker-compose.test.yml ps        # stato (healthy)
docker compose -f db/test/docker-compose.test.yml down -v   # spegnimento
```

L'URL del database di test è
`mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test`. Le credenziali valgono
solo per questo container usa e getta.

## Comandi del backend

Da `backend/`, con l'ambiente virtuale attivo.

macOS e Linux, test unitari (non serve il container):

```bash
TEST_DATABASE_URL=mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test \
EMAIL_BACKEND=memoria ERSAF_ENV=test \
python -m pytest tests/unit
```

Suite completa (il container deve essere acceso):

```bash
TEST_DATABASE_URL=mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test \
EMAIL_BACKEND=memoria ERSAF_ENV=test \
python -m pytest --require-mariadb
```

Solo i test dei tempi:

```bash
TEST_DATABASE_URL=mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test \
EMAIL_BACKEND=memoria ERSAF_ENV=test \
python -m pytest -m timing --require-mariadb
```

Windows (PowerShell):

```powershell
$env:TEST_DATABASE_URL = 'mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test'
$env:EMAIL_BACKEND = 'memoria'
$env:ERSAF_ENV = 'test'
.\.venv\Scripts\python.exe -m pytest tests/unit
.\.venv\Scripts\python.exe -m pytest --require-mariadb
```

### Test unitari

I test unitari non usano il database e non richiedono Docker. Servono però:

- **PyMySQL installato.** L'engine viene creato all'import con un URL MariaDB,
  e SQLAlchemy carica subito il driver.
- **Un URL che rispetti il vincolo.** Vedi sopra.
- **Il checkout completo del repository.** Alcuni test leggono file fuori da
  `backend/`: una migrazione, il logo del frontend, la regola delle password
  del frontend, le regioni di EduNews24 del frontend.
- **Node, facoltativo.** Un test esegue la regola delle password del frontend
  con `node`; se `node` manca, quel test viene saltato.

I test di `tests/security` che non usano il database non stanno in
`tests/unit`: il gate `Unit` e il comando `pytest tests/unit` non li eseguono.
Si lanciano per percorso, con `python -m pytest tests/security`, anche senza
MariaDB: i test che lo richiedono vengono saltati, gli altri girano.

## Test del frontend

- I test usano il runner di Node (`node --test`), senza browser.
- Importano solo moduli di `src/lib/` e `src/config/`, mai componenti `.jsx`.
- Alcuni importano pacchetti npm (`react-router`, e `lucide-react` tramite
  `config/icone.js`): prima serve `npm ci`.

Da `frontend/`:

```bash
npm ci          # una volta, o dopo un cambio di package-lock.json
npm test        # test
npm run lint    # ESLint
npm run build   # build di produzione
```

Le date di EduNews24 si calcolano nel fuso Europe/Rome;
`tests/edunews24.test.js` ripete i casi dei cambi d'ora con altri fusi e si
lancia anche con `TZ=UTC node --test tests/edunews24.test.js`.
`tests/edunews24Sorgenti.test.js` legge come testo, senza importarli,
componenti, hook, CSS e SVG di EduNews24, più Dashboard, testi e librerie
collegati, per le regole che il lint non vede (niente iframe, `crossorigin`,
`autoplay` o HTML esterno, un solo link esterno, classi mai composte a
runtime, niente glifi, stili in linea o colori grezzi, indirizzi dei social
solo in `src/config/edunews24.js`) e per alcune scelte di struttura e
d'impaginazione che `node --test` non può misurare nel browser, come la
colonna di due voci di solo testo in coppia e specchio o l'elenco compatto
del riquadro subito sotto la voce principale.

## Test degli strumenti della documentazione

Stanno in `scripts/documentazione/tests/`, con un proprio
`scripts/documentazione/pytest.ini`. Sono
separati dai test del backend perché il conftest del backend impone MariaDB e
le sue variabili. Si lanciano con lo stesso ambiente virtuale. Comandi e regole:
[documentazione.md](documentazione.md).

Fra questi c'è il test di `compose_rel`, del firewall EduNews24, del bridge
dichiarato dalla sua rete e di `prepara_edunews24` con gli SMS reali o con un
bridge diverso da quello delle regole, con la chiave `USCITA_EDUNEWS24`
assente, vuota, a `si` o con un altro valore (`test_deploy_edunews24.py`), con `docker` e `iptables` finti: richiede `bash`,
anche la 3.2 di macOS, e senza viene saltato.

## scripts/verify-local.ps1

Lo script lancia i controlli in sequenza. Funziona solo su Windows: usa
`backend\.venv\Scripts\python.exe` e `npm.cmd`.

- Imposta per il solo processo `TEST_DATABASE_URL`, `EMAIL_BACKEND=memoria` ed
  `ERSAF_ENV=test`, e alla fine ripristina i valori di prima.
- Il gate si sceglie con `-Gate`:

| Gate | Cosa esegue |
|---|---|
| `Unit` (predefinito) | `pytest tests/unit` |
| `Backend` | `pytest --require-mariadb`, cioè tutta la suite del backend |
| `Frontend` | `npm test`, `npm run build`, `npm run lint` |
| `All` | `Backend` e `Frontend` |
| `Docs` | Test degli strumenti, verifica dei riferimenti generati e controlli della documentazione. Non fa parte di `All`. Dettagli in [documentazione.md](documentazione.md) |

- `Backend` e `All` richiedono il container di test acceso.
- Ogni passo scrive il log in `logs/verification/<nome>.log` e mostra le ultime
  righe.
- Alla fine lo script stampa una tabella dei risultati. Esce con 1 se un passo
  è fallito.

Esempio, dalla radice:

```powershell
.\scripts\verify-local.ps1 -Gate All
```

Su macOS e Linux si usano i comandi delle sezioni precedenti.

## Integrazione continua

Nessuna CI esegue i test dell'applicazione, né del backend né del frontend.
L'unico workflow riguarda la documentazione ([documentazione.md](documentazione.md)).
I test dell'applicazione si lanciano quindi in locale. Il flusso di lavoro è in
[convenzioni.md](convenzioni.md).


## Chat e firma

Le suite coprono acquisizione e concorrenza della firma, riuso nei PDF e chat
nativa sul database usa-e-getta. Sono provati invio, storico, idempotenza
concorrente, limiti, rollback atomico anche delle notifiche, revoca e isolamento
di cookie/token, grant, cursori e due trasporti WebSocket sul medesimo archivio.
Il vettore crittografico sintetico è quello già verificato contro Java.
Le suite `test_realtime_completo.py`, `test_realtime_isolamento.py` e
`test_realtime_contratti.py` aggiungono chat personali/ticket, login e replay
del refresh, snapshot immutabili, presenza, bridge legacy, idempotenza del
produttore e recupero delle consegne via socket. Il conftest fissa lo schema
ticket a `ersaf_test`; le fixture preparano archivi e segreti sintetici.
Il gate non esegue test Flutter o la suite Java.
Vedi [verifiche](realtime.md#verifiche-riproducibili).
Le fixture HTTP preparano sempre schema e chiavi sintetiche realtime, senza
flag di abilitazione. Nei test di dominio bridge e manutenzione sono pilotati
esplicitamente; la prova del ciclo di vita usa invece i lavori reali e verifica
readiness, autenticazione, connessione WebSocket e invio cifrato. L'avvio con
keyring o chiave JWT mancanti deve fallire.
Il test di rollback conserva i metadati condivisi delle 017/018/019: possono essere
preesistenti e non devono subire DROP.

Le suite `test_realtime_hardening.py` (unitaria e d'integrazione),
`test_realtime_risorse.py` e `test_realtime_conservazione.py` provano limiti,
ordine, cancellazioni, multi-connessione, scadenze, input avversi e retention.
`test_realtime_parita_java.py` confronta 59 vettori sintetici prodotti con
16 classi Java originali: HKDF, u2/u3, hash, JSON, cursore e date legacy.
Il normale gate Python non richiede un JDK: usa la fixture congelata, con hash
di provenienza. `test_realtime_trasporto.py` apre un server Uvicorn su una
porta loopback temporanea e verifica dimensione dei frame, scadenza silenziosa
del token e ping/pong, con dati sintetici e dipendenze DB isolate. Le eccezioni
ai warning sono limitate al trasporto `websockets.legacy` fissato e verificato.
Sono prove di comportamento e sicurezza, non benchmark. La matrice e gli
adattamenti sono in [realtime-parita.md](realtime-parita.md).

## Stato dei contatti e database facoltativi

`test_stato_clienti.py` confronta elenchi e scheda per account attivi legacy,
account disattivi, verifica OTP corrente e versioni storiche diverse dal contatto attuale.
Le prove del numero di query per pagina restano applicate anche agli indicatori.

`test_database_secondari.py` verifica che le connessioni amministrative siano
inizializzate solo quando richieste, chiudano le sessioni anche su errore e non
ereditino gli indirizzi ordinari durante i test. Gli override
`TEST_DATABASE_URL_GESTIONE_PAGAMENTI` e `TEST_DATABASE_URL_SYS_ADMIN` accettano
soltanto lo stesso MariaDB locale usa-e-getta della suite: nessun database
aggiuntivo o remoto è necessario. Un indirizzo malformato non viene riportato
nel messaggio d'errore.

`test_database_trasporto.py` verifica la policy comune: TLS senza trust store
implicito, verifica dell'host, rifiuto del downgrade prima dell'invio delle
credenziali, URL senza override di trasporto e pool limitato. Le prove non
richiedono connessioni a server esterni né certificati reali.

## Storico e notifiche delle pratiche

`test_storico_stati_pratica.py` verifica la creazione in Bozza, il cambio di
stato riservato al Nazionale e la singola notifica al primo ingresso in Bozza
o Caricata. Sessioni MariaDB indipendenti riproducono uno snapshot precedente
al salvataggio concorrente, anche con ritorno allo stato iniziale, e uno
spostamento di azienda che revoca la visibilita della pratica.

La stessa suite copre il rinnovo con aggiornamenti parziali: un secondo anno
non può sommarsi a quello già salvato, mentre una sostituzione esplicita è
valida. `test_pratiche_rinnovi.py` verifica la normalizzazione dei flag legacy,
l'esclusione fra anni e la lettura delle righe storiche incoerenti. I test
frontend di `praticaForm.test.js` verificano la scelta esclusiva e l'omissione
dei campi di rinnovo quando il percorso non è di tipo Lauree.

`tests/support/pratiche.py` prepara solo lookup e template email sintetici;
la pulizia elimina lo storico prima delle pratiche, rispettando le chiavi
esterne. Le email sono catturate dal backend in memoria: nessun invio reale.

Il conftest fissa `SCHEMA_GESTIONE_PAGAMENTI` a `ersaf_test`, quindi le
tabelle contabili che la creazione di una pratica SSML o A4U scrive stanno nel
database di test: `tests/support/contabilita.py` le crea (`articolo`,
`articolo_pratica`, `documento`, `documento_articolo`, i loro tipi e gruppi e
`pratica_codice`) con colonne e tipi del database reale, senza le chiavi
esterne verso le tabelle legacy. `test_dopo_salvataggio_pratica.py` verifica
righe e collegamenti, la numerazione che riparte dal massimo esistente, i
contatori concorrenti e l'annullamento di tutto se manca un dato.

I test del deploy EduNews24 separano overlay e notifiche
(`scripts/documentazione/tests/test_deploy_edunews24.py`) da DNS e firewall
(`test_deploy_edunews24_firewall.py`). Le fixture condivise eseguono solo
comandi Docker e iptables finti; su Windows scelgono Git Bash e normalizzano
i percorsi, senza avviare WSL o modificare il firewall della macchina.
