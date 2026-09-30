-- =============================================================================
-- 022 - Contatori per articolo e partitario della pratica
-- =============================================================================
-- DB        : admin_entedb (MariaDB 10.11, InnoDB, utf8mb4_unicode_ci)
-- Rollback  : db/rollback/022_contatori_articolo_partitario_down.sql
-- Dipende da: 020 (crea pratiche_contatori)
-- Idempotente: si (MODIFY COLUMN verso lo stesso tipo non cambia nulla)
--
-- PROBLEMA
--   Alla creazione di una pratica SSML o A4U il backend crea anche l'articolo
--   ARTICOLO_PRATICA_<n> e il partitario PARTITARIO_PRATICA_<n> nel database
--   dei pagamenti (vedi backend/src/pratiche/dopo_salvataggio.py). I due
--   progressivi usano lo stesso contatore atomico del codice pratica, ma i
--   prefissi sono lunghi 17 e 19 caratteri e `prefisso` ne ammette 10: con
--   STRICT_TRANS_TABLES l'inserimento fallirebbe, senza verrebbe troncato.
--
-- NESSUN SEED QUI (a differenza della 020)
--   Articoli e partitari stanno in un altro schema, il cui nome cambia fra
--   produzione, collaudo e test (SCHEMA_GESTIONE_PAGAMENTI): una migrazione non
--   lo conosce. Il contatore si allinea nel codice a ogni uso, al massimo
--   numerico gia' presente in quello schema, quindi riparte da li' anche se il
--   gestionale precedente ha creato altri articoli nel frattempo.
-- =============================================================================

ALTER TABLE `pratiche_contatori`
  MODIFY COLUMN `prefisso` varchar(32) NOT NULL;

-- -----------------------------------------------------------------------------
-- VERIFICA
--   SHOW COLUMNS FROM pratiche_contatori LIKE 'prefisso';
-- -----------------------------------------------------------------------------
