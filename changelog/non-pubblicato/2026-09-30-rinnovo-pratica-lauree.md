---
---

## Novità e correzioni

- aggiunto: Per una pratica con percorso di tipo Lauree, la scheda mostra tre caselle "Rinnovo primo/secondo/terzo anno": si può spuntarne al più una, spuntarne un'altra toglie automaticamente la precedente, e si può anche non sceglierne nessuna.

## Dettagli tecnici

- modificato: `PraticaUpdate` (`PUT /pratiche/{id}`) accetta ora anche `pratica_rinnPrimoAnno`, `pratica_rinnSecondoAnno`, `pratica_rinnTerzoAnno`; entrambi gli schemi normalizzano il valore con la convenzione booleana legacy (vedi `src/comune/flag_legacy.py`) e rifiutano il payload se più di uno dei tre campi risulta vero. Nessuna migrazione: le colonne esistevano già.
