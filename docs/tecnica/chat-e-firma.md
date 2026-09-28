# Chat condivisa delle pratiche e firma

La conversazione di una pratica ha un solo archivio: il servizio Java di
Universo. Università legge e invia messaggi attraverso quel servizio, senza
creare tabelle di messaggistica proprie. La firma usa invece il campo già
letto dai moduli PDF, `pratiche.pratica_firma`.

## Sessione e autorizzazione della chat

Il browser parla con FastAPI usando il cookie HttpOnly e il CSRF comuni.
FastAPI controlla la visibilità della pratica con
`pratiche/accesso.py`, poi chiede una sessione breve al nuovo ingresso Java
`POST /internal/practices/session`.

Questo ingresso è esclusivamente tra server. Richiede un segreto dedicato
da file e un identificativo del dataset comune. Java confronta ID utente e
cliente, username esatto, ID e numero pratica e ID studente con i propri
dati, risolve ruolo e azienda dal proprio database e applica le ACL della
chat già usate da Universo. Account ambigui o inattivi vengono rifiutati.
Non si trasferiscono password, ruoli dichiarati dal browser o credenziali
del database. La sessione Java dura al massimo quattro minuti, non espone
un refresh token ed è revocata al termine della richiesta o della connessione.

La visibilità della scheda non assegna nuovi partecipanti alla chat. Anche
un Nazionale deve risultare autorizzato dal servizio Java alla conversazione.
Le pratiche o gli utenti creati in un clone e assenti in Universo non vengono
associati per approssimazione: l'accesso viene rifiutato. Questo ponte non
sincronizza anagrafiche e pratiche fra database diversi.

## Contratto HTTP e WebSocket

| Percorso, sotto `/pratiche/{id}` | Operazione |
|---|---|
| `GET /messaggi?cursor=…` | pagina dello storico Java, 30 elementi, testo decifrato sul backend |
| `POST /messaggi/prepara` | valida il testo e prepara il ciphertext u2 per un `clientMessageId` |
| `WS /messaggi/socket` | invio e ricezione degli eventi della sola pratica |
| `GET /firma` | anteprima e versione della firma corrente |
| `PUT /firma` | salvataggio PNG con controllo della versione |

L'handshake WebSocket richiede Origin autorizzata, cookie valido e i
sottoprotocolli `ersaf.pratiche.v1` e `csrf.<csrf_token>`. Il token CSRF
non compare nell'URL. Nginx inoltra Upgrade/Connection e Vite abilita `ws`
nel suo proxy facoltativo. Il container limita i frame in entrata a 4096 byte.
La sessione Università viene ricontrollata prima di ogni invio e ogni venti
secondi durante la connessione.

Il ponte ricostruisce il destinatario dal contesto autorizzato. Scarta eventi
personali, ticket, altre pratiche e notifiche globali. Le conferme di consegna
sono inoltrate solo per eventi ricevuti in quella connessione e caricati nello
storico dal browser. Le conferme di consegna non sono ricevute di lettura:
questa versione non cambia lo stato letto/non letto dello storico Universo.

La cifratura riprende i formati del servizio: invio u2, storico u3, u2 e
legacy v1, oltre ai messaggi legacy in chiaro. I grant storici restano quelli
di Universo: un testo per cui Java non concede la chiave non viene mostrato,
senza bloccare il resto della conversazione. Le chiavi e il JWT Java restano
sul backend. Il limite è 1000 byte UTF-8. Il Java mantiene l'unica scrittura
transazionale, l'idempotenza e la distribuzione ai partecipanti.

Il browser mantiene un invio pendente in memoria, aspetta la conferma del
server e ritenta con **lo stesso ID e lo stesso ciphertext**. Dopo la
riconnessione recupera le pagine mancanti; i messaggi sono deduplicati per ID.
Bozze e invii non vengono salvati in localStorage: ricaricare o abbandonare
la pagina perde una bozza non confermata. In questo caso verificare lo
storico prima di riscriverla. Le schede interne restano montate e conservano
la bozza quando si passa a Dati o Firma. Solo dopo un rifiuto Java
`key_epoch_stale`, che segue il controllo di idempotenza e il rollback della
scrittura, Riprova può ricifrare con la chiave dell'ora corrente mantenendo l'ID.

## Firma

Il componente canvas usa Pointer Events per mouse, touch e penna. La tela ha
dimensioni logiche costanti e coordinate proporzionali, indipendenti dal
layout mobile/desktop. Annulla e Cancella il disegno non modificano il database.

Il backend accetta soltanto PNG a singolo fotogramma entro 350 KB, lato massimo
2048 pixel e area massima 2097152 pixel. Rifiuta una tela vuota, normalizza il
tratto su fondo bianco e rimuove metadati. Una transazione con lock confronta
l'impronta SHA-256 della firma letta dal client: una modifica concorrente
restituisce 409. Nessuna nuova migrazione è necessaria.

La firma nuova aggiorna il blob esistente e il relativo flag di mancanza.
Il generatore PDF continua a leggere la stessa sorgente, applicandole la
pulizia e il ritaglio comuni. I documenti già scaricati non cambiano.

## Configurazione e pubblicazione

La chat è disabilitata quando la configurazione manca; l'API restituisce un
errore di indisponibilità. Le altre funzioni della pratica restano utilizzabili.

| Università | Java | Significato |
|---|---|---|
| `CHAT_JAVA_URL` | — | origine HTTP(S) interna del servizio, senza prefisso di percorso |
| `CHAT_JAVA_ORIGINE` | `AUTH_ALLOWED_ORIGINS` | un'Origin autorizzata dal servizio, inviata solo dal backend |
| `CHAT_JAVA_SECRET_FILE` | `UNIVERSITA_BRIDGE_SECRET_FILE` | file contenenti lo stesso segreto casuale dedicato, almeno 32 byte |
| `CHAT_DATASET` | `UNIVERSITA_BRIDGE_DATASET` | nome concordato del dataset, identico e specifico dell'ambiente |

Montare i file segreti in sola lettura, leggibili dagli utenti dei container.
Non riutilizzare JWT secret, credenziali SMTP o password di altri ingressi.
Non esporre `/internal/practices/session` sul proxy pubblico. Collegare solo
il backend Università all'indirizzo e alla porta interni del Java; con host
distinti usare una rete privata protetta o TLS. Il database resta isolato.

Lo stack di collaudo versionato isola l'API dalla LAN e il firewall notifiche
blocca le reti private. L'attivazione reale richiede quindi anche una regola
di rete mirata al servizio Java e il mount del file segreto: impostare soltanto
le variabili non basta. Queste regole dipendono dall'ambiente e non vengono
attivate automaticamente dal codice o dal deploy corrente.

Le modifiche Java sono applicate nella sorgente locale di Universo e sono
consegnate anche come [patch riproducibile](../../integrazioni/universo-realtime/istruzioni.md).
Prima di pubblicare Università, distribuire il Java aggiornato, verificare
readiness e dataset, configurare il collegamento privato e poi verificare
l'invio bidirezionale tra le due applicazioni con due account di collaudo.
Non collegare automaticamente un ambiente di test al servizio di produzione.

## Verifiche

- Gate FastAPI/React `scripts/verify-local.ps1 -Gate All`, sul solo database
  locale usa-e-getta: firma, controllo versione, riuso nei PDF, ACL, CSRF,
  preparazione messaggi, isolamento WebSocket e revoca della sessione.
- Suite Java e compilazione WAR con Maven, inclusi ingresso bridge, durata
  del token e vettore crittografico comune con Python.
- Test frontend di idempotenza, riconnessione, recupero delle pagine mancanti
  e cleanup in React StrictMode.
- Verifica visiva desktop/mobile con fixture sintetiche e HTTP/WS simulati.

Queste verifiche non costituiscono una prova sul servizio Universo pubblicato:
il collaudo bidirezionale reale resta un passaggio della pubblicazione.
