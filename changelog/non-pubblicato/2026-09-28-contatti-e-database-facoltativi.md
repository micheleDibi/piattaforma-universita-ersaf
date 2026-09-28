---
---

## Novità e correzioni

- corretto: Negli elenchi Sottoscrittori e Attuatori gli indicatori di verifica dei contatti seguono la stessa regola della scheda, anche per gli account attivi precedenti al sistema OTP.

## Dettagli tecnici

- modificato: Lo stato dei contatti mostrato nell'anagrafica è calcolato da una funzione condivisa; restano distinte le verifiche richieste per l'accesso e il secondo fattore.
- aggiunto: DATABASE_URL_GESTIONE_PAGAMENTI e DATABASE_URL_SYS_ADMIN predispongono due connessioni facoltative, inizializzate solo al primo utilizzo e ancora prive di funzionalità collegate.
- sicurezza: Le connessioni facoltative ignorano la configurazione ordinaria durante i test e accettano solo il database locale usa-e-getta. Gli errori di configurazione non espongono indirizzi o credenziali.
