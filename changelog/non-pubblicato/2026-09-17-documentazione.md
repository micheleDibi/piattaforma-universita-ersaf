---
---

## Novità e correzioni

- aggiunto: È disponibile una guida alla piattaforma per chi la usa: pagine, ruoli e permessi, accesso,
  sottoscrittori e attuatori, aziende, pratiche e prodotti formativi.
- aggiunto: A ogni pubblicazione il registro delle modifiche riporta le novità della versione, con lo stesso
  numero e la stessa data mostrati in fondo al menu.

## Dettagli tecnici

- aggiunto: Documentazione in `docs/` (funzionale e tecnica), `README.md`, `CLAUDE.md` per gli agenti e
  riferimenti generati da `scripts/documentazione/genera.py` (API, pagine, migrazioni, configurazione).
- aggiunto: Controllo `.github/workflows/documentazione.yml` sulle pull request verso main: frammento di
  changelog, documenti collegati secondo `docs/mappa-documentazione.yml`, link interni e pagine generate.
  Esenzioni con le etichette `senza-changelog` e `documentazione-invariata`.
- aggiunto: Timbro del changelog dopo il deploy di origin/main (`scripts/documentazione/timbra_changelog.py`),
  con il comando remoto in sola lettura `release-info`; gate `Docs` in `scripts/verify-local.ps1`.
- modificato: `.gitattributes` impone LF ai file Markdown e agli strumenti della documentazione; commenti di
  `backend/.env.example` e `db/README.md` allineati al codice.
