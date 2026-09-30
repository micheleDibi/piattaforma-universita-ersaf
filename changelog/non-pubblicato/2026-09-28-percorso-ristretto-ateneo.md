---
---

## Novità e correzioni

- corretto: Creando una pratica da un ateneo della pagina Pratiche, la ricerca del percorso formativo ora mostra solo i percorsi di quell'ateneo: prima si poteva scegliere per sbaglio un percorso di un'altra università, e la pratica finiva su quell'altro ateneo invece di quello da cui si era partiti.

## Dettagli tecnici

- modificato: `RelazioniPratica.jsx` filtra `GET /listini-testa/` con il parametro `universita` (già supportato dal backend) quando la scheda conosce l'ateneo di provenienza (`?universita=` nell'indirizzo di ritorno). Il tipo di corso non è filtrato allo stesso modo: l'endpoint accetta una sola descrizione, e alcune righe del pannello ne raggruppano più di una.
