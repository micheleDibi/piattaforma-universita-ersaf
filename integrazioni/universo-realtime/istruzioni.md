# Estensione del servizio Java Universo

`pratiche-chat.patch` è il delta del servizio esistente, non un secondo
servizio di messaggistica. Si applica alla radice `realtime_lab` di Universo.
La cartella locale di riferimento non è un repository Git: il delta rende
revisionabili e trasferibili le modifiche insieme a Università.

```sh
git apply --check /percorso/pratiche-chat.patch
git apply /percorso/pratiche-chat.patch
cd realtime-service
mvn test package
```

Eseguire il controllo prima dell'applicazione e risolvere eventuali differenze
con il sorgente aggiornato, senza sovrascriverle. Se il delta è già applicato,
`git apply --reverse --check` lo riconosce. Il [manifest](manifest.json) riporta
SHA-256 dei file di partenza e di arrivo; non include configurazioni reali.

Il delta aggiunge l'ingresso interno di sessione delle pratiche, i test di
autenticazione e interoperabilità Python/Java e allinea il limite preliminare
dei messaggi al limite del formato crittografico già previsto dal servizio.
Nessuna nuova tabella o migrazione Java viene introdotta. Restano necessari
schema e migrazioni richiesti dal runtime Universo corrente, compreso il tipo
TEXT dei messaggi previsto dal limite di 1000 byte.

La [guida tecnica](../../docs/tecnica/chat-e-firma.md) descrive configurazione,
rete, autorizzazioni e verifica prima della pubblicazione. Il WAR compilato
localmente non viene distribuito da questa patch o dal deploy Università.
