-- Rollback della migrazione 004.
-- ATTENZIONE: disconnette tutti gli utenti loggati. La tabella legacy
-- utente_session non viene toccata.
DROP EVENT IF EXISTS `ev_purge_auth_sessione`;
DROP TABLE IF EXISTS `auth_sessione`;
