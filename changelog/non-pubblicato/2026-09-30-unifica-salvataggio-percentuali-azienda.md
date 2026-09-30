---
---

## Novità e correzioni

- modificato: Nella scheda dell'azienda il pulsante "Salva percentuali" non c'è più: "Salva modifiche" salva anche le percentuali delle convenzioni universitarie. Se il salvataggio azzererebbe delle percentuali a cascata sulle aziende figlie, compare comunque la richiesta di conferma, e finché non si conferma non si salva niente (né le percentuali né il resto della scheda).

## Dettagli tecnici

- modificato: `DettaglioConvenzioniUniversitarie.jsx` non ha più stato o effetti propri: lettura, scrittura e conferma dell'azzeramento a cascata vivono nel nuovo hook `useDettaglioConvenzioni` (`frontend/src/hooks/useDettaglioConvenzioni.js`), usato sia da `SchedaAzienda.jsx` (in scrittura) sia da `SchedaAziendaAttuatori.jsx` (in sola lettura).
- aggiunto: `caricaDettaglioConvenzioni`/`salvaDettaglioConvenzioni` in `frontend/src/lib/schedaAzienda.js`.
- modificato: `SchedaAzienda.jsx` salva prima le percentuali (l'unica parte che può chiedere conferma) e solo dopo l'anagrafica; nessuna modifica al backend, restano due `PUT` distinte in sequenza.
