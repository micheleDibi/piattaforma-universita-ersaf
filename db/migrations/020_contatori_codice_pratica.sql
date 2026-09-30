-- =============================================================================
-- 020 - Contatori per il codice pratica (numerazione automatica)
-- =============================================================================
-- DB        : admin_entedb (MariaDB 10.11, InnoDB, utf8mb4_unicode_ci)
-- Rollback  : db/rollback/020_contatori_codice_pratica_down.sql
-- Dipende da: nessuna
-- Idempotente: si (CREATE TABLE IF NOT EXISTS, INSERT IGNORE)
--
-- PROBLEMA
--   Il codice pratica (MT000042, A4U_CP000007, ...) veniva assegnato in base
--   al MAX(pratica_numero) esistente per prefisso, come nella piattaforma
--   Instant Developer di origine: due salvataggi concorrenti con lo stesso
--   prefisso potevano leggere lo stesso MAX e generare lo stesso codice.
--   Questa migrazione introduce un contatore per prefisso con incremento
--   atomico (INSERT ... ON DUPLICATE KEY UPDATE ... LAST_INSERT_ID, vedi
--   backend/src/pratiche/codice.py): da solo gia' garantisce che i codici
--   generati da questo momento in poi non collidano mai fra loro.
--
-- NESSUNA UNIQUE SU pratiche.pratica_numero (a differenza della bozza
-- iniziale di questa card)
--   pratiche.pratica_numero ha gia' oggi molti valori duplicati non generati
--   da questa logica: codici legacy in formato libero ripetuti, e segnaposto
--   storici (una stringa di soli trattini, o di prova) usati piu' volte per
--   "nessun codice assegnato". Una ALTER TABLE ... ADD UNIQUE fallirebbe
--   subito con ERROR 1062, e i duplicati non sono il tipo di errore isolato
--   che si sistema rinominando due righe come nella 006 (vedi db/README.md):
--   serve una vera bonifica dei dati, decisa da chi conosce quelle pratiche,
--   non un passo automatico di questo file. Stesso trattamento gia' usato
--   dalla 005 per utenti.utente_username: la UNIQUE resta un passo manuale
--   da fare DOPO la bonifica, vedi "Prima di andare in produzione" in
--   db/README.md.
--
-- NOTA SUL DATABASE DI TEST
--   db/test/schema_base.sql non definisce `pratiche`: non fa parte delle
--   tabelle ereditate ricostruite li' (vedi la nota in testa a quel file).
--   In assenza di archivio si crea soltanto il contatore vuoto. Le prove del
--   seed preparano codici sintetici; nessun dump reale e usato dalla suite.
-- =============================================================================

START TRANSACTION;

-- Un contatore per prefisso (MT, CP, AF, CS, CL, A4U_MT, ...): la riga resta
-- bloccata fino al commit, quindi pratiche concorrenti con lo stesso
-- prefisso vengono serializzate. Vedi backend/src/pratiche/codice.py.
CREATE TABLE IF NOT EXISTS `pratiche_contatori` (
  `prefisso` varchar(10) NOT NULL,
  `ultimo_numero` int(10) unsigned NOT NULL,
  PRIMARY KEY (`prefisso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed dai codici gia' esistenti nel formato standard [A4U_]<2 lettere><6
-- cifre>: si riparte da li' invece che da zero. I codici legacy in formato
-- libero (compresi i duplicati descritti sopra) non lo rispettano e restano
-- fuori: non influenzano il contatore. INSERT IGNORE: se questo file viene
-- rieseguito dopo che l'applicazione ha gia' generato altri codici, non deve
-- sovrascrivere il contatore corrente con un MAX ricalcolato sui dati di
-- allora.
SET @seed_pratiche = IF(EXISTS (
  SELECT 1 FROM information_schema.TABLES
   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pratiche'
), 'INSERT IGNORE INTO `pratiche_contatori` (`prefisso`, `ultimo_numero`)
SELECT LEFT(`pratica_numero`, CHAR_LENGTH(`pratica_numero`) - 6) AS prefisso,
       MAX(CAST(RIGHT(`pratica_numero`, 6) AS UNSIGNED)) AS ultimo_numero
  FROM `pratiche`
 WHERE `pratica_numero` REGEXP ''^(A4U_)?(MT|CP|AF|CS|CL)[0-9]{6}$''
 GROUP BY prefisso', 'DO 0');
PREPARE seed_pratiche FROM @seed_pratiche;
EXECUTE seed_pratiche;
DEALLOCATE PREPARE seed_pratiche;

COMMIT;

-- -----------------------------------------------------------------------------
-- VERIFICA
--   SELECT * FROM pratiche_contatori ORDER BY prefisso;
-- -----------------------------------------------------------------------------
