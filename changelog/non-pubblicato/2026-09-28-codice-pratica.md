---
---

## Novità e correzioni

- aggiunto: Il codice di una pratica nuova (es. MT000042) si genera da solo al salvataggio, per le università che lo prevedono: non resta più vuoto.

## Dettagli tecnici

- aggiunto: `POST /pratiche/` genera `pratica_numero` (e, per SSML, `pratica_codiceASG`) dentro la stessa transazione dell'inserimento, con un contatore atomico per prefisso: due salvataggi concorrenti non generano più lo stesso codice. Se il tipo di corso del percorso non ha un prefisso associato, la richiesta risponde 400.
- aggiunto: Migrazione `017_contatori_codice_pratica.sql`, con rollback. Crea `pratiche_contatori`, il contatore atomico per prefisso. Non aggiunge una UNIQUE su `pratiche.pratica_numero`: verificato sul database reale, quella colonna ha già molti duplicati legacy, quindi la UNIQUE resta un passo manuale da fare dopo una bonifica (vedi "Prima di andare in produzione" in `db/README.md`, stesso trattamento già riservato a `utenti.utente_username` dalla `005`).
