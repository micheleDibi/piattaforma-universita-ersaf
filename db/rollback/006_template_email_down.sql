-- Rollback della migrazione 006.
DELETE FROM `messaggi_email`
 WHERE `messaggio_email_codice` IN ('password_reset_richiesta','password_reset_eseguito');

ALTER TABLE `messaggi_email`
  DROP INDEX IF EXISTS `uq_messaggi_email_codice`;
