---
---

## Novità e correzioni

- modificato: Nella scheda di un sottoscrittore o attuatore il pulsante "Salva utente" non c'è più: "Salva modifiche" salva anche username, stato dell'account, utente padre e ruolo della scheda Utente, qualunque sia la scheda aperta al momento.
- modificato: La tendina "Ruolo attuatore" (Dati principali) parte già su Aderente, senza la voce segnaposto "Aderente (default)".

## Dettagli tecnici

- modificato: `SchedaUtente.jsx` non ha più un pulsante di salvataggio proprio: espone `salva()` tramite `useImperativeHandle` (ref come prop, React 19), chiamata da `NuovoSottoscrittore.jsx` in `handleSubmit` prima del resto del salvataggio. Il componente resta sempre montato (nascosto con `hidden` quando non è la scheda attiva, non smontato): altrimenti cambiare scheda prima di salvare avrebbe perso le sue modifiche non ancora salvate.
- modificato: La tendina "Ruolo attuatore" di `NuovoSottoscrittore.jsx` parte su Aderente già in creazione, letto da `GET /ruoli/`, invece di una voce segnaposto vuota.
