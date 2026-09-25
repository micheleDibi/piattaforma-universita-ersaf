---
---

## Novità e correzioni

- modificato: La pagina Pratiche mostra il numero di pratiche per ateneo, tipologia di corso e
  stato: in cima il totale e quello di ogni stato, poi una tabella per ateneo con il totale di ogni
  riga e dell'ateneo.
- modificato: Nella pagina Pratiche si apre l'elenco filtrato scegliendo la riga di una
  tipologia, al posto del pulsante; senza abilitazione la riga resta visibile ma sbiadita.
- modificato: Sul telefono e negli spazi stretti la tabella di ogni ateneo diventa un elenco, con
  i sei stati sotto il nome della tipologia.

## Dettagli tecnici

- aggiunto: `GET /pratiche/conteggi` restituisce il numero di pratiche per università, tipo di
  corso e stato, con la stessa visibilità di `GET /pratiche/` perché passa da `query_filtrata`.
- modificato: Il pannello somma i gruppi secondo i tipi di corso di ogni riga in
  `lib/pannelloPratiche.js`; stili in `config/styles/pannelloPratiche.css` con soglie del
  contenitore a 480, 720 e 820px, nuovi campioni e ruoli di colore per gli stati, tipografia
  `text-totale` e `text-conteggio`, opzione `marginiInclusi` di `contenutoPagina()`.
