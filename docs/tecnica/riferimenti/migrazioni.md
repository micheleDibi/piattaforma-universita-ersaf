# Migrazioni del database

> Pagina generata da `python scripts/documentazione/genera.py` a partire da `db/migrations/` e `db/rollback/`.
> Non modificarla a mano: rilancia il comando dopo aver cambiato le fonti.

Le regole per applicarle, annullarle e correggere gli errori sono in [db/README.md](../../../db/README.md); il contesto in [database e migrazioni](../database-e-migrazioni.md).

| Numero | File | Descrizione | Rollback |
|---|---|---|---|
| 001 | `001_password_hashing.sql` | HASHING DELLE PASSWORD (bcrypt) - colonne di supporto | `001_password_hashing_down.sql` |
| 002 | `002_password_reset_token.sql` | TOKEN DI RECUPERO PASSWORD | `002_password_reset_token_down.sql` |
| 003 | `003_rate_limiting.sql` | RATE LIMITING E AUDIT DELLE RICHIESTE DI RECUPERO | `003_rate_limiting_down.sql` |
| 004 | `004_sessioni.sql` | SESSIONI APPLICATIVE (prerequisito del requisito 14) | `004_sessioni_down.sql` |
| 005 | `005_indici_e_integrita.sql` | INDICI E INTEGRITA' SULLE TABELLE ESISTENTI | `005_indici_e_integrita_down.sql` |
| 006 | `006_template_email.sql` | TEMPLATE EMAIL DEL RECUPERO PASSWORD | `006_template_email_down.sql` |
| 008 | `008_esito_errore_interno.sql` | ESITO 'errore_interno' PER LE RICHIESTE DI RECUPERO | `008_esito_errore_interno_down.sql` |
| 009 | `009_bonifica_utente_attivo.sql` | BONIFICA DI utenti.utente_attivoSN = 1 | `009_bonifica_utente_attivo_down.sql` |
| 010 | `010_limiti_login.sql` | Contatori condivisi tra processi, indipendenti dall'esistenza dell'account | `010_limiti_login.sql` (nome irregolare) |
| 011 | `011_template_email_otp_login.sql` | TEMPLATE EMAIL OTP LOGIN NAZIONALE | `011_template_email_otp_login_down.sql` |
| 012 | `012_template_email_verifica_contatti.sql` | TEMPLATE EMAIL: VERIFICA CONTATTI E CREDENZIALI DI ACCESSO | `012_template_email_verifica_contatti_down.sql` |
| 013 | `013_verifiche_otp.sql` | Stato autonomo OTP. Il registro legacy logs_otp resta invariato | `013_verifiche_otp.sql` (nome irregolare) |
| 014 | `014_contenuti_email.sql` | Contenuti email uniformi al modello FindYourGoal | assente |
| 015 | `015_secondo_fattore.sql` | Secondo fattore a scelta per il ruolo Nazionale (ADR 0009) | `015_secondo_fattore_down.sql` |

## Anomalie

- Il numero 007 non è usato.
- Il rollback della 010 si chiama `010_limiti_login.sql`, senza il suffisso `_down`.
- L'intestazione della 010 non riporta il numero.
- Il rollback della 013 si chiama `013_verifiche_otp.sql`, senza il suffisso `_down`.
- L'intestazione della 013 non riporta il numero.
- La 014 non ha un file di rollback.
