# Sviluppo locale

Questo documento spiega come preparare un PC per lavorare su backend e
frontend. È anche il documento a cui rimanda `scripts/verify-local.ps1` quando
manca l'ambiente virtuale.

I comandi partono dalla radice del repository, salvo indicazione diversa. Per
ogni passo ci sono le varianti per macOS e Linux e per Windows (PowerShell).

Documenti collegati:

- test e loro comandi: [test.md](test.md);
- flusso di lavoro con git e pull request: [convenzioni.md](convenzioni.md);
- variabili di configurazione: [riferimenti/configurazione.md](riferimenti/configurazione.md).

## Prerequisiti

- **Git.**
- **Python.** Il container dell'API usa Python 3.14 (`backend/Dockerfile`). Il
  repository non dichiara una versione minima: usare la stessa versione o una
  compatibile con `backend/requirements.txt`.
- **Node.js.** Il build del frontend usa Node 24 (`frontend/Dockerfile`).
  `frontend/package.json` non dichiara una versione.
- **Docker con Compose,** per il MariaDB locale.
- **PowerShell,** solo su Windows, per `scripts/verify-local.ps1`.

## Ambiente virtuale e dipendenze

L'ambiente virtuale va in `backend/.venv`: lo cerca `scripts/verify-local.ps1`
ed è già escluso da git.

macOS e Linux:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
```

Windows:

```powershell
py -3 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

`backend/requirements.txt` contiene anche:

- i pacchetti dei test (`pytest`, `httpx2`);
- quelli dei PDF (`typst`, `Pillow`), distribuiti come wheel senza librerie di
  sistema;
- `tzdata`, solo su Windows.

**Strumenti della documentazione.** Chi lavora sulla documentazione installa
nello stesso ambiente anche i requisiti degli strumenti, con i vincoli di
versione:

```bash
backend/.venv/bin/python -m pip install -r backend/requirements.txt \
  -r scripts/documentazione/requisiti.txt -c scripts/documentazione/vincoli.txt
```

```powershell
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt `
  -r scripts\documentazione\requisiti.txt -c scripts\documentazione\vincoli.txt
```

I vincoli fissano le versioni che influenzano i riferimenti generati. Vedi
[documentazione.md](documentazione.md).

**Frontend:**

```bash
cd frontend
npm ci
```

## Configurazione

### Backend

1. Copiare `backend/.env.example` in `backend/.env`. Il file `.env` è escluso
   da git e non va mai committato.
2. Completare i valori obbligatori (sotto).
3. Lasciare il resto: i valori del file d'esempio vanno bene per lo sviluppo.

Il backend legge sempre `backend/.env`, da qualunque cartella venga avviato.

**Valori obbligatori.**

- `DATABASE_URL`. Per il MariaDB locale si usa l'URL del database di test
  indicato in [test.md](test.md), con `ersaf_dev` al posto di `ersaf_test`.
- `PASSWORD_RESET_TOKEN_PEPPER`, `SESSION_TOKEN_PEPPER` e `TOTP_CHIAVE`:
  - almeno 32 byte ciascuno;
  - tutti diversi fra loro;
  - senza il prefisso segnaposto del file d'esempio.

  Ogni valore si genera con il comando indicato in testa a
  `backend/.env.example`. Non si riusano valori di altri ambienti.

Se la configurazione non è valida, l'avvio si ferma ed elenca tutti i problemi.

**Valori di sviluppo.** Sono quelli del file copiato da
`backend/.env.example`; per queste voci coincidono con i predefiniti del
codice, tranne dove indicato.

- Ambiente `sviluppo`.
- Frontend, CORS e origini WebAuthn sul server di sviluppo di Vite in
  `localhost`, con WebAuthn legato a `localhost`.
- Email scritte come file `.eml` in `backend/var/email_dev`. Lì si leggono i
  codici OTP e i link di recupero password.
- Log a console e in `backend/logs/app.log`.
- SMS scritti come file JSON in `backend/var/sms_dev`. Qui il file d'esempio e
  il codice non coincidono: senza `SMS_BACKEND` gli SMS sono disabilitati e
  l'invio di un codice fallisce.

Le cartelle `backend/var/` e `logs/` sono escluse da git.

**Attenzione.** Se `TEST_DATABASE_URL` è impostata, nella shell oppure in
`backend/.env`, backend e script usano quella al posto di `DATABASE_URL`.

### Frontend

Il frontend legge `VITE_API_BASE_URL` (`frontend/src/lib/api.js`). Se manca, il
codice usa il backend locale sulla porta 8000. Per cambiarla si copia
`frontend/.env.example` in `frontend/.env`.

Tutte le variabili `VITE_` finiscono nel codice scaricato dal browser: mai
segreti.

## Database locale

### Avvio

Il container dei test ospita anche il database di sviluppo:

```bash
docker compose -f db/test/docker-compose.test.yml up -d
```

- Il database `ersaf_dev` nasce vuoto insieme a `ersaf_test`
  (`db/test/init/01_database.sql`).
- I dati stanno in memoria (`tmpfs`). Fermare il container cancella tutto,
  anche `ersaf_dev`.

### Schema

Il repository non contiene lo schema completo del gestionale. Si può
ricostruire la parte minima come fa la suite di test: prima
`db/test/schema_base.sql`, poi tutte le migrazioni in ordine.

`schema_base.sql` cancella le tabelle che ricrea: si usa solo su `ersaf_dev` o
`ersaf_test` di questo container, mai su un database con dati.

Nei comandi seguenti `UTENTE` e `PASSWORD` vanno sostituiti con quelli
dell'URL di test. Il ciclo si ferma al primo errore.

macOS e Linux:

```bash
for f in db/test/schema_base.sql db/migrations/*.sql; do
  echo "== $f"
  docker exec -i ersaf-db-test mariadb -u UTENTE -pPASSWORD ersaf_dev < "$f" || break
done
```

Windows (il reindirizzamento passa da `cmd`, che invia i file senza
convertirne la codifica):

```powershell
$file = [string[]](Resolve-Path db\test\schema_base.sql).Path
$file += Get-ChildItem db\migrations\*.sql | Sort-Object Name | ForEach-Object FullName
foreach ($f in $file) {
  Write-Host "== $f"
  cmd /c "docker exec -i ersaf-db-test mariadb -u UTENTE -pPASSWORD ersaf_dev < `"$f`""
  if ($LASTEXITCODE -ne 0) { break }
}
```

Con questo schema mancano le tabelle delle pratiche, dei prodotti formativi e
delle loro decodifiche. Le pagine che le usano rispondono con un errore.

### Dati di prova

`backend/scripts/seed_sviluppo.py` crea account di prova per i casi del
recupero password e del rehash pigro:

- i nomi utente finiscono con `.prova`;
- a ogni esecuzione cancella e ricrea solo le proprie righe;
- rifiuta di partire se il nome del database non contiene `dev` o `test`;
- alla fine stampa gli account creati e le password di prova.

Da `backend/`:

```bash
.venv/bin/python scripts/seed_sviluppo.py
```

```powershell
.\.venv\Scripts\python.exe scripts\seed_sviluppo.py
```

## Avvio

### Backend

Da `backend/`:

```bash
.venv/bin/python -m uvicorn src.main:app --reload
```

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

- uvicorn ascolta sulla porta 8000, quella che il frontend usa per difetto.
- `GET /salute` risponde se il servizio è attivo.
- La documentazione interattiva di FastAPI è su `/docs`. L'elenco ragionato
  delle rotte è in [riferimenti/api.md](riferimenti/api.md).
- `--reload` serve solo in sviluppo.

### Frontend

Da `frontend/`:

```bash
npm run dev
```

- Vite serve l'interfaccia su `http://localhost:5173`. È l'origine che il
  backend ammette con la configurazione predefinita. Se Vite sceglie un'altra
  porta, il backend rifiuta le scritture e il browser blocca le risposte per
  il CORS: vanno aggiornate `FRONTEND_BASE_URL`, `CORS_ORIGINS` e
  `WEBAUTHN_ORIGINI`.
- Backend e frontend stanno su porte diverse dello stesso host. Il cookie di
  sessione viaggia perché le chiamate usano le credenziali e il backend ammette
  l'origine del frontend.
- `npm run build` produce `frontend/dist`; `npm run preview` la serve in
  locale.

### Proxy verso un'API remota (facoltativo)

`frontend/vite.config.js` legge `ERSAF_API_PROXY` dai file `.env` di
`frontend/`.

- Con la variabile impostata, le chiamate a `/api` passano dal server di
  sviluppo verso quell'indirizzo. Il browser parla solo con `localhost`, quindi
  non scatta il controllo del CORS nel browser.
- **Il proxy non riscrive l'intestazione `Origin`:** cambia solo `Host`. Le
  richieste arrivano all'API remota con l'origine del server di sviluppo. Per
  le scritture, login compreso, funziona solo se l'API remota ammette quella
  origine fra `FRONTEND_BASE_URL` e `CORS_ORIGINS`; altrimenti la risposta è
  403 (`backend/src/security/browser.py`).
- Il percorso conserva il prefisso `/api`. Il bersaglio deve quindi gestirlo,
  come fa l'nginx del frontend (per esempio `https://<dominio-collaudo>`).
- Per usarlo serve anche `VITE_API_BASE_URL=/api`.
- Un file dedicato, per esempio `frontend/.env.collaudo`, è escluso da git. Si
  attiva con `npm run dev -- --mode collaudo`.

Il comportamento del cookie di sessione su `http://localhost` verso un'API in
HTTPS non è stato provato: il nome del cookie e il suo attributo `Secure`
dipendono dalla configurazione del server remoto (`security/browser.py`).

## Verifiche prima di proporre una modifica

**macOS e Linux.** Si usano i comandi di [test.md](test.md).

**Windows.** `scripts/verify-local.ps1` esegue i controlli in sequenza. Gate,
log e comandi sono descritti in [test.md](test.md).

Se i criteri di esecuzione di PowerShell bloccano lo script:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify-local.ps1 -Gate All
```

Il flusso di lavoro con git e le pull request è in
[convenzioni.md](convenzioni.md).
