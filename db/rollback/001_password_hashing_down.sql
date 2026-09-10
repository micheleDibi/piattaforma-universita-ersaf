-- Rollback della migrazione 001.
-- ATTENZIONE: elimina gli hash bcrypt generati dal rehash pigro. Gli utenti
-- gia' migrati tornano a essere verificati sulla colonna in chiaro, che la 001
-- non ha mai toccato: nessuno perde l accesso, ma si perde il lavoro di
-- migrazione svolto fino a ora.
ALTER TABLE `utenti`
  DROP INDEX  IF EXISTS `ix_utenti_password_algo`,
  DROP COLUMN IF EXISTS `utente_password_changed_via`,
  DROP COLUMN IF EXISTS `utente_password_changed_at`,
  DROP COLUMN IF EXISTS `utente_password_algo`,
  DROP COLUMN IF EXISTS `utente_password_hash`;
