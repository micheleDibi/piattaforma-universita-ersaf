---
---

## Novità e correzioni

- aggiunto: Creando una pratica SSML o A4U si creano anche il suo articolo e il suo partitario nella gestione pagamenti, con il prezzo della pratica e una numerazione che continua quella esistente. Per A4U il codice pratica viene registrato anche come codice definitivo.
- modificato: Se manca un dato che serve alla parte contabile, per esempio chi crea la pratica non ha una scheda cliente, la pratica SSML o A4U non viene salvata e compare un errore.

## Dettagli tecnici

- aggiunto: `POST /pratiche/` per SSML e A4U scrive `articolo`, `articolo_pratica`, `documento` (partitario) e `documento_articolo` nello schema dei pagamenti, e per A4U una riga in `pratica_codice`, nella stessa transazione della pratica (`pratiche/dopo_salvataggio.py`, porting di `Pratica.AfterSave`). Un dato di riferimento mancante risponde 400 e non scrive nulla.
- aggiunto: Configurazione `SCHEMA_GESTIONE_PAGAMENTI` (predefinito `admin_gestione_pagamenti`): nome dello schema dei pagamenti sullo stesso server, letto con la connessione di `DATABASE_URL`, il cui utente deve poterci scrivere.
- aggiunto: Migrazione `022_contatori_articolo_partitario.sql`, con rollback: porta `pratiche_contatori.prefisso` a 32 caratteri. I contatori `ARTICOLO_PRATICA_` e `PARTITARIO_PRATICA_` si riallineano nel codice al massimo esistente a ogni uso (`prossimo_numero_oltre`).
- modificato: Il gruppo articolo si sceglie dall'id del tipo di corso: Master area scuola e Master classi di concorso vanno su `PRATICA MASTER`, Corsi di formazione su `PRATICA CORSI DI ALTA FORMAZIONE`.
- rimosso: Rispetto all'originale restano fuori le cartelle FTP della pratica (`ftp_path` non ha percorsi per le pratiche e il backend non gestisce ancora i file) e l'azzeramento di `pratica_pathFile` al cambio di stato (PDF del gestionale precedente, non usato da questo backend).
