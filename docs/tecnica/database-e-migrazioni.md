# Database e migrazioni

Questo documento spiega com'è fatto il database, perché le migrazioni sono file
SQL e quali debiti restano aperti. Non contiene dati di produzione.

Case uniche a cui rimanda:

- regole operative delle migrazioni (ordine, errori noti, prima della
  produzione): [db/README.md](../../db/README.md);
- elenco delle migrazioni e loro anomalie:
  [riferimenti/migrazioni.md](riferimenti/migrazioni.md);
- container e comandi dei test: [test.md](test.md).

## MariaDB 10.11

- Il database è MariaDB 10.11, motore InnoDB, set di caratteri `utf8mb4` con
  collation `utf8mb4_unicode_ci`.
- Il collaudo (`deploy/compose.yml`) e il container dei test
  (`db/test/docker-compose.test.yml`) usano la stessa serie 10.11.
- Il driver è PyMySQL: gli URL hanno la forma `mysql+pymysql://...`.

**Perché MariaDB e non MySQL.** Le migrazioni usano una sintassi che esiste
solo in MariaDB. Su MySQL sono un errore di sintassi: vedi
[db/README.md](../../db/README.md). Non si usa MySQL, nemmeno in locale.

**`sql_mode` diverso fra collaudo e test.** Il collaudo usa lo `sql_mode` della
sorgente, senza `STRICT_TRANS_TABLES`, perché i dati clonati si comportino come
in produzione (`deploy/compose.yml`). I test usano uno `sql_mode` severo di
proposito, e un test lo impone (`db/test/docker-compose.test.yml`;
`backend/tests/db/test_migrazioni.py`). Lo stesso troncamento, o la stessa
scrittura di `NULL` su una colonna `NOT NULL`, fallisce nei test e passa con un
avviso in collaudo. Gli ambienti non sono quindi equivalenti.

**Engine** (`backend/src/database.py`):

- `pool_pre_ping` e `pool_recycle` evitano gli errori sulle connessioni chiuse
  dal server dopo una pausa;
- `hide_parameters=True` ed `echo=False` impediscono che i parametri delle query
  (per esempio le impronte dei token) finiscano nei log.

**Orologio.** Le scadenze di sessioni, token di recupero e codici OTP si
confrontano con l'ora del database, non con quella di Python
(`backend/src/security/tempo.py`). Così un processo e un database con fusi
diversi non producono scadenze sbagliate. Non vale per tutto il codice: altri
confronti, per esempio la scadenza del documento del cliente e la finestra
dell'authenticator, usano l'orologio di Python.

## Schema legacy e tabelle nuove

Lo schema non nasce da questo repository. È quello di un gestionale già
esistente, costruito con la piattaforma Instant Developer. Il repository non
contiene la sua DDL completa.

**Tabelle esistenti mappate dai modelli.** Fra le altre:

- anagrafiche: `utenti`, `clienti`, `ruoli`, `aziende`, `aderenti_dettagli`,
  `aziende_xcod` (gerarchia);
- curriculum ed esami: `universita`, `esami`;
- prodotti formativi e decodifiche: `listini_testa`, `listini_dettagli`, le
  altre tabelle `listini_*`, `nome_universita`;
- pratiche: `pratiche` e le tabelle `pratiche_*`;
- template delle email: `messaggi_email`;
- registro OTP del gestionale: `logs_otp`.

**Tabelle create dalle migrazioni:**

- recupero password: `password_reset_token`, `password_reset_richiesta`;
- sessioni: `auth_sessione`;
- limiti del login: `auth_login_limite`;
- codici OTP e verifica dei contatti: `otp_sfide`, `otp_contatti`,
  `otp_attivazioni`, `otp_limiti`;
- secondo fattore: `auth_totp`, `auth_passkey`, `auth_mfa_utente`.

Alcune migrazioni modificano anche tabelle esistenti: colonne per l'hash delle
password in `utenti`, indici e vincoli, template in `messaggi_email`.

**I modelli seguono la DDL reale, non la definiscono.**

- Dove il database non ha un vincolo, il modello non lo dichiara. Per esempio
  `utenti.utente_username` non è unico (`backend/src/utenti/models.py`).
- Alcune chiavi esterne compaiono nei modelli solo per descrivere i join: nel
  database non esistono (per esempio `universita.cliente_id`).
- L'applicazione non chiama mai `create_all`: lo fanno solo alcuni test.
- Le differenze note fra modelli e database sono elencate in testa a
  `db/test/schema_base.sql`.

**Convenzione booleana.** Nelle tabelle legacy il vero vale -1 (in alcune
colonne 1). Vedi [architettura.md](architettura.md) e
[convenzioni.md](convenzioni.md).

## Migrazioni in file SQL

- Le migrazioni sono file `db/migrations/NNN_nome.sql`, applicati in ordine di
  nome.
- Gli annullamenti stanno in `db/rollback/`.
- L'applicazione non tiene traccia delle migrazioni applicate. In collaudo lo
  fa lo script di deploy (vedi sotto).

**Perché non Alembic.** Il motivo è in [db/README.md](../../db/README.md), con
le altre regole operative.

**Idempotenza.** Le migrazioni sono rieseguibili: usano `IF NOT EXISTS` su
colonne, indici, tabelle ed eventi, `DROP EVENT IF EXISTS` prima di ricreare un
evento, `INSERT ... ON DUPLICATE KEY UPDATE` per i template e condizioni `WHERE`
che alla seconda esecuzione non trovano più righe.

**Migrazioni pubblicate.** Una migrazione già applicata in collaudo non si
modifica: se ne scrive una nuova. Il registro del deploy rifiuterebbe un file
con contenuto cambiato, e il deploy si fermerebbe; il meccanismo è descritto in
[deploy.md](deploy.md).

**Verifiche automatiche** (`backend/tests/db/test_migrazioni.py`):

- applicazione su un database pulito;
- seconda applicazione con schema identico;
- annullamenti in ordine inverso di nome, fino a tornare allo schema base;
- valori dell'ENUM degli esiti allineati al codice.

## Eventi pianificati

Alcune migrazioni creano eventi MariaDB che ripuliscono i dati scaduti:

- richieste e token di recupero password vecchi;
- sessioni scadute;
- contatori del login;
- sfide e limiti OTP;
- authenticator avviati e mai attivati.

Gli eventi girano solo con `event_scheduler=ON`. Il container dei test e il
collaudo lo attivano all'avvio. Senza scheduler quelle tabelle non vengono
ripulite: il controllo da fare su un'altra installazione è in
[db/README.md](../../db/README.md).

## Debito tecnico

### Password in chiaro e rehash pigro

La colonna legacy `utenti.utente_password` contiene la password in chiaro di
chi non ha ancora fatto un login con il nuovo sistema. Una migrazione ha
aggiunto le colonne per l'hash, l'algoritmo e la data dell'ultimo cambio. La
conversione avviene una riga alla volta, al primo login riuscito di quell'utente:
come funziona e i test che la sorvegliano sono in [sicurezza.md](sicurezza.md).

L'avanzamento si segue con `db/diagnostica/010_stato_migrazione_password.sql`.
Togliere la colonna in chiaro è una decisione ancora aperta: vedi
[db/README.md](../../db/README.md).

### Cascade sulla relazione utente-cliente

`Utente.clienti` ha `cascade="all, delete-orphan"`
(`backend/src/utenti/models.py`). Cancellare un utente con l'ORM cancellerebbe
anche il suo cliente. A quel punto SQLAlchemy proverebbe a scrivere `NULL` nel
`cliente_id` delle righe collegate di `universita` e `pratiche`, colonne
`NOT NULL`. A seconda dello `sql_mode` e dei vincoli davvero presenti nel
database, la cancellazione fallirebbe oppure lascerebbe quelle righe con un
`cliente_id` non valido: con lo `sql_mode` del collaudo la scrittura di `NULL`
è solo un avviso, e per `universita.cliente_id` non esiste alcuna chiave
esterna reale.

Oggi nessuna rotta cancella utenti o clienti. Il difetto va corretto prima di
scriverne una.

### Nome di schema scritto nel codice

Lo script `backend/src/comune/backfill_contatti_storici.py` legge `logs_otp`
indicando nella query un nome di schema fisso. Funziona solo su un database che
ha quel nome.

## Diagnostica

`db/diagnostica/` contiene script in sola lettura. Non sono migrazioni e non
rientrano nel ciclo su `db/migrations/`.

- `000_diagnostica_pre_migrazione.sql`: fotografa i dati prima delle prime
  migrazioni. I valori attesi nei commenti vengono dai dati reali e non valgono
  per altri database.
- `010_stato_migrazione_password.sql`: mostra l'avanzamento del rehash pigro.

## Schema di test

`db/test/schema_base.sql` non è una migrazione.

- Cancella e ricrea le tabelle legacy su cui lavorano le migrazioni e i test di
  accesso, più le righe dei ruoli.
- Non contiene dati personali.
- Va eseguito solo su un database usa e getta: su un database con dati li
  cancella.

Le altre tabelle legacy (pratiche, prodotti formativi, esami) non ci sono. I
test che ne hanno bisogno le creano dai modelli con `Base.metadata.create_all`:
in quei test rispecchiano i modelli, non la DDL reale.

Container, variabili e comandi: [test.md](test.md).
