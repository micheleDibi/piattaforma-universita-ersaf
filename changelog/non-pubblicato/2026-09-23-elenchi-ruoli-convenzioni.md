---
---

## Novità e correzioni

- modificato: L'elenco Sottoscrittori comprende anche i consulenti.
- modificato: L'elenco Attuatori comprende anche gli operatori, che si trovano con il filtro per ruolo;
  gli operatori continuano a non accedere alla piattaforma.
- modificato: Nel menu la voce Attuatori compare anche a Regionale e Provinciale, e la voce Pratiche
  anche a Regionale, Provinciale e Aderente.
- modificato: Il codice nazionale di una nuova azienda viene assegnato automaticamente e non si
  può più modificare.
- modificato: Le percentuali delle convenzioni universitarie stanno nella sezione "Dettaglio
  convenzioni universitarie": si modificano dalla scheda dell'azienda e si leggono nella scheda
  Azienda di un attuatore.
- rimosso: Nell'elenco Pratiche non c'è più il filtro per studente.

## Dettagli tecnici

- aggiunto: `GET /clienti/` accetta `solo_sottoscrittori=true` (ruoli Utente e Consulente);
  `solo_utenti` resta limitato al ruolo Utente, usato dal selettore dello studente nelle pratiche.
- modificato: `solo_attuatori` comprende anche il ruolo Operatore; accesso e recupero della
  password restano ai ruoli di `RUOLI_ATTUATORE` (Aderente, Regionale, Provinciale, Nazionale).
- modificato: `POST /aziende/` genera `azienda_codice_nazionale` (22 caratteri casuali, univoco) e
  ignora il valore inviato; `PUT /aziende/{id}` non lo modifica più.
- modificato: Le voci del menu dichiarano i ruoli che le vedono con `ruoliAmmessi` in
  `frontend/src/config/routes/rotte.js`.
