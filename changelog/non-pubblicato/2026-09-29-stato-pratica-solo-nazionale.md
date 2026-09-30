---
---

## Novità e correzioni

- aggiunto: Una pratica nasce sempre in stato Bozza. Da quel momento, solo il Nazionale può cambiarne lo stato.

## Dettagli tecnici

- modificato: `POST /pratiche/` ignora un eventuale `pratica_stato_id` inviato e forza sempre lo stato iniziale a Bozza. `PUT /pratiche/{id}` scarta silenziosamente `pratica_stato_id` se chi chiama non è Nazionale, stessa regola già in vigore per `azienda_id`.
