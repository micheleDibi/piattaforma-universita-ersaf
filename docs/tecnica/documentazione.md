# Come si mantiene la documentazione

Questa pagina spiega come è organizzata la documentazione, chi aggiorna cosa e quali controlli la tengono allineata al codice. Riguarda chi sviluppa, chi rivede le pull request e chi pubblica.

## Struttura

| Dove | Per chi | Cosa contiene |
|---|---|---|
| [README.md](../../README.md) | tutti | cos'è il progetto e da dove partire |
| [docs/README.md](../README.md) | tutti | l'indice ragionato |
| `docs/funzionale/` | chi usa la piattaforma | pagine, ruoli, accesso e flussi, senza termini tecnici |
| `docs/tecnica/` | chi sviluppa o pubblica | architettura, sviluppo, test, database, deploy, convenzioni, sicurezza |
| `docs/tecnica/riferimenti/` | chi sviluppa | pagine **generate**: API, pagine del frontend, migrazioni, configurazione |
| `docs/prompt/` | storico | prompt dati in passato agli agenti; sono istantanee datate |
| [CHANGELOG.md](../../CHANGELOG.md) | tutti | le versioni pubblicate |
| `changelog/non-pubblicato/` | chi sviluppa | i frammenti delle modifiche non ancora pubblicate |
| [CLAUDE.md](../../CLAUDE.md) | agenti AI | le regole da seguire nel repository |
| [db/README.md](../../db/README.md) | chi sviluppa | regole operative delle migrazioni |

Un'informazione ha una sola casa; gli altri documenti ci rimandano. Le case principali:

| Argomento | Casa |
|---|---|
| Flusso di lavoro (rami, pull request, pubblicazione) | [convenzioni](convenzioni.md) |
| Elenco delle API | [riferimenti/api.md](riferimenti/api.md) |
| Elenco delle pagine | [riferimenti/rotte-frontend.md](riferimenti/rotte-frontend.md) |
| Elenco e anomalie delle migrazioni | [riferimenti/migrazioni.md](riferimenti/migrazioni.md) |
| Variabili di configurazione | [riferimenti/configurazione.md](riferimenti/configurazione.md) |
| Limiti noti e contrasti fra interfaccia e server | [sicurezza](sicurezza.md#limiti-noti) |
| Timbro del changelog al deploy | [deploy](deploy.md) |
| Formato dei frammenti | [changelog/MODELLO.md](../../changelog/MODELLO.md) |

La documentazione descrive il codice di main. Se codice e documentazione non coincidono, si corregge la documentazione nella stessa modifica oppure si segnala il problema: non si lascia com'è.

## Il ciclo di una modifica

1. Chi sviluppa cambia il codice e, nella stessa pull request:
   - aggiunge un frammento in `changelog/non-pubblicato/`, secondo il [modello](../../changelog/MODELLO.md);
   - aggiorna i documenti che la [mappa](#la-mappa-codice--documenti) collega ai file toccati;
   - rilancia `genera.py` se ha cambiato API, pagine, migrazioni o configurazione.
2. La CI controlla tutto questo sulla pull request.
3. Dopo l'unione, alla pubblicazione, il deploy scrive la versione in `CHANGELOG.md` con i frammenti del commit pubblicato e li cancella ([timbro](deploy.md)).

Le modifiche che arrivano su main senza pull request non passano dalla CI: il frammento va scritto lo stesso. Il timbro stampa un avviso per i commit che hanno toccato il codice senza aggiungerne uno.

## Pagine generate

`docs/tecnica/riferimenti/` contiene solo pagine prodotte da `scripts/documentazione/genera.py`. Non si modificano a mano: si cambia il codice (o il commento nell'esempio di configurazione) e si rigenera.

| Pagina | Fonte |
|---|---|
| `api.md` | OpenAPI dell'applicazione. L'app si importa in un sottoprocesso senza leggere `backend/.env` e senza database; l'accesso richiesto da ogni operazione si ricava dalle sue dipendenze. |
| `rotte-frontend.md` | `frontend/src/config/routes/` importati con Node e `frontend/src/App.jsx` letto come albero sintattico con `@babel/core`. |
| `migrazioni.md` | Intestazioni di `db/migrations/` e file di `db/rollback/`; le anomalie sono calcolate. |
| `configurazione.md` | Campi di `backend/src/config.py` e `backend/src/notifiche/config_sms.py`, commenti dei file `.env.example`, variabili lette dagli script di deploy e dal frontend. L'obbligatorietà si ricava dalla verifica di avvio con valori finti. |

Nessuna pagina contiene valori reali: i segreti compaiono come "—", e da commenti, intestazioni e valori predefiniti vengono tolti indirizzi email, IP, domini, credenziali e percorsi del server, sostituiti da segnaposto fra parentesi quadre. Un commento di `.env.example` descrive la variabile che lo segue; le variabili successive del gruppo lo ereditano solo se il commento le nomina.

Comandi, dalla radice del repository:

```bash
python scripts/documentazione/genera.py             # scrive le pagine
python scripts/documentazione/genera.py --verifica  # controlla senza scrivere
```

Esiti: 0 in ordine; 1 una pagina non corrisponde al codice (va rigenerata e committata); 2 un generatore non riesce, per esempio per una forma dell'OpenAPI o di `App.jsx` che non riconosce, oppure per versioni delle librerie diverse da quelle previste.

Prerequisiti:

```bash
pip install -r backend/requirements.txt -r scripts/documentazione/requisiti.txt \
    -c scripts/documentazione/vincoli.txt
npm ci --prefix frontend
```

`scripts/documentazione/vincoli.txt` fissa le versioni di FastAPI, Pydantic e SQLAlchemy con cui si generano le pagine, così il risultato è identico in locale e in CI. Quando si aggiorna una di quelle librerie si aggiornano i vincoli e si rigenera nella stessa pull request.

Due pull request unite una dopo l'altra possono lasciare su main pagine non aggiornate, perché la seconda è stata controllata prima che la prima fosse unita. La pull request successiva lo segnala: basta rigenerare.

## Controlli sulle pull request

Il workflow [documentazione.yml](../../.github/workflows/documentazione.yml) gira sulle pull request verso main, senza segreti e senza database. Esegue:

1. i test degli strumenti (`scripts/documentazione/tests/`);
2. `genera.py --verifica`;
3. il controllo della sintassi di `scripts/deploy.ps1` e `scripts/verify-local.ps1`;
4. `controlla.py tutto`, cioè:
   - **frammenti**: ogni file in `changelog/non-pubblicato/` rispetta il formato;
   - **link**: i link relativi fra file Markdown puntano a file esistenti (maiuscole comprese) e a titoli esistenti, con le ancore calcolate come le calcola GitHub;
   - **mappa**: la mappa è valida, i documenti esistono e ogni pattern trova almeno un file;
   - **contenuti**: in nessun file Markdown compaiono indirizzi email, indirizzi IP diversi dal loopback, nomi di rete interna, domini dell'ente, credenziali o percorsi del server, perché il repository è pubblico; l'unica eccezione dichiarata è l'URL del database di test usa-e-getta;
   - **frammento obbligatorio**: se la pull request tocca `backend/src/`, `frontend/src/`, `db/` o `deploy/` (esclusi i `.md`), deve aggiungere o modificare un frammento valido;
   - **documenti collegati**: se tocca un file coperto da una regola della mappa, deve modificare almeno uno dei documenti di quella regola; il messaggio dice quali;
   - **registro protetto**: la pull request non può modificare `CHANGELOG.md` né cancellare o rinominare frammenti; lo fa solo il timbro.

Un secondo job ripete i test del timbro con Python 3.10 e senza dipendenze, perché il timbro gira sul PC di chi pubblica.

I file cambiati si calcolano rispetto al main su cui la pull request viene unita (opzione `--merge`), così i commit arrivati su main dopo l'apertura, compresi quelli del timbro, non contano.

Nessun workflow gira sui push a main: i commit "Changelog: Versione N" del timbro arrivano direttamente e non devono essere bloccati. Se si rende obbligatorio questo controllo nelle impostazioni del repository, va applicato solo alle pull request.

### Etichette di esenzione

| Etichetta | Quando |
|---|---|
| `senza-changelog` | la modifica al codice non va raccontata (per esempio un commento o un test) |
| `documentazione-invariata` | i documenti collegati sono stati controllati e non c'è nulla da cambiare |

Aggiungere o togliere un'etichetta rilancia il controllo con le etichette aggiornate. Il pulsante "Re-run" di GitHub, invece, riusa le etichette del momento in cui il controllo era partito.

Chi apre la pull request può mettere le etichette da sé: chi la rivede controlla che l'esenzione sia giustificata. Se le etichette non esistono ancora nel repository, si creano una volta con:

```bash
gh label create senza-changelog --color BFD4F2 --description "La PR non richiede un frammento in changelog/non-pubblicato"
gh label create documentazione-invariata --color C5DEF5 --description "Nessun documento collegato da aggiornare"
```

## La mappa codice → documenti

[docs/mappa-documentazione.yml](../mappa-documentazione.yml) elenca regole fatte di `percorsi` (pattern di file) e `documenti`. Nei pattern `*` resta dentro una cartella e `**` le attraversa; non si usano graffe, un pattern per riga, fra virgolette.

Limiti da conoscere:

- il controllo verifica che un documento sia stato toccato, non che sia stato aggiornato bene: il merito resta alla revisione;
- una modifica solo estetica a un file coperto richiede comunque l'etichetta `documentazione-invariata`;
- alcuni file cambiano spesso senza effetti da documentare (registrazione dei router, icone, stati della query, stili, migrazioni) e sono stati lasciati fuori dalla mappa: le migrazioni sono coperte dal frammento e da `riferimenti/migrazioni.md`;
- quando si aggiunge un modulo o si rinomina un file, la mappa va aggiornata: il controllo segnala i pattern che non trovano più nulla, non i file nuovi rimasti scoperti.

## In locale

Su Windows il gate `Docs` esegue i controlli della CI sulla documentazione (test degli strumenti, pagine generate, frammenti, link, mappa, contenuti e requisiti della pull request). Restano solo in CI il controllo di sintassi degli script PowerShell e la ripetizione dei test del timbro con Python 3.10:

```powershell
powershell -NoProfile -File scripts\verify-local.ps1 -Gate Docs
powershell -NoProfile -File scripts\verify-local.ps1 -Gate Docs -Etichette documentazione-invariata
```

Su macOS e Linux, dalla radice e con l'ambiente virtuale attivo:

```bash
python -X warn_default_encoding -m pytest scripts/documentazione/tests
python scripts/documentazione/genera.py --verifica
python scripts/documentazione/controlla.py tutto --base origin/main
```

Senza `--base` i controlli della pull request non vengono eseguiti: l'ultima riga elenca sempre quali controlli sono girati.

In locale il controllo della pull request confronta i commit del ramo con `origin/main` (va aggiornato con `git fetch`): le modifiche non ancora committate non contano. Le etichette si passano con `--etichette`.

## Il timbro del changelog

Dopo una pubblicazione riuscita di origin/main, `scripts/deploy.ps1` chiama `scripts/documentazione/timbra_changelog.py`, che scrive la versione in `CHANGELOG.md` e cancella i frammenti pubblicati. Funzionamento, codici di uscita e recupero a mano sono descritti in [deploy](deploy.md).

## Strumenti

| File | Compito |
|---|---|
| `scripts/documentazione/genera.py` | pagine generate |
| `scripts/documentazione/controlla.py` | controlli su frammenti, link, mappa e pull request |
| `scripts/documentazione/timbra_changelog.py` | timbro al deploy |
| `scripts/documentazione/frammenti.py`, `comune.py` | lettura dei frammenti, git, pattern, ancore, redazione; solo libreria standard |
| `scripts/documentazione/mappa.py` | lettura della mappa (PyYAML) |
| `scripts/documentazione/generatori/` | un modulo per pagina generata |
| `scripts/documentazione/tests/` | test, lanciati con il loro `pytest.ini` |

Il timbro, i frammenti e le funzioni comuni usano solo la libreria standard e restano compatibili con Python 3.10.
