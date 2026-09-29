-- 021 - Il ciphertext realtime puo' superare il VARCHAR(255) legacy.
-- Si allarga solo la colonna corta; archivi TEXT/LONGTEXT rimangono invariati.
-- Il database minimo dei test non contiene notifiche: nessuna tabella fittizia.
-- Non ridurre automaticamente la capienza in rollback: perderebbe messaggi.
SET @amplia_notifica = IF(EXISTS (
  SELECT 1 FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='notifiche'
    AND COLUMN_NAME='notifica_body' AND CHARACTER_MAXIMUM_LENGTH < 1403
), 'ALTER TABLE notifiche MODIFY COLUMN notifica_body TEXT NOT NULL', 'DO 0');
PREPARE amplia_notifica FROM @amplia_notifica;
EXECUTE amplia_notifica;
DEALLOCATE PREPARE amplia_notifica;
