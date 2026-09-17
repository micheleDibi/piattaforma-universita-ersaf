# Deploy sul collaudo

Questo documento spiega:

- come si pubblica la piattaforma sull'ambiente di collaudo con `scripts/deploy.ps1`;
- che cosa succede sul server;
- come nasce il numero di versione mostrato nel menu;
- come quel numero finisce in `CHANGELOG.md`.

Le variabili citate sono elencate in [Configurazione](riferimenti/configurazione.md). Le regole delle migrazioni sono in [db/README.md](../../db/README.md), l'elenco delle migrazioni in [Migrazioni](riferimenti/migrazioni.md).

## Chi pubblica e quando

- Si pubblica `origin/main`. Chi pubblica, quando lo fa e il percorso di una modifica fino a `main` sono descritti in [Convenzioni](convenzioni.md).
- L'ambiente di collaudo è uno solo, e lo usa anche chi non sviluppa: una pubblicazione cambia ciò che vedono tutti.
- Lo script non impone queste regole: accetta anche altri riferimenti git e si limita a un avviso (vedi più avanti il parametro `-Ref`).

## Lo script `scripts/deploy.ps1`

Lo script esegue l'intero ciclo da un PC Windows:

1. controlli locali;
2. pacchetto del codice;
3. invio al server;
4. comandi remoti.

Tutto ciò che gira sul server sta in `deploy/remote/*.sh`. A ogni esecuzione lo script concatena questi file e li passa a `bash` via SSH. Sul server restano solo le release estratte, i dati e la configurazione (`deploy/remote/00-lib.sh:4-8`; funzioni `Get-RemoteBundle` e `Invoke-Remote` di `scripts/deploy.ps1`).

### Ambiente

- **Windows PowerShell 5.1.** Esempio:

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\deploy.ps1 -Action preflight
  ```

  `-ExecutionPolicy Bypass` è la forma che lo script stesso suggerisce nei propri messaggi: su un PC con un criterio di esecuzione restrittivo, senza quell'opzione il comando non parte.

- **Strumenti nel `PATH`:** `ssh`, `scp`, `git` e `tar`, controllati all'avvio (funzione `Test-LocalTools`). Le azioni `setup` e `authorize-key` usano anche `ssh-keygen`.
- **Accesso a GitHub**, per il `fetch` del riferimento da pubblicare.
- **VPN aziendale collegata.** Lo script la verifica con un ping al server. Non apre una connessione alla porta SSH, per non essere scambiato per una scansione (funzione `Test-Vpn`).
- **Una chiave SSH autorizzata sul server:**
  1. Chi entra nel team esegue una volta `-Action setup`. Il comando genera una chiave dedicata senza passphrase, registra la chiave host del server scritta nello script, aggiunge un alias in `~/.ssh/config` e prova l'accesso.
  2. Se l'accesso non funziona ancora, lo script mostra la chiave pubblica da inviare a chi gestisce il server.
  3. Chi ha già accesso autorizza la chiave con `-Action authorize-key -KeyFile <file.pub>` e conferma digitando una parola.
- **Python e Node non servono** per il deploy: le immagini si costruiscono sul server. Python serve solo per il timbro del changelog, che è facoltativo.

Se il server venisse reinstallato, la chiave host scritta nello script (variabile `$ChiaveHostServer`) va aggiornata.

### Azioni

`-Action` è il primo parametro. Il valore predefinito è `deploy`.

| Azione | Cosa fa |
|---|---|
| `setup` | Configura il PC al primo utilizzo: chiave SSH, chiave host, alias, prova di accesso. |
| `authorize-key` | Autorizza sul server la chiave pubblica di un collega (`-KeyFile`). |
| `preflight` | Esegue controlli in sola lettura, sul PC e sul server. |
| `install` | Prima installazione: cartelle, segreti generati sul server, configurazione, clone del database e primo deploy (di `origin/main`, con il `-Ref` predefinito). |
| `deploy` | Pubblica il riferimento `-Ref`. I dati del clone restano. |
| `build` | Costruisce le immagini sul server senza toccare i container in esercizio. |
| `refresh-clone` | Salva una copia del clone attuale e lo ricrea dal database sorgente. Chiede conferma. |
| `configure-source` | Registra sul server le credenziali di lettura del database sorgente. |
| `rollback` | Torna alla release precedente. |
| `backup-db` | Salva uno snapshot del clone. |
| `restore-db` | Sostituisce il clone con uno snapshot (`-Snapshot <nome>`), poi applica le migrazioni della release attiva non ancora registrate e riavvia l'applicazione con la verifica. Chiede conferma. |
| `publish-domain` | Pubblica il collaudo su un dominio servito dal reverse proxy della rete locale (`-Domain`, `-ProxyIp`). |
| `unpublish-domain` | Toglie la pubblicazione sul dominio: resta solo il tunnel SSH. |
| `status` | Mostra la release attiva e la precedente, le release presenti, i container, lo spazio, gli snapshot e il numero di voci nella cartella delle email. |
| `logs` | Mostra le ultime righe di log di un servizio (`-Service`, `-Tail`). |
| `verify` | Ripete la verifica dello stack. |
| `stop` | Ferma solo i container del collaudo. |
| `start` | Riavvia i container e ripete la verifica. |
| `tunnel` | Apre un tunnel SSH verso il collaudo, raggiungibile su `http://localhost:<porta>` (`-LocalPort`). |

**Note sulle azioni.**

- `install`:
  - se le credenziali della sorgente non sono ancora registrate, si ferma per chiederle (codice remoto 10, `deploy/remote/20-install.sh:122-123`);
  - chiede conferma prima di clonare.
- `configure-source` registra le credenziali di lettura del database sorgente. Servono solo al dump, che è in sola lettura: meglio un utente senza privilegi di scrittura, ma lo script non lo verifica e si limita a consigliarlo (`deploy/remote/40-db.sh:4-7`).
- `rollback`:
  - non annulla le migrazioni già applicate (`deploy/remote/70-deploy.sh:86`);
  - scambia la release attiva con la precedente, quindi un secondo `rollback` torna alla release di partenza (`deploy/remote/70-deploy.sh:84`).
- `restore-db`:
  - non salva prima il clone attuale (`deploy/remote/40-db.sh:105-119`). Se serve una copia, eseguire prima `backup-db`;
  - dopo l'import applica le migrazioni della release attiva (`deploy/remote/40-db.sh:116`, `deploy/remote/50-migrate.sh:45`). Per tornare indietro con uno snapshot pre-migrazione occorre quindi che sia attiva una release che non contiene quelle migrazioni: prima `rollback`, poi `restore-db`.
- Host, indirizzi, porte e nomi predefiniti sono parametri dello script (blocco `param` di `scripts/deploy.ps1`) e non si riportano qui.

### Il parametro `-Ref`

- **Predefinito: `origin/main`.** Per i riferimenti che iniziano con `origin/`, lo script esegue prima un `fetch`: si pubblica ciò che è su GitHub (funzione `Update-RemoteRef`).
- **Altri riferimenti** (un ramo, un tag, uno SHA) sono ammessi, purché git li risolva in un commit.
  - Lo script mostra un avviso in giallo: il collaudo resterà su quel codice finché qualcuno non ripubblica (funzione `Publish-Release`).
  - Per i riferimenti che non iniziano con `origin/` non c'è `fetch`.
- **Stringa vuota** (`-Ref ''`): si pubblica l'albero di lavoro.
  - Il pacchetto contiene i file tracciati e i non tracciati non ignorati di `backend`, `frontend`, `db` e `deploy`.
  - Serve solo per le prove.
  - Se ci sono modifiche non committate, `RELEASE_INFO` le segnala con `albero_modificato=true`.

**Attenzione.** Il codice dell'applicazione viene dal riferimento scelto. `deploy.ps1` e gli script remoti, invece, sono quelli della cartella da cui si lancia il comando (variabile `$RemoteScripts` e funzione `Get-RemoteBundle`). Prima di pubblicare, conviene aggiornare il proprio checkout di `main`.

## Sequenza del deploy

### Sul PC

1. **Controlli locali:** strumenti, cartella `deploy\remote`, VPN.
2. **Riferimento:** `fetch` e calcolo dello SHA.
3. **Istante:** l'orologio del PC fornisce un solo istante (funzione `Publish-Release`), da cui nascono:
   - l'identificativo della release, `AAAAMMGG-hhmmss-<primi 7 caratteri dello SHA>`;
   - l'istante di aggiornamento, in formato ISO 8601 con il fuso del PC.
4. **Pacchetto:** `git archive` delle cartelle `backend`, `frontend`, `db` e `deploy` al riferimento scelto. Con `-Ref` vuoto non c'è `git archive`: il pacchetto è un `tar` dei file dell'albero di lavoro (funzione `New-ReleaseArchive`).
5. **Invio:** `scp` nella cartella `incoming/` del server. L'archivio locale viene poi cancellato.
6. **Comando remoto `deploy`,** con l'identificativo, lo SHA, l'indicatore di albero modificato e l'istante.

### Sul server

La sequenza è in `cmd_deploy` (`deploy/remote/70-deploy.sh:32-68`). I percorsi sono relativi alla cartella base del deploy (`ERSAF_DEPLOY_BASE`).

1. **Preparazione.**
   - L'ambiente deve essere già installato.
   - Un lock sul file `.lock` impedisce due operazioni contemporanee.
   - Tutto l'output va anche in `logs/deploy-<id>.log`.
2. **Preflight** (`deploy/remote/10-preflight.sh`). Controlla Docker, spazio, memoria, porta web, raggiungibilità dei registri di immagini e pacchetti, e la sorgente. Basta un controllo fallito per fermare il deploy.
3. **Spazio.** Sulla cartella base serve uno spazio libero minimo (`MIN_FREE_GIB_DEPLOY` in `deploy/remote/00-lib.sh`).
4. **Release** (`deploy/remote/30-release.sh:60-81`):
   1. assegna il numero di versione (vedi la sezione Numero di versione);
   2. estrae l'archivio in `releases/<id>` (se la cartella esiste già, si ferma);
   3. normalizza i fine riga;
   4. scrive `RELEASE_INFO`;
   5. valida `deploy/compose.yml`;
   6. costruisce le immagini `api` e `web`.
5. **Notifiche.** Solo se le notifiche reali sono attive: copia la configurazione della rete dedicata e installa le sue regole di firewall (`deploy/remote/26-notifiche.sh`). È l'unico punto che installa quelle regole: nessun'altra azione le crea (`deploy/remote/70-deploy.sh:46`).
6. **Database.**
   - Avvia il database del clone e aspetta che sia pronto.
   - Con `install`, se il clone non c'è ancora, lo crea dalla sorgente.
   - Se il clone manca, il deploy si ferma.
7. **Migrazioni** (`deploy/remote/50-migrate.sh`), prima dell'attivazione.
   - I file `db/migrations/*.sql` vengono confrontati con il registro `_deploy_migrazioni` del clone, che conserva nome e SHA-256 di ogni migrazione.
   - Una migrazione già registrata ma con contenuto diverso ferma il deploy.
   - Se ci sono migrazioni nuove, prima si salva un backup del clone in `snapshots/clone-pre-migrazione-*.sql.gz`, poi le migrazioni si applicano in ordine.
8. **Attivazione** (`deploy/remote/70-deploy.sh:4-14`).
   - La release attiva viene registrata come precedente in `shared/previous_release`.
   - `RELEASE_TAG` e `RELEASE_DIR` vengono aggiornati in `shared/compose.env`.
   - Il collegamento `current` punta alla nuova release.
   - A `shared/api.env` si aggiungono solo le chiavi nuove che mancano (`deploy/remote/20-install.sh:71-87`).
9. **Verifica** (`deploy/remote/60-verify.sh:50-62`). Avvia `api` e `web`, aspetta che siano sani e controlla:
   - `/healthz` e `/api/salute`;
   - la pagina dell'applicazione, servita anche quando si apre direttamente un percorso interno come `/elenco` (`deploy/remote/60-verify.sh:14-16`, `frontend/nginx.conf:66-69`);
   - un login con un utente inesistente, che deve rispondere 401;
   - la presenza di utenti nel clone;
   - l'assenza di errori di configurazione nei log dell'API.
10. **Registrazione della versione.** Il numero della release diventa l'ultimo pubblicato, in `shared/ultima_versione`.
11. **Pulizia** (`deploy/remote/30-release.sh:83-96`). Oltre alla release attiva e alla precedente, si tengono le release più recenti (tre con la configurazione predefinita, `KEEP_RELEASES`). Le altre vengono cancellate insieme alle loro immagini.

### Se qualcosa va storto

**Verifica fallita dopo l'attivazione.** Parte il rollback automatico alla release precedente (`deploy/remote/70-deploy.sh:18-29`). Il comando remoto esce con uno di questi codici:

| Codice remoto | Significato |
|---|---|
| 3 | Deploy annullato e release precedente ripristinata. Oppure primo deploy fallito, senza una release a cui tornare. |
| 4 | Deploy fallito e rollback non riuscito: serve un intervento manuale (azioni `status` e `logs`). |

Le migrazioni già applicate restano. Per annullarle si ripristina uno snapshot pre-migrazione con `restore-db`, ma solo quando è attiva una release che non contiene quelle migrazioni: dopo un rollback lo è, altrimenti il ripristino le riapplica subito. In alternativa ci sono gli script di `db/rollback` (vedi [db/README.md](../../db/README.md)); in quel caso la riga della migrazione resta nel registro `_deploy_migrazioni` del clone, quindi il deploy successivo non la riapplica.

**Guasto prima dell'attivazione** (preflight, spazio, build, database, migrazioni).

- Il comando remoto esce con un errore e non c'è rollback: `shared/compose.env` non è cambiato, quindi la release precedente è ancora attiva.
- Sul disco restano:
  - la cartella della release fallita, con il suo `RELEASE_INFO`, cancellata poi dalla pulizia di un deploy riuscito;
  - le migrazioni eventualmente già applicate.

**Contatore delle versioni.** Se il deploy fallisce prima che la verifica riesca, il contatore non avanza. Un errore successivo alla verifica, per esempio durante la pulizia finale, arriva invece con il numero già registrato (`deploy/remote/70-deploy.sh:61-65`): vedi i casi limite del timbro.

**Sul PC:**

- un codice remoto diverso da 0 e da 255 produce `ERRORE: comando remoto 'deploy' terminato con codice N` e l'uscita con codice 1;
- il codice 255 dà un messaggio diverso, sulla connessione SSH non riuscita, e invita a eseguire `setup` (funzione `Invoke-Remote`). Se il 255 arriva a deploy avviato, la connessione può essere caduta mentre il server lavorava: prima di rieseguire `setup` o di ripubblicare conviene guardare `status`;
- con esito 0, lo script ricorda come aprire il tunnel ed esce con 0.

## Il collaudo

### Il database è una copia

- Il clone nasce da un dump in sola lettura del database sorgente: uno snapshot consistente, senza lock e senza scritture (`deploy/remote/40-db.sh:4-28`).
- L'API sta su reti interne e non può raggiungere il database sorgente (`deploy/compose.yml:7-11`). Quello che si prova in collaudo non arriva in produzione.
- Il clone contiene dati personali: i dump restano sul server (`deploy/remote/40-db.sh:10-11`).

### Email e SMS

**Configurazione iniziale.** Con la configurazione creata da `install`, email e SMS non partono: vengono scritti su file sul server (`EMAIL_BACKEND=file` e `SMS_BACKEND=file` in `shared/api.env`, `deploy/remote/20-install.sh:62-65`). Le email finiscono in `state/email`, gli SMS in una sua sottocartella.

- L'azione `status` mostra il numero di voci della cartella delle email (`deploy/remote/80-status.sh:15`). La sottocartella degli SMS vale una voce sola, quindi gli SMS non vengono contati.
- Chi deve leggere un messaggio lo chiede a chi pubblica.
- Una volta creato, `shared/api.env` non viene riscritto dai deploy successivi.

**Notifiche reali.** Per attivarle servono due modifiche manuali sul server, che nessuna azione dello script esegue, e poi una pubblicazione:

1. **In `shared/compose.env`:** `NOTIFICHE_REALI=si`. Con questa chiave ogni comando `compose` aggiunge all'API una rete dedicata con uscita verso l'esterno (`deploy/compose.notifiche.yml`, `deploy/remote/00-lib.sh:94-101`).
2. **In `shared/api.env`:** i canali di invio reali, cioè `EMAIL_BACKEND=smtp` con i parametri SMTP e `SMS_BACKEND=skebby` con le credenziali del fornitore SMS. Senza quelle credenziali l'API non parte (`backend/src/notifiche/config_sms.py:16-19`, `backend/src/main.py:71-72`).
3. **Poi `-Action deploy`.** È il deploy a installare le regole di firewall di quella rete: uscita consentita solo verso le porte HTTPS e SMTP di indirizzi pubblici, rete locale e servizi del server bloccati (`deploy/remote/26-notifiche.sh:5-48`). Le regole restano installate e vengono riapplicate al riavvio del server.

**Attenzione.** Le altre azioni che riavviano l'API (`start`, `rollback`, `restore-db`, `refresh-clone`, `publish-domain`, `unpublish-domain`) collegano l'API a quella rete ma non installano le regole. Eseguirne una dopo aver messo `NOTIFICHE_REALI=si` e prima del primo `deploy` lascia l'API con un'uscita verso l'esterno senza restrizioni, fino al deploy successivo (`deploy/remote/80-status.sh:42-48`, `deploy/remote/70-deploy.sh:46`). Vedi [Limiti noti](sicurezza.md#limiti-noti).

Da quel momento i messaggi del collaudo partono davvero verso i destinatari presenti nel clone. La verifica del deploy non prova un invio reale: il collaudo gira con l'ambiente di sviluppo (`ERSAF_ENV=sviluppo`, `deploy/remote/20-install.sh:44`), quindi i controlli che in produzione pretendono l'invio via SMTP con un host configurato non si applicano (`backend/src/config.py:280-291`) e una configurazione SMTP incompleta non ferma l'avvio.

### Accesso

- **Tunnel SSH:** `-Action tunnel`, poi `http://localhost:<porta>` nel browser.
- **Dominio:** se il collaudo è stato pubblicato con `publish-domain`, si raggiunge anche su `https://<dominio-collaudo>`. La porta web è aperta solo al reverse proxy.
- **Dopo una pubblicazione:** `index.html` non viene messo in cache (`frontend/nginx.conf:62-64`), quindi basta ricaricare la pagina.

### Se il collaudo non risponde

- Chi sviluppa non interviene sul server. Segnala che cosa stava facendo e che cosa ha visto.
- Chi pubblica usa le azioni `status`, `logs` e `verify`.
- Una pubblicazione che non supera la verifica torna da sola alla versione precedente.

## Numero di versione

### Come nasce

- **Contatore sul server.** Il file `shared/ultima_versione` contiene l'ultimo numero pubblicato con successo, e ogni nuova release prende quel numero più uno (`deploy/remote/30-release.sh:23-40,63`).
  - Se il file non esiste, la numerazione parte da 1.
  - Se il file è illeggibile, il server avvisa e riparte da 1.
- **`releases/<id>/RELEASE_INFO`** (`deploy/remote/30-release.sh:11-21`) ha una riga `chiave=valore` per ciascuna di queste chiavi:
  - `release`, `git_sha`, `albero_modificato`, `versione`, `aggiornata`;
  - `data` e `operatore`, cioè l'ora e l'utente del server.
- **Istante `aggiornata`.** È l'istante preso sul PC di chi pubblica (vedi la sequenza sul PC).
  - Il server lo accetta solo nel formato `AAAA-MM-GGThh:mm:ss` seguito dal fuso (`+hh:mm`, `-hh:mm` o `Z`).
  - Altrimenti lo lascia vuoto (`deploy/remote/30-release.sh:64-66`).
- **Build del frontend.** Numero e istante arrivano come build-arg `VITE_VERSIONE` e `VITE_AGGIORNATA_IL` (`deploy/compose.yml:86-88`).
  - Nel `frontend/Dockerfile` sono dichiarati dopo `npm ci`, per non invalidare la cache delle dipendenze (`frontend/Dockerfile:11-15`).
  - Restano quindi incorporati nell'immagine della release.
- **Menu.** Mostra "Versione N" e "Aggiornata il gg/mm/aaaa alle hh:mm" (`frontend/src/lib/versione.js:3-25`).
  - L'ora è sempre nel fuso Europe/Rome, qualunque sia il fuso del dispositivo.
  - Senza un numero valido, il menu mostra "Versione di sviluppo".
  - Senza un istante valido, mostra solo il numero.

### Quando il numero si consuma

Il contatore avanza solo dopo una verifica riuscita (`deploy/remote/70-deploy.sh:61-62`).

| Caso | Contatore |
|---|---|
| Deploy riuscito, anche con `install` | Avanza. |
| Deploy riuscito di un riferimento diverso da `origin/main`, compreso l'albero di lavoro | Avanza: il numero è consumato. |
| Deploy fallito prima della verifica riuscita, con o senza rollback | Non avanza: il deploy successivo riusa lo stesso numero. |
| Azione `build` | Non avanza (`deploy/remote/90-main.sh:14`). |
| `rollback` manuale | Non cambia. Il menu mostra il numero incorporato nell'immagine della release ripristinata. |
| Scrittura del contatore non riuscita dopo un deploy riuscito | Non avanza. Il server avvisa che il deploy successivo riuserà il numero (`deploy/remote/30-release.sh:46-50`). |
| File del contatore cancellato | La numerazione riparte da 1. |

Il `RELEASE_INFO` di una release fallita resta sul disco con un numero che verrà assegnato anche alla release successiva.

## Timbro del changelog

Dopo ogni pubblicazione riuscita di `origin/main`, `deploy.ps1` scrive in `CHANGELOG.md` una sezione con:

- lo stesso numero e la stessa ora mostrati nel menu;
- le voci dei frammenti di changelog.

Il formato dei frammenti e le regole della cartella `changelog/non-pubblicato/` sono in [Documentazione](documentazione.md).

### Quando parte

- Dopo un deploy riuscito, sia con `-Action deploy` sia con `-Action install`: sono i due soli rami che lo chiamano (funzione `Invoke-TimbroChangelog`).
- Se il deploy fallisce, lo script si ferma prima e il timbro non parte.
- Con un `-Ref` diverso da `origin/main`, compreso l'albero di lavoro, lo script scrive in giallo che il numero di versione è stato consumato ma non viene scritto in `CHANGELOG.md`, e non lancia il timbro. Lo stesso controllo è ripetuto nello strumento: lanciato a mano con un `--ref` diverso, stampa il medesimo messaggio ed esce con 0 senza fare nulla (`scripts/documentazione/timbra_changelog.py:354-357`).
- Non fa mai fallire un deploy: i suoi errori diventano avvisi, e lo script esce comunque con 0.

### Che cosa fa

1. **Lettura di `RELEASE_INFO`.** `deploy.ps1` legge il `RELEASE_INFO` della release appena pubblicata con il comando remoto `release-info`, in sola lettura (`deploy/remote/80-status.sh:18-28`).
   - Il comando stampa solo `release`, `git_sha`, `albero_modificato`, `versione`, `aggiornata` e il valore del contatore: `data` e `operatore` restano sul server.
   - Lo script controlla che i valori ci siano tutti e siano coerenti con la release pubblicata: stesso identificativo, commit di quaranta caratteri che inizia con la parte finale dell'identificativo, numero di versione valido, albero non modificato.
2. **Avvio del timbro.** Lo script cerca un Python 3.10 o successivo, provando in ordine `py -3`, `python` e `python3`, e lancia `scripts/documentazione/timbra_changelog.py` (funzione `Find-PythonTimbro`). Ogni candidato deve superare un breve controllo della versione: chi non lo supera viene scartato.
3. **Preparazione.** Il timbro (`scripts/documentazione/timbra_changelog.py:289-332`):
   - controlla che git abbia `user.name` e `user.email`;
   - aggiorna `origin/main` con un `fetch`;
   - controlla che lo SHA pubblicato esista nel repository e sia contenuto in `main`;
   - lavora in un worktree temporaneo, che rimuove sempre alla fine.

   A parte l'aggiornamento di `origin/main`, il checkout di chi pubblica non viene toccato.
4. **Raccolta.** Il timbro prende i frammenti di `changelog/non-pubblicato/` presenti nello SHA pubblicato e ancora identici su `main`.
   - Un frammento modificato dopo la pubblicazione resta per la versione successiva.
   - Un frammento non valido viene segnalato e lasciato dov'è.
   - `LEGGIMI.md` non si tocca mai.
5. **Scrittura.** Nel punto indicato dal marcatore di inserimento di `CHANGELOG.md`, il timbro scrive la sezione `## Versione N — gg/mm/aaaa hh:mm`, tenendo le versioni in ordine decrescente.
   - L'ora è in Europe/Rome, come nel menu.
   - Senza istante, il titolo è `## Versione N`.
   - Senza frammenti, la sezione contiene "Nessuna modifica documentata."
   - Sotto il titolo c'è un commento con numero e commit: serve a riconoscere una versione già timbrata e non va tolto.
6. **Commit e push.**
   - Il timbro cancella i frammenti raccolti, fa il commit "Changelog: Versione N", senza passare dagli hook locali, e lo invia a `main`.
   - Se l'invio non riesce, ricontrolla `origin/main`: solo se nel frattempo è avanzato, rifà una sola volta la sezione sopra il `main` aggiornato e riprova. Non esegue alcun rebase (`scripts/documentazione/timbra_changelog.py:309-327`).

**Avvisi che non fermano il timbro:**

- il contatore sul server non vale N, quindi il deploy successivo riuserà lo stesso numero;
- rispetto all'ultima versione timbrata mancano dei numeri di versione, per esempio dopo un deploy di prova;
- fra l'ultima versione timbrata e quella pubblicata ci sono commit che toccano il codice senza un frammento. Il controllo guarda i singoli commit, esclusi quelli di merge (`scripts/documentazione/timbra_changelog.py:219-240`): l'avviso compare quindi anche per una pull request unita con un merge, quando il frammento sta in un commit diverso da quelli che toccano il codice.

### Prerequisiti sul PC di chi pubblica

Sono facoltativi. Senza, il deploy funziona lo stesso e il timbro si riduce a un avviso con il comando manuale.

- **Python 3.10 o successivo.** Basta la libreria standard.
- **git configurato:**
  - identità impostata (`user.name`, `user.email`);
  - credenziali di scrittura su GitHub che funzionino senza richieste interattive, perché il timbro disattiva i prompt (`scripts/documentazione/comune.py:20-27`);
  - se il remoto usa SSH, la chiave deve essere quella predefinita o quella indicata in `~/.ssh/config`: il timbro impone il proprio comando SSH, quindi un `core.sshCommand` configurato non viene usato.
- **Firma dei commit:** se è attiva, non deve chiedere una passphrase.

### Esiti del timbro

| Codice | Significato | Che cosa fare |
|---|---|---|
| 0 | Sezione scritta, oppure versione già timbrata con lo stesso commit, oppure riferimento diverso da `origin/main`. | Niente. |
| 2 | Argomenti non validi o mancanti: numero, commit o istante in un formato non accettato. Nessuna operazione su git. | Correggere gli argomenti e rilanciare il comando manuale. |
| 3 | Il numero N è già in `CHANGELOG.md` con un altro commit: il contatore sul server è ripartito, oppure non è stato registrato. | Non rilanciare. Vedi più sotto "Numero già usato". |
| 4 | Invio a `main` non riuscito: diritti mancanti, rete, oppure `main` che rifiuta i push diretti. Il messaggio distingue il caso della protezione del ramo. | Rilanciare il comando manuale stampato, da un clone con diritti di scrittura su `main`. Se `main` è protetto, il comando manuale fallisce allo stesso modo finché la protezione resta. |
| 5 | `CHANGELOG.md` o il suo marcatore mancano su `main`. Nessun commit. | Ripristinare il file (vedi [Documentazione](documentazione.md)), poi rilanciare il comando manuale. |
| 6 | Errore di git: identità mancante, `fetch` non riuscito, commit assente o non su `origin/main`, altri errori del comando. | Correggere la causa descritta nel messaggio, poi rilanciare il comando manuale. |

Un altro codice diverso da 0 indica un errore imprevisto, descritto nel messaggio. In ogni caso `deploy.ps1` mostra solo un avviso in giallo ed esce con 0.

### Numero già usato (codice 3)

Nessun frammento è stato cancellato. Per rimediare:

1. Confrontare il numero più alto presente in `CHANGELOG.md` con il valore di `shared/ultima_versione`, nella cartella base del deploy sul server.
2. Riportare il contatore al numero più alto presente in `CHANGELOG.md`. Questo intervento si fa a mano sul server: nessuna azione dello script lo esegue.
3. Ripubblicare. La nuova release prende il numero successivo, e il timbro raccoglie i frammenti rimasti.

Finché non si ripubblica, il menu del collaudo mostra un numero che nel changelog appartiene a un'altra versione.

### Comando manuale

```
python scripts/documentazione/timbra_changelog.py --ref=origin/main --versione=N --aggiornata=<ISO> --sha=<SHA>
```

- **È idempotente:** su una versione già timbrata con lo stesso commit non fa nulla.
- **Dove lanciarlo:** da un clone del repository con diritti di scrittura su `main`.
- **Argomenti:**
  - si scrivono nella forma `--nome=valore`, la sola che porti anche un valore vuoto attraverso Windows PowerShell 5.1;
  - `--aggiornata=` può restare vuoto, e allora il titolo avrà solo il numero;
  - `--ultima-versione=` è facoltativo: serve all'avviso sul contatore del server, e `deploy.ps1` lo passa sempre.
- **Dove trovare i dati.** Quando il timbro non parte o non riesce, `deploy.ps1` stampa il comando con i dati che ha, e lascia un segnaposto per quelli che mancano. In quel caso:
  - **numero e ora:** si leggono nel menu del collaudo. L'istante va scritto con il fuso, per esempio `2026-09-16T19:30:00+02:00`;
  - **commit:** si ricava con `git rev-parse <sha7>`. `<sha7>` è la parte finale dell'identificativo della release, mostrato da `deploy.ps1` durante il deploy e dall'azione `status`.

### Casi limite

- **`install`.** Pubblica `origin/main` e consuma un numero, quindi il timbro parte come per `deploy`.
- **Deploy di prova di un altro riferimento.** Consuma un numero senza timbro. Nel changelog quel numero manca, e il timbro successivo lo segnala.
- **Rollback manuale successivo.** La versione resta in `CHANGELOG.md` anche se non è più attiva. Il changelog registra le pubblicazioni, non ciò che è attivo: la release attiva si legge con `status` (`deploy/remote/80-status.sh:6-7`), il suo numero di versione nel menu.
- **Deploy fallito dopo la registrazione del numero.** Il server può registrare il numero anche se il PC riceve un errore: per esempio per un problema durante la pulizia finale, o per una connessione caduta prima che l'esito arrivi.
  - La release è attiva, ma il timbro non parte.
  - Controllare con `status`, poi lanciare il comando manuale.
- **Copia locale di `deploy.ps1` non aggiornata.** Una copia precedente all'introduzione del timbro non lo lancia e non avvisa.
  - Pubblicare sempre da un checkout aggiornato di `main`.
  - Se è già successo, lanciare il comando manuale.
- **Commit senza frammento.** Le modifiche non compaiono nel changelog, e il timbro lo segnala. La regola è in [Convenzioni](convenzioni.md).
- **Pubblicazione senza frammenti nuovi**, per esempio quando si ripubblica lo stesso codice. Ha comunque la sua sezione, con "Nessuna modifica documentata."

## Modificare gli script di deploy

- **Solo caratteri ASCII** in `scripts/deploy.ps1` e in `deploy/remote/*.sh`. Windows PowerShell 5.1 legge un `.ps1` senza BOM con la codifica di sistema, e i caratteri accentati si rovinerebbero.
- **Sintassi** compatibile con Windows PowerShell 5.1.
- **Fine riga:** `.gitattributes` impone LF per gli `.sh` e CRLF per i `.ps1`.
- **Struttura degli script remoti:**
  - ogni file definisce solo funzioni;
  - `deploy/remote/90-main.sh` è il dispatcher e deve restare l'ultimo in ordine alfabetico (`deploy/remote/90-main.sh:2-4`).
- **Che cosa è verificato.** I controlli automatici coprono solo una parte di queste regole.
  - Caratteri ASCII, assenza di BOM e sintassi bash del bundle degli script remoti: `scripts/documentazione/tests/test_deploy.py`.
  - Analisi sintattica degli script PowerShell, che però non gira con la 5.1 e quindi non ne garantisce la compatibilità. Solo per le funzioni del timbro un test cerca alcune sintassi che la 5.1 non conosce.
  - Fine riga e struttura degli script remoti non sono verificate.
- **Documento collegato.** Una pull request che tocca questi file deve aggiornare anche questo documento, oppure usare l'etichetta di esenzione. Controlli ed etichette sono descritti in [Documentazione](documentazione.md).
