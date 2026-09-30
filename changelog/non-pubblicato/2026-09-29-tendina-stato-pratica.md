---
---

## Novità e correzioni

- aggiunto: Il Nazionale può ora cambiare lo stato di una pratica già salvata da una tendina nella scheda. Per tutti gli altri ruoli lo stato resta di sola lettura, come prima.

## Dettagli tecnici

- modificato: `frontend/src/components/pratiche/DatiPratica.jsx` mostra la tendina solo per il ruolo Nazionale (`leggiRuolo()`) e solo in modifica; `payloadPratica` invia sempre `pratica_stato_id`, ma solo il Nazionale ottiene un effetto reale lato server (vedi il frammento del 2026-09-29 sulla regola `PUT /pratiche/{id}`).
