# Piattaforma Università

Applicazione web della rete ERSAF per gestire sottoscrittori, attuatori, aziende, pratiche universitarie e prodotti formativi. Lavora sul database della piattaforma precedente, a cui aggiunge alcune tabelle proprie.

## Per chi

- **Chi usa la piattaforma** (committente, operatori, collaudatori): la [guida funzionale](docs/funzionale/panoramica.md) spiega pagine, ruoli e flussi.
- **Chi sviluppa o pubblica**: la [documentazione tecnica](docs/README.md#documentazione-tecnica) parte dall'[architettura](docs/tecnica/architettura.md).
- **Agenti AI**: le regole sono in [CLAUDE.md](CLAUDE.md).

L'indice completo è in [docs/README.md](docs/README.md). Le versioni pubblicate sono nel [registro delle modifiche](CHANGELOG.md).

## Avvio rapido

Servono Python, Node.js, Docker e Git. In breve:

1. avviare il database di test con `docker compose -f db/test/docker-compose.test.yml up -d`;
2. creare l'ambiente virtuale in `backend/`, installare `backend/requirements.txt` e preparare `backend/.env` partendo da `backend/.env.example`;
3. installare il frontend con `npm ci` in `frontend/` e avviarlo con `npm run dev`.

I passi completi, con i comandi per Windows, macOS e Linux, sono in [sviluppo locale](docs/tecnica/sviluppo-locale.md); i test in [test](docs/tecnica/test.md).

## Struttura del repository

| Cartella | Contenuto |
|---|---|
| `backend/` | API FastAPI, modelli, test |
| `frontend/` | applicazione React |
| `db/` | migrazioni, rollback, diagnostica e database di test |
| `deploy/` | configurazione Docker e script eseguiti sul server di collaudo |
| `scripts/` | pubblicazione, verifiche locali e strumenti della documentazione |
| `docs/` | documentazione |
| `changelog/` | frammenti delle modifiche non ancora pubblicate |

## Come contribuire

Si lavora su un ramo personale e si apre una pull request verso `main`; una sola persona unisce e pubblica. Ogni modifica al codice porta un frammento di changelog e l'aggiornamento dei documenti collegati, controllati in automatico sulla pull request. Il flusso è descritto in [convenzioni](docs/tecnica/convenzioni.md), le regole della documentazione in [documentazione](docs/tecnica/documentazione.md).
