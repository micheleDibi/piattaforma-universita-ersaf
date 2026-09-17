# Migrazioni database — piattaforma-universita-ersaf

Target: **MariaDB 10.11**, InnoDB, `utf8mb4_unicode_ci`.

La suite applica tutte le migrazioni su un database di prova costruito da
`db/test/schema_base.sql`, le riesegue e poi esegue i rollback presenti
(`backend/tests/db/test_migrazioni.py`): le migrazioni da sole non creano le
tabelle legacy su cui lavorano. La 014 non ha un rollback: prima di applicarla
si salva una copia dei modelli email che aggiorna, se sono stati
personalizzati, e per tornare indietro si ripristina quella copia.

Questo file contiene le regole operative: come si applicano le migrazioni, cosa
fare quando una fallisce, cosa controllare prima. Il contesto — com'è fatto lo
schema, perché le migrazioni sono file SQL, i debiti tecnici — è in
[database e migrazioni](../docs/tecnica/database-e-migrazioni.md).

## Struttura

```
db/
├── diagnostica/                                     SOLA LETTURA
│   ├── 000_diagnostica_pre_migrazione.sql           da eseguire per prima
│   └── 010_stato_migrazione_password.sql            avanzamento del rehash pigro
├── migrations/                                      da applicare in ordine numerico
├── rollback/                                        annullamento, ordine inverso
└── test/                                            database della suite di test, NON una migrazione
```

L'elenco delle migrazioni e dei rollback, con le anomalie di numerazione e i
rollback mancanti, è in [Migrazioni](../docs/tecnica/riferimenti/migrazioni.md).

## Ordine di esecuzione

```bash
mariadb -u <user> -p <database> < db/diagnostica/000_diagnostica_pre_migrazione.sql | tee diag_$(date +%F).txt

# Il glob prende TUTTE le migrazioni in ordine numerico: non elencarle a mano,
# è così che si dimentica l'ultima.
for f in db/migrations/*.sql; do
  echo "== $f"; mariadb -u <user> -p <database> < "$f" || break
done
```

In collaudo le migrazioni le applica lo script di deploy, che tiene un proprio
registro con nome e impronta di ogni file già applicato e si ferma se un file
registrato è cambiato: vedi [deploy](../docs/tecnica/deploy.md). Applicare a
mano le migrazioni su quel database lascia il registro indietro, e il deploy
successivo le riapplica — riscrivendo i modelli email personalizzati.

**Nessuna migrazione tocca le password esistenti**, ma non tutte sono solo DDL:

- la 009 aggiorna `utente_attivoSN` sulle righe di `utenti` che valevano 1, e
  il suo rollback non le riporta indietro;
- la 006, la 011, la 012 e la 014 inseriscono o aggiornano modelli email in
  `messaggi_email`;
- gli eventi di pulizia creati dalle migrazioni cancellano periodicamente le
  righe scadute o più vecchie della finestra di conservazione, solo nelle
  tabelle create dalle migrazioni stesse.

Le password si convertono una riga alla volta, al login del singolo utente o
alla conferma di un recupero password: chi non fa né l'uno né l'altro resta
intatto. Come si segue l'avanzamento è più sotto.

> **`db/test/` non è una migrazione.** `db/test/schema_base.sql` cancella e
> ricrea le tabelle legacy su cui lavorano le migrazioni e i test di accesso,
> fra cui `utenti` e `clienti`, reinserendo solo le righe dei ruoli: serve a
> costruire da zero il database usa-e-getta della suite di test, e **cancella
> i dati** se eseguito su un database vero. Non compare nel glob qui sopra
> proprio per questo. Applicando le migrazioni a mano, non toccare quella
> cartella.

## Se una migrazione fallisce

Il client si ferma al primo errore, ma i DDL di MariaDB fanno commit implicito:
le istruzioni del file che precedono l'errore restano applicate. Vale anche
dentro uno `START TRANSACTION` scritto nel file — la 003 e la 004 lo aprono, e
il primo `CREATE TABLE` lo chiude — e gli eventi di pulizia che quei due file
creano stanno comunque dopo il `COMMIT`. Dopo un errore va quindi verificato
cosa è già passato.

Si corregge la causa e si rilancia lo stesso comando: le migrazioni sono
idempotenti, quindi la riesecuzione non danneggia lo schema. Fanno eccezione i
modelli email: la 006, la 011, la 012 e la 014 riscrivono oggetto e testo dei
propri modelli, quindi una riesecuzione cancella le modifiche fatte a quei
testi dopo l'applicazione.

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
Queste migrazioni richiedono MariaDB: il collaudo (`deploy/compose.yml`) e il
container dei test (`db/test/docker-compose.test.yml`) usano la serie 10.11.

## Proprietà garantite

Le prime quattro righe le sorveglia la suite, e solo quando gira contro un
MariaDB reale: quei test portano il marcatore `mariadb` e altrimenti vengono
saltati (`backend/pytest.ini`).

| Proprietà | Come è verificata |
|---|---|
| Idempotenza (riesecuzione senza errori né cambi di schema) | `backend/tests/db/test_migrazioni.py` |
| Rollback dello schema allo stato iniziale | `backend/tests/db/test_migrazioni.py`, con tutti i rollback presenti (per la 009 e la 014 vedi sopra). Confronta lo schema, non i dati |
| Consumo del token monouso e atomico | `backend/tests/integration/test_reset_concorrenza.py` |
| Revoca di tutte le sessioni alla conferma del reset | `backend/tests/integration/test_reset_token.py`, `backend/tests/integration/test_sessioni.py` |
| Indice usato dalla lookup per email | nessun test la sorveglia: è una verifica fatta a mano quando è stata scritta la 005 |

## Perché file .sql e non Alembic

Il progetto non usa Alembic (le dipendenze sono in `backend/requirements.txt`),
e lo schema di produzione non è gestito da migrazioni: è quello ereditato dalla
piattaforma Instant Developer. Introdurre Alembic significherebbe generare un
baseline da tutte le tabelle ereditate prima di poter scrivere la prima
migrazione utile. Questi file sono la via più breve; se in seguito si adotta
Alembic, si parte da uno `stamp head` sullo schema che risulta dopo l'ultima
migrazione applicata.

## Prima di andare in produzione

1. Backup completo **verificato** (prova il restore, non fidarti del dump).
2. Applicare su una copia e rieseguire la diagnostica.
3. `005` lascia deliberatamente due cose a mano: le chiavi esterne su `clienti`
   e la `UNIQUE` su `utenti.utente_username` (prima vanno bonificati i duplicati).
4. `event_scheduler` deve essere `ON` perché gli eventi di retention girino:
   `SHOW VARIABLES LIKE 'event_scheduler';`

## Il debito che resta aperto

La colonna in chiaro `utenti.utente_password` e il rehash pigro sono spiegati
in [database e migrazioni](../docs/tecnica/database-e-migrazioni.md).

Qui la parte operativa: l'avanzamento si segue con
`db/diagnostica/010_stato_migrazione_password.sql`. Quando mostrerà pochi
utenti rimasti si potrà decidere cosa fare della colonna, con i numeri davanti.
In questa cartella non esiste nessuno script che la elimini.
