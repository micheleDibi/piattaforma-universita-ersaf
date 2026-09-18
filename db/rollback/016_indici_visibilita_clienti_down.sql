-- Rollback della migrazione 016: rimuove i due indici della visibilita'.
-- La regola continua a funzionare, solo piu' lentamente.
ALTER TABLE `clienti`
  DROP INDEX IF EXISTS `ix_clienti_azienda_utente`;

ALTER TABLE `utenti`
  DROP INDEX IF EXISTS `ix_utenti_padre`;
