---
---

## Novità e correzioni

- corretto: Aprendo una pratica Corsi Singoli già salvata si vedono tutti i corsi scelti, non più solo il primo.
- modificato: Nella scheda di una pratica Corsi Singoli la sezione "Caratteristiche del percorso" è sostituita da "Corsi selezionati": una riga per corso con codice, denominazione, corso di laurea, CFU e prezzo; in creazione ogni riga ha una X per togliere il corso. Nel campo "Corsi" della sezione Iscrizione resta il numero dei corsi scelti.

## Dettagli tecnici

- aggiunto: `GET /pratiche/{id}` (e la risposta di creazione e modifica) restituisce `corsi`, l'elenco delle righe di `pratiche_listini` con codice, descrizione, prezzo salvato, CFU del dettaglio di listino valido alla data di creazione e corso di laurea; `null` nell'elenco `GET /pratiche/`, che non carica la relazione.
- modificato: `GET /listini-testa/` carica il corso di laurea con un join, per la selezione dei Corsi Singoli.
- aggiunto: `ElencoCorsiPratica.jsx`; `SchedaPratica.jsx` riconosce una pratica Corsi Singoli salvata anche dal suo `listino_tipo_corso_id`, quando l'indirizzo non porta il contesto. `formattaImporto` spostata in `lib/praticaForm.js`.
- nota: 12 pratiche Corsi Singoli del 2022 non hanno righe in `pratiche_listini` e mostrano il solo corso principale (4 di queste hanno altri corsi in `listTesta_corso2_id`/`listTesta_corso3_id`, senza prezzo per corso: non mostrati, per scelta).
