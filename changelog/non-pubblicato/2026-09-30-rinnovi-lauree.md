---
---

## Novità e correzioni

- aggiunto: Nelle pratiche Lauree si può scegliere il rinnovo del primo, secondo o terzo anno; la selezione di un anno esclude gli altri.
- corretto: Gli aggiornamenti parziali non possono lasciare due anni di rinnovo selezionati contemporaneamente. I valori storici restano consultabili.

## Dettagli tecnici

- modificato: Contratti HTTP della pratica separati dalla mappatura ORM; regola di rinnovo centralizzata e verificata sotto il blocco della pratica.
- corretto: Il frontend invia i flag di rinnovo solo quando sono visibili per il percorso Lauree, conservando quelli storici degli altri percorsi.
- aggiunto: Test sui flag legacy, sulla modifica parziale del rinnovo e sulla conservazione dei campi non visibili; nessuna nuova migrazione.
