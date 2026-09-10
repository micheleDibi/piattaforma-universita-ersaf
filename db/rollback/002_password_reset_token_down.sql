-- Rollback della migrazione 002. I token pendenti vengono persi: le richieste
-- di reset gia' inviate smettono di funzionare.
DROP TABLE IF EXISTS `password_reset_token`;
