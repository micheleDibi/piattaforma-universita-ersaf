# Client Universo: pratiche sul backend Università

Questo delta sostituisce la precedente proposta di ponte Java. Il backend
Università ora gestisce direttamente storico, cifratura, invio e socket;
non occorre distribuire `/internal/practices/session` o il suo segreto.
La vecchia sorgente Java locale non viene ripristinata o riscritta da questo delta.

`chat-nativa-flutter.patch` contiene esclusivamente le modifiche al client
Flutter `piattaforma_universo`; `manifest.json` registra le impronte dei file
prima e dopo, senza includere altre modifiche presenti nel checkout Universo.
Il delta è già applicato nel checkout locale usato per l'implementazione.
Non applicarlo una seconda volta. Nel repository Università viene conservato
per consegnare una variazione riproducibile senza committare il lavoro altrui.

## Applicazione in un altro checkout

Dalla radice Flutter, verificare prima le impronte e lo stato Git, quindi:

```sh
git apply --check /percorso/chat-nativa-flutter.patch
git apply /percorso/chat-nativa-flutter.patch
flutter test test/realtime
```

Se il controllo fallisce, conciliare i singoli file con le modifiche locali;
non usare reset, sostituzione integrale del checkout o applicazione forzata.
Per verificare un delta già presente usare `git apply --reverse --check`.

## Attivazione

Il valore vuoto di `PRACTICE_REALTIME_BASE_URL` mantiene il percorso esistente.
Al passaggio concordato compilare con:

```sh
flutter build web --dart-define=PRACTICE_REALTIME_BASE_URL=https://universita.example.org
```

Sostituire l'origine di esempio con quella del backend dello stesso ambiente.
Sono ammessi solo HTTPS e origine senza percorso/credenziali; il client usa
`/api/chat-universo`. API dello storico, chiavi e CHAT/PRACTICE passano al nuovo
backend. Entrambe le socket ricevono lo stesso token già ottenuto da Universo.
Chat personali, ticket, typing/presenza e notifiche globali restano sul servizio
attuale. L'invio di una pratica non ripiega mai sul Java se il nuovo servizio
non risponde. Il gestore di riconnessione esistente riapre entrambe le socket;
l'indisponibilità di uno dei due servizi interrompe quindi il trasporto comune.

Gli stati di lettura e le notifiche sono conservati nelle tabelle legacy:
il backend nativo non sostituisce il distributore globale delle notifiche.
L'aggiornamento dei client è coordinato: non lasciare vecchi client che scrivono
pratiche a Java. Un vecchio client non è garantito ricevere subito eventi
prodotti dal nuovo servizio soltanto perché condivide la coda SQL.

Prerequisiti, chiavi, dataset e rollback sono in
[chat e firma](../../docs/tecnica/chat-e-firma.md#configurazione-e-pubblicazione).
Le prove usano dati sintetici: il collaudo fra le due applicazioni pubblicate
va svolto dopo la configurazione dell'ambiente condiviso.

## Blocco del vecchio writer Java

`passaggio-java.patch` (impronte in `manifest-java.json`) modifica solo il writer
PRACTICE, aggiunge due test e inoltra il flag nei compose locale/produzione.
È già applicato nella sorgente locale `realtime_lab`; non include altre modifiche
pregresse né il vecchio ponte di autenticazione. Su un altro checkout applicare
con `git apply --check`, poi eseguire `mvn package` in `realtime-service`.

Distribuire anche questo WAR al passaggio e impostare `PRACTICE_CHAT_NATIVE=true`
nell'ambiente Compose Java, ricreando il servizio. Il writer rifiuta ogni nuovo
inserimento PRACTICE prima di accedere al database; le altre destinazioni
restano operative. Il valore assente/false mantiene la modalità precedente;
valori diversi da true/false sono rifiutati. Un retry di un vecchio messaggio
già persistito può ancora ricevere la sua conferma, senza una nuova scrittura.
Per rollback invertire questo flag solo dopo aver fermato gli invii nativi.
