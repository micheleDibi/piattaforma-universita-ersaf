---
---

## Novità e correzioni

- corretto: La generazione consecutiva di documenti di tipi diversi non accumula più la memoria del compilatore nell’API.

## Dettagli tecnici

- modificato: Ogni PDF viene compilato in un processo breve, una richiesta alla volta per processo API, con timeout e pulizia degli allegati anche in caso di interruzione.
- sicurezza: I dati del documento passano tramite stdin; gli errori del processo non espongono dati personali.
