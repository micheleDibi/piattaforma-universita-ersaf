# Chat condivisa delle pratiche e firma

Università gestisce direttamente la conversazione di una pratica e la sua
firma grafica. La chat usa il dominio comune descritto in
[servizio realtime](realtime.md): non inoltra richieste HTTP o WebSocket a Java.
L'archivio resta la tabella legacy `messaggi`, senza copie separate dello storico.

## Sessione e autorizzazione della chat

Università usa la propria sessione cookie HttpOnly e il CSRF comune. La socket
verifica Origin, cookie e sottoprotocolli `ersaf.pratiche.v1` e
`csrf.<csrf_token>`; nessun token nell'URL. La sessione e i partecipanti vengono
ricontrollati prima degli invii e durante l'attesa degli eventi.

La partecipazione richiede un utente referente/consulente della pratica oppure
il cliente studente, aderente o consulente. Servono account attivi, un solo
cliente per utente, numero pratica e almeno due partecipanti validi. Il ruolo
Nazionale da solo non concede accesso alla conversazione. Gli ID utente e
cliente restano distinti.

L'ingresso esterno completo è `/realtime/`: sessioni, chat personali,
pratiche, ticket e notifiche sono descritti nel documento dedicato.
Il precedente namespace `/chat-universo/` per le sole pratiche è stato ritirato.

## Contratto HTTP e WebSocket

| Percorso FastAPI | Operazione |
|---|---|
| `GET /pratiche/{id}/messaggi?cursor=…` | storico decifrato, pagine da 30 |
| `POST /pratiche/{id}/messaggi/prepara` | valida 1000 byte UTF-8 e prepara u2 |
| `WS /pratiche/{id}/messaggi/socket` | invio ed eventi della sola pratica |
| `GET /pratiche/{id}/firma` | anteprima e versione della firma |
| `PUT /pratiche/{id}/firma` | salvataggio PNG con controllo versione |

Il proxy pubblico mantiene il prefisso `/api`; Nginx lo rimuove prima di
inoltrare a FastAPI e gestisce Upgrade/Connection. I frame della socket cookie
sono limitati a 4096 byte. I cursori sono firmati e legati a utente e pratica.

`chat_pratiche/scrittura.py` adatta il comando cookie al servizio comune
`realtime/scrittura.py`. Una transazione salva messaggio u3, ricevuta
idempotente, orario UTC, grant, consegne e notifiche legacy. Le notifiche
contengono ciphertext; lo storico nativo considera gli stati di lettura
condivisi. La scrittura e le quote non sono duplicate fra i trasporti.

I retry conservano ID e ciphertext. Quattro invii simultanei dello stesso
comando producono una sola scrittura; contenuti diversi con lo stesso ID
vengono rifiutati. La deduplicazione dura 30 giorni, anche dopo la pulizia
della coda di consegna. Il limite è 20 nuovi messaggi al minuto per utente.
Archivio, grant e stati di lettura non vengono eliminati dalla manutenzione.

La cifratura mantiene i contesti Universo: ingresso u2, archivio u3, lettura
u3/u2, legacy v1 e testo precedente. Le chiavi storiche richiedono i grant
esistenti. Il browser Università non riceve chiavi master o token realtime.

Bozze e invii pendenti restano in memoria. Ricaricare o abbandonare la pagina
perde una bozza non confermata; le schede Dati/Firma la conservano. Dopo
`key_epoch_stale`, quando il server ha escluso una precedente scrittura,
Riprova può ricifrare con la chiave corrente mantenendo l'ID.

## Firma

Il canvas usa Pointer Events per mouse, touch e penna. La tela ha dimensioni
logiche costanti e coordinate proporzionali al layout mobile/desktop.
Annulla e Cancella il disegno non modificano il database.

Il backend accetta PNG a singolo fotogramma entro 350 KB, lato massimo 2048
pixel e area massima 2097152 pixel. Rifiuta una tela vuota, normalizza il tratto
su fondo bianco e rimuove metadati. Un lock confronta l'impronta SHA-256 della
firma letta dal client: una modifica concorrente restituisce 409.

La nuova firma aggiorna il blob esistente e il flag di mancanza. Il generatore
PDF legge la stessa sorgente con pulizia e ritaglio comuni. I documenti già
scaricati non cambiano. Nessuna migrazione specifica è richiesta per la firma.

## Configurazione e pubblicazione

La chat cookie e il servizio realtime sono parte del backend e usano il keyring
`CHAT_CHIAVI_FILE` / `CHAT_CHIAVE_VERSIONE`. Applicare **017 e 018** prima del
backend aggiornato. Il preflight controlla schema e capienza delle colonne
cifrate; le migrazioni non creano gli archivi legacy e non prevedono DROP di
tabelle condivise. La firma rimane una funzionalità distinta dalla chat.

Il deploy monta `shared/chat-secrets` in sola lettura tramite `compose.chat.yml`
con `CHAT_NATIVA=si` in `shared/compose.env`; le variabili applicative stanno in
`shared/api.env`. Il database non cambia automaticamente. Il successivo
passaggio di Universo e del vecchio servizio è descritto in
[configurazione realtime](realtime.md#configurazione-e-passaggio-successivo).
I delta di integrazione limitati alle pratiche sono storici e non vanno usati
per attivare il nuovo servizio completo.

## Verifiche

Il gate `scripts/verify-local.ps1 -Gate All` copre firma/PDF, ACL, CSRF, invio,
storico, concorrenza, quota, rollback atomico, revoca, grant, cursori e
interoperabilità dei due trasporti. Il vettore crittografico delle pratiche
è quello sintetico già validato contro Java. Le ulteriori prove del servizio
completo sono elencate in [realtime](realtime.md#verifiche-riproducibili).

Il gate documentazione controlla riferimenti e contratti. Queste prove locali
non attestano un deploy né sostituiscono il collaudo fra applicazioni
sull'archivio condiviso pubblicato.
