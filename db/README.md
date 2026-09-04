# Migrazioni database — piattaforma-universita-ersaf

Target: **MariaDB 10.11** (`admin_entedb`), InnoDB, `utf8mb4_unicode_ci`.
Tutte le migrazioni sono state applicate, rieseguite e annullate con successo su
MariaDB 10.11.14, la stessa versione del dump di produzione.

## Struttura

```
db/
├── diagnostica/                                     SOLA LETTURA
│   ├── 000_diagnostica_pre_migrazione.sql           da eseguire per prima
│   └── 010_stato_migrazione_password.sql            avanzamento del rehash pigro
├── migrations/                                      da applicare in ordine numerico
│   ├── 001_password_hashing.sql
│   ├── 002_password_reset_token.sql
│   ├── 003_rate_limiting.sql
│   ├── 004_sessioni.sql
│   ├── 005_indici_e_integrita.sql
│   ├── 006_template_email.sql
│   └── 008_esito_errore_interno.sql          il 007 non esiste, non è un buco
└── rollback/                                        annullamento, ordine inverso
```

## Ordine di esecuzione

```bash
mariadb -u <user> -p admin_entedb < db/diagnostica/000_diagnostica_pre_migrazione.sql | tee diag_$(date +%F).txt

# Il glob prende TUTTE le migrazioni in ordine numerico: non elencarle a mano,
# è così che si dimentica l'ultima.
for f in db/migrations/*.sql; do
  echo "== $f"; mariadb -u <user> -p <database> < "$f" || break
done
```

**Nessuna migrazione modifica o cancella i dati esistenti.** Le 001–008 sono
solo DDL (colonne, tabelle, indici) più l'inserimento di due template email.

> ⚠️ **`db/test/` non è una migrazione.** `db/test/schema_base.sql` fa
> `DROP TABLE` su `utenti`, `clienti`, `aziende`, `ruoli` e `messaggi_email`:
> serve a costruire da zero il database usa-e-getta della suite di test, e
> **cancella i dati** se eseguito su un database vero. Non compare nel glob
> qui sopra proprio per questo. Applicando le migrazioni a mano, non toccare
> quella cartella.
Le password si convertono una riga alla volta, al login del singolo utente:
chi non accede resta intatto. L'avanzamento si segue con
`db/diagnostica/010_stato_migrazione_password.sql`.

## Se una migrazione fallisce

Il client si ferma al primo errore, quindi il file che fallisce non lascia
nulla applicato a metà: si corregge la causa e si rilancia lo stesso comando.
Le migrazioni sono idempotenti, quindi rieseguire quelle già passate non fa
danni.

### 005 — `ERROR 1709: Index column size too large. The maximum column size is 767 bytes`

Succede quando `clienti` ha `ROW_FORMAT=COMPACT`, il formato dei database più
vecchi: lì il limite per una colonna indicizzata è 767 byte, e
`cliente_email VARCHAR(255)` in utf8mb4 ne occupa 1020. Con `DYNAMIC`, il
formato predefinito da MariaDB 10.2, il limite sale a 3072 e il problema
sparisce. L'`ALTER` della 005 aggiunge i quattro indici in un colpo solo, quindi
o passano tutti o non ne viene creato nessuno: lo stato resta pulito.

```sql
-- quali tabelle hanno ancora il formato vecchio
SELECT TABLE_NAME, ROW_FORMAT FROM information_schema.TABLES
 WHERE TABLE_SCHEMA = DATABASE() AND ENGINE = 'InnoDB'
   AND ROW_FORMAT NOT IN ('Dynamic','Compressed');

-- la correzione: riscrive la tabella, non cambia i dati
ALTER TABLE `clienti` ROW_FORMAT=DYNAMIC;
```

Poi si rilancia la 005. **Non** si risolve accorciando l'indice a
`cliente_email(191)`: significherebbe modificare la migrazione, e un indice su
prefisso si comporta diversamente nelle ricerche.

### 006 — `ERROR 1062: Duplicate entry '<codice>' for key 'uq_messaggi_email_codice'`

`messaggi_email` contiene due o più righe con lo stesso
`messaggio_email_codice`, e la UNIQUE non può essere creata. È il caso che il
commento in testa alla 006 anticipa. Poiché il file si ferma lì, i due template
del recupero password non vengono inseriti: nessuno stato intermedio.

```sql
-- 1. quali codici sono duplicati
SELECT messaggio_email_codice, COUNT(*) AS quante,
       GROUP_CONCAT(messaggio_email_id ORDER BY messaggio_email_id) AS id
  FROM messaggi_email GROUP BY messaggio_email_codice HAVING COUNT(*) > 1;

-- 2. guardare le righe PRIMA di decidere: i testi possono essere diversi
SELECT messaggio_email_id, messaggio_email_codice, messaggio_email_oggetto
  FROM messaggi_email WHERE messaggio_email_codice IN (...);
```

Quale riga sopravvive è una decisione di contenuto, non tecnica. Se non c'è un
motivo per preferirne una, si tiene quella con l'id più basso e si **rinomina**
le altre invece di cancellarle, così non si perde nessun testo:

```sql
UPDATE messaggi_email m
  JOIN (SELECT messaggio_email_codice AS c, MIN(messaggio_email_id) AS tenere
          FROM messaggi_email GROUP BY messaggio_email_codice HAVING COUNT(*) > 1) AS d
    ON m.messaggio_email_codice = d.c AND m.messaggio_email_id <> d.tenere
   SET m.messaggio_email_codice = CONCAT(m.messaggio_email_codice, '_dup', m.messaggio_email_id);
```

Poi si rilancia la 006. Attenzione: se un altro applicativo cerca quei template
per codice, rinominarli lo rompe — in quel caso vanno cancellati i doppioni
veri, non rinominati.

### La 005 fallisce dicendo che l'indice esiste già

Non dovrebbe: usa `ADD INDEX IF NOT EXISTS`. Se succede, un tentativo
precedente ha creato un indice con lo stesso nome ma colonne diverse. Si
controlla e, se non corrisponde, si elimina e si rilancia:

```sql
SELECT INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS colonne
  FROM information_schema.STATISTICS
 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'clienti'
 GROUP BY INDEX_NAME;
```

### `ERROR 1064` con `IF NOT EXISTS` dentro `ALTER TABLE`

Il database non è MariaDB. `ADD COLUMN IF NOT EXISTS` e `ADD INDEX IF NOT
EXISTS` esistono solo in MariaDB: su MySQL 8 o 9 sono un errore di sintassi.
Queste migrazioni richiedono MariaDB, come la produzione.

## Proprietà garantite

| Proprietà | Stato |
|---|---|
| Idempotenza (riesecuzione senza errori) | verificata sulle 001–006 |
| Rollback pulito e ri-applicazione | verificato |
| Consumo del token monouso e atomico | verificato (`ROW_COUNT()` = 1, poi 0 al replay) |
| Revoca sessioni al cambio password | verificato |
| Indice usato dalla lookup per email | verificato (`EXPLAIN` → `ref` su `ix_clienti_email`) |

## Perché file .sql e non Alembic

Il progetto oggi non ha né Alembic né `requirements.txt`, e lo schema di
produzione non è gestito da migrazioni: è quello ereditato dalla piattaforma
Instant Developer (171 tabelle). Introdurre Alembic significherebbe generare un
baseline da 171 tabelle prima di poter scrivere la prima migrazione utile.
Questi file sono la via più breve; se in seguito si adotta Alembic, si parte da
uno `stamp head` sullo schema post-006.

## Prima di andare in produzione

1. Backup completo **verificato** (prova il restore, non fidarti del dump).
2. Applicare su una copia e rieseguire la diagnostica.
3. `005` lascia deliberatamente due cose a mano: le chiavi esterne su `clienti`
   e la `UNIQUE` su `utenti.utente_username` (6 duplicati da bonificare).
4. `event_scheduler` deve essere `ON` perché gli eventi di retention girino:
   `SHOW VARIABLES LIKE 'event_scheduler';`

## Il debito che resta aperto

Finché esiste `utenti.utente_password`, il database contiene password in chiaro
per ogni utente che non ha ancora rifatto login. È una scelta consapevole: la
conversione è graduale e non rompe nessuno. Quando
`010_stato_migrazione_password.sql` mostrerà pochi utenti rimasti, si potrà
decidere cosa farne — ma è una decisione da prendere con i numeri davanti, e
non esiste in questa cartella nessuno script che la esegua.
