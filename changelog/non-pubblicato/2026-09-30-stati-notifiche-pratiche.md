---
---

## Novità e correzioni

- modificato: Le nuove pratiche nascono in Bozza; solo il Nazionale può cambiarne lo stato.
- aggiunto: Lo studente riceve una conferma al primo ingresso della pratica in Bozza; l'ufficio pratiche riceve una notifica al primo passaggio in Caricata.
- corretto: Salvataggi contemporanei della stessa pratica non duplicano le notifiche di cambio stato.

## Dettagli tecnici

- aggiunto: Storico degli stati nella transazione della pratica, template email esistenti e destinazione dell'ufficio configurabile tramite `EMAIL_NOTIFICHE_PRATICHE`; nessuna nuova migrazione.
- sicurezza: Letture correnti sotto blocco per stato, storico e visibilità della pratica, senza riutilizzare snapshot precedenti a una modifica concorrente.
- modificato: Invio email dopo il commit tramite `BackgroundTasks`, con errori registrati e senza ritentativi persistenti.
- corretto: Test degli script di deploy eseguibili su Windows con Git Bash e percorsi normalizzati; fixture di overlay e firewall separate e condivise.
