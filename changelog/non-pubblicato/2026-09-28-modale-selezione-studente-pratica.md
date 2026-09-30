---
---

## Novità e correzioni

- aggiunto: In una pratica nuova, lo studente si sceglie ora da una finestra con l'elenco dei sottoscrittori (Codice fiscale, Denominazione, Stato), con ricerca per nome e cognome e le stesse tre verifiche (email, cellulare, diploma) già mostrate nell'elenco Sottoscrittori. Chi non le ha tutte e tre superate compare in elenco ma non è selezionabile.
- modificato: Nell'elenco della finestra compaiono solo i sottoscrittori con un account già attivo, con la stessa visibilità dell'elenco Sottoscrittori.
- corretto: Il campo Studente non promette più una ricerca per codice che non esisteva davvero.

## Dettagli tecnici

- aggiunto: `GET /clienti/` e `GET /clienti/conteggio` accettano il nuovo parametro `solo_attivi`, che esclude chi non ha ancora un account attivo.
