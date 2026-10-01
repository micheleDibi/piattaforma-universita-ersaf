---
---

## Novità e correzioni

- modificato: Nella scheda azienda, se una percentuale supera quella dell'azienda padre non viene più proposto di azzerarla: il salvataggio si ferma con un errore che indica i campi da correggere e il massimo ammesso per ciascuno.
- modificato: La richiesta di conferma nel salvataggio delle percentuali ora compare solo quando i nuovi valori, più bassi, azzererebbero quelli di aziende figlie, e nomina sia gli atenei sia le aziende coinvolte. Il cambio di padre resta invariato.

## Dettagli tecnici

- modificato: `PUT /aziende/{id}/dettagli` risponde 422 con `detail.messaggio` e `detail.superamenti` (`campo`, `valore`, `limite`) quando un valore supera quello del padre, prima di calcolare la cascata; il 409 con `reset` riguarda ora solo le discendenti. Nuova `superamenti_padre` in `backend/src/aziende_xcod/servizi.py`.
- aggiunto: `messaggioSuperamento` e `messaggioAzzeramentoFiglie` in `frontend/src/lib/schedaAzienda.js`; `messaggioAzzeramento` resta per il cambio di padre.
