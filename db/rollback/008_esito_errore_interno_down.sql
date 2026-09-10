-- Rollback della migrazione 008.
--
-- ATTENZIONE: e' l'unico file di db/ che modifica dei dati, ed e' necessario.
-- Rimuovendo un valore dall'ENUM, MariaDB troncherebbe a stringa vuota le
-- righe che lo usano. Si riconducono prima a 'errore_invio', che e' il valore
-- semanticamente piu' vicino. Riguarda solo una tabella creata dalla 003, mai
-- dati preesistenti.
UPDATE `password_reset_richiesta`
   SET `prr_esito` = 'errore_invio'
 WHERE `prr_esito` = 'errore_interno';

ALTER TABLE `password_reset_richiesta`
  MODIFY COLUMN `prr_esito` ENUM(
      'email_inviata',
      'identificativo_sconosciuto',
      'ruolo_non_abilitato',
      'utente_disattivato',
      'email_mancante',
      'identificativo_ambiguo',
      'rate_limited_ip',
      'rate_limited_account',
      'errore_invio'
  ) NOT NULL;
