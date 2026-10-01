---
---

## Novità e correzioni

- corretto: Cambiare il ruolo dalla scheda Utente di un attuatore ora viene salvato: prima "Salva modifiche" lo riportava al valore della tendina "Ruolo attuatore" di Dati principali. Le due tendine mostrano sempre lo stesso ruolo e funzionano entrambe.
- modificato: Nella scheda Utente i campi che non si hanno i permessi di modificare sono bloccati: nome utente, stato e "Cambia padre" per chi non è Regionale o Nazionale (sulle schede degli altri), il ruolo sulla propria scheda per chi non è Nazionale, e la voce Nazionale delle tendine del ruolo per chi non è Nazionale.
- rimosso: Gli avvisi "Correggi l'errore nella scheda Utente prima di salvare." e "Non hai i permessi per modificare un altro utente." non compaiono più.

## Dettagli tecnici

- modificato: Il ruolo è uno stato di `NuovoSottoscrittore.jsx` passato a `SchedaUtente.jsx` (`ruoloId`, `onCambiaRuolo`), invece di due stati separati.
- aggiunto: `lib/permessiSchedaUtente.js`, con i test, rispecchia i controlli di `PUT /utenti/{id}` e `verifica_ruolo_assegnabile`; `SchedaUtente.salva()` non manda `PUT /utenti/{id}` senza il permesso sull'account.
