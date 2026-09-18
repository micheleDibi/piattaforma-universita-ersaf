# Documentazione

Indice di tutta la documentazione della Piattaforma Università. Per una presentazione del progetto vedi il [README](../README.md); per le versioni pubblicate il [registro delle modifiche](../CHANGELOG.md).

## Guida funzionale

Per chi usa la piattaforma: committente, operatori, collaudatori. Nessun termine tecnico.

| Documento | Argomento |
|---|---|
| [Panoramica](funzionale/panoramica.md) | cos'è la piattaforma, le pagine e come ci si muove |
| [Ruoli e permessi](funzionale/ruoli-e-permessi.md) | i ruoli, chi accede e che cosa vede ciascuno |
| [Accesso e sicurezza](funzionale/accesso-e-sicurezza.md) | accesso, secondo fattore, sessione, recupero password, profilo |
| [Sottoscrittori e attuatori](funzionale/sottoscrittori-e-attuatori.md) | elenchi, creazione, scheda, verifica dei contatti |
| [Aziende](funzionale/aziende.md) | elenco, scheda, gerarchia e percentuali |
| [Pratiche](funzionale/pratiche.md) | dashboard, elenco, scheda e documento PDF |
| [Prodotti formativi](funzionale/prodotti-formativi.md) | listini e righe di prezzo |
| [Glossario](funzionale/glossario.md) | i termini usati nella piattaforma |

## Documentazione tecnica

Per chi sviluppa, rivede o pubblica.

| Documento | Argomento |
|---|---|
| [Architettura](tecnica/architettura.md) | stack, moduli, percorso di una richiesta |
| [Sviluppo locale](tecnica/sviluppo-locale.md) | preparare l'ambiente e avviare l'applicazione |
| [Test](tecnica/test.md) | suite del backend e del frontend, comandi |
| [Database e migrazioni](tecnica/database-e-migrazioni.md) | MariaDB, schema legacy, migrazioni |
| [Deploy](tecnica/deploy.md) | pubblicazione sul collaudo, numero di versione, timbro del changelog |
| [Convenzioni](tecnica/convenzioni.md) | flusso di lavoro, commit, regole di codice |
| [Sicurezza](tecnica/sicurezza.md) | sessione, password, secondo fattore, limiti noti |
| [Documentazione](tecnica/documentazione.md) | come si mantiene tutto questo |

Riferimenti generati dal codice, da non modificare a mano:

| Documento | Argomento |
|---|---|
| [API](tecnica/riferimenti/api.md) | operazioni del backend e modelli |
| [Pagine del frontend](tecnica/riferimenti/rotte-frontend.md) | indirizzi, pagine, menu |
| [Migrazioni](tecnica/riferimenti/migrazioni.md) | migrazioni, rollback e anomalie |
| [Configurazione](tecnica/riferimenti/configurazione.md) | variabili d'ambiente |

Altri documenti:

- [db/README.md](../db/README.md): regole operative delle migrazioni;
- [changelog/MODELLO.md](../changelog/MODELLO.md): come si scrive un frammento di changelog;
- [mappa-documentazione.yml](mappa-documentazione.yml): quali documenti rileggere quando cambia il codice;
- [CLAUDE.md](../CLAUDE.md): regole per gli agenti AI.

## Storico

- [Prompt del recupero password](prompt/recupero-password.md): il prompt con cui è stato chiesto a un agente di costruire il recupero password, conservato come istantanea del 4 settembre 2026. Non descrive lo stato attuale.
