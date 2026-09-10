-- Rollback della migrazione 003.
DROP EVENT IF EXISTS `ev_purge_password_reset_token`;
DROP EVENT IF EXISTS `ev_purge_password_reset_richiesta`;
DROP TABLE IF EXISTS `password_reset_richiesta`;
