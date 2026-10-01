---
---

## Novità e correzioni

- modificato: Il ruolo di una persona si assegna secondo chi lo assegna, sia creando un attuatore sia nella scheda Utente di sottoscrittori e attuatori: il Nazionale assegna qualunque ruolo, il Regionale solo Provinciale o Aderente, il Provinciale solo Aderente; l'Aderente non cambia ruoli. Le tendine mostrano solo le scelte ammesse.
- aggiunto: Nella scheda Utente di un attuatore, Regionale e Provinciale possono riportare a Utente chi sta sotto di loro (il Regionale un Aderente o un Provinciale, il Provinciale un Aderente).
- modificato: Dove c'è una sola scelta possibile il ruolo non ha la tendina e compare come valore bloccato: per esempio un Provinciale che crea un attuatore (solo Aderente), la propria scheda (tranne che per il Nazionale), la scheda di chi ha un ruolo più alto (un Regionale che apre un altro Regionale) e ogni scheda vista da un Aderente.
- modificato: Un nuovo sottoscrittore nasce sempre con ruolo Utente, chiunque lo crei.

## Dettagli tecnici

- modificato: `verifica_ruolo_assegnabile` (`backend/src/clienti/servizio.py`) applica `RUOLI_ASSEGNABILI` (`auth/autorizzazioni.py`) in `POST /clienti/con-utente` e `PUT /clienti/{id}`; un ruolo non ammesso risponde 403 "Non puoi assegnare questo ruolo.". Gemella lato client in `frontend/src/lib/permessiSchedaUtente.js`.
