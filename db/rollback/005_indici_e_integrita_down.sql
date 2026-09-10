-- Rollback della migrazione 005.
-- Rimuove solo gli indici aggiunti automaticamente. Le chiavi esterne e la
-- UNIQUE su utente_username sono opzionali/manuali: se le hai applicate,
-- rimuovile a mano.
ALTER TABLE `clienti`
  DROP INDEX IF EXISTS `ix_clienti_email_ruolo`,
  DROP INDEX IF EXISTS `ix_clienti_ruolo`,
  DROP INDEX IF EXISTS `ix_clienti_utente`,
  DROP INDEX IF EXISTS `ix_clienti_email`;
