-- =============================================================================
-- 009 - BONIFICA DI utenti.utente_attivoSN = 1
-- =============================================================================
-- DB        : admin_entedb (MariaDB 10.11, InnoDB, utf8mb4_unicode_ci)
-- Rollback  : db/rollback/009_bonifica_utente_attivo_down.sql
-- Dipende da: nulla
-- Idempotente: si (la WHERE non trova piu' nulla alla seconda esecuzione)
--
-- PERCHE' SERVE
--   La convenzione della piattaforma legacy e' -1 = attivo, 0 = disattivo.
--   POST /clienti/con-utente creava le righe con utente_attivoSN = 1, che non
--   e' ne' l'uno ne' l'altro: sia servizio_login sia la validazione della
--   sessione confrontano con -1, quindi ogni utente creato da quell'endpoint
--   riceveva lo stesso 401 indistinguibile di un account inesistente. Il
--   difetto e' stato corretto nel codice; questa migrazione recupera le righe
--   gia' scritte.
--
-- QUANTE RIGHE TOCCA
--   Solo quelle con il valore 1. Nel dump di produzione non ne esiste
--   nessuna (utente_attivoSN vale -1 su 4.750 righe e 0 su 21): tutte le
--   righe con 1 sono state create dall'endpoint difettoso dopo il dump.
--   Verificare PRIMA di applicare:
--
--     SELECT COUNT(*) FROM utenti WHERE utente_attivoSN = 1;
--
--   Se il conteggio e' zero, la migrazione non ha nulla da fare ed e'
--   comunque sicuro applicarla.
--
--   NON tocca ne' le righe a -1 ne' quelle a 0: un utente disattivato
--   deliberatamente resta disattivato.
-- =============================================================================

UPDATE `utenti`
   SET `utente_attivoSN` = -1
 WHERE `utente_attivoSN` = 1;

-- -----------------------------------------------------------------------------
-- VERIFICA
--   SELECT utente_attivoSN, COUNT(*) FROM utenti GROUP BY utente_attivoSN;
--   Devono comparire solo -1 e 0.
