---
---

## Novità e correzioni

- aggiunto: Quando una pratica raggiunge per la prima volta lo stato Bozza, il sottoscrittore riceve un'email di conferma. Quando raggiunge per la prima volta lo stato Caricata, la riceve l'ufficio pratiche universitarie di ERSAF. Tornare più tardi sullo stesso stato non manda una seconda email.
- aggiunto: Ogni cambio di stato di una pratica, compreso quello iniziale alla creazione, resta ora in uno storico (non ancora visibile da nessuna pagina).

## Dettagli tecnici

- aggiunto: `POST /pratiche/` e `PUT /pratiche/{id}` scrivono una riga in `pratiche_stati_storico` a ogni cambio di stato (tabella già presente nello schema, prima non scritta da nessun codice), e mandano le email `pratica_bozza`/`nuova_pratica_ersaf` (già presenti in `messaggi_email`) in background, dopo il commit, solo la prima volta che lo stato viene raggiunto.
- aggiunto: `PUT /pratiche/{id}` blocca la riga della pratica (`SELECT ... FOR UPDATE`) prima di leggere lo stato precedente, per evitare che due salvataggi concorrenti della stessa pratica generino due righe di storico o due email.
- modificato: Valutati e lasciati fuori, perché senza corrispondenza reale in questo database (verificato sui dati): la tabella `pratica_codice` (ridondante rispetto a `pratica_numero`, ferma dal 22/08), la creazione di righe "Articolo"/"Documento" per la contabilità (nessuna tabella corrispondente esiste) e le cartelle allegati su FTP (gli allegati sono blob in `pratiche`, non file su cartelle esterne).
