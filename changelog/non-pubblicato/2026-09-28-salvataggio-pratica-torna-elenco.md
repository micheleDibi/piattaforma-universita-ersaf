---
---

## Novità e correzioni

- corretto: Salvare la modifica di una pratica ora torna all'elenco di provenienza, invece di restare sulla scheda con solo il messaggio "Pratica salvata.".

## Dettagli tecnici

- corretto: `SchedaPratica.jsx` non navigava dopo un salvataggio riuscito quando `praticaId` era presente (modifica): solo la creazione lo faceva, verso il dettaglio della nuova pratica. Ora la modifica torna a `ritorno` (lo stesso indirizzo del pulsante "Annulla"), come già fa `SchedaAzienda.jsx` dopo ogni salvataggio.
