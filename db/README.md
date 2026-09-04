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
│   └── 006_template_email.sql
└── rollback/                                        annullamento, ordine inverso
```

## Ordine di esecuzione

```bash
mariadb -u <user> -p admin_entedb < db/diagnostica/000_diagnostica_pre_migrazione.sql | tee diag_$(date +%F).txt

for f in db/migrations/00{1,2,3,4,5,6}_*.sql; do
  echo "== $f"; mariadb -u <user> -p admin_entedb < "$f" || break
done
```

**Nessuna migrazione modifica o cancella i dati esistenti.** Le 001–006 sono
solo DDL (colonne, tabelle, indici) più l'inserimento di due template email.
Le password si convertono una riga alla volta, al login del singolo utente:
chi non accede resta intatto. L'avanzamento si segue con
`db/diagnostica/010_stato_migrazione_password.sql`.

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
