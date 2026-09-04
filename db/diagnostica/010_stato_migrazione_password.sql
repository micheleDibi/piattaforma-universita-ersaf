-- =============================================================================
-- 010 - STATO DELLA MIGRAZIONE DELLE PASSWORD (SOLA LETTURA)
-- =============================================================================
-- Progetto : piattaforma-universita-ersaf
-- DB       : admin_entedb (MariaDB 10.11)
-- Scopo    : seguire l'avanzamento del rehash pigro. Nessuna DDL, nessuna
--            scrittura, nessuna cancellazione.
--
-- Da eseguire periodicamente dopo che il nuovo login e' in produzione.
--
--   mariadb -u <user> -p admin_entedb < db/diagnostica/010_stato_migrazione_password.sql
--
-- COME FUNZIONA LA MIGRAZIONE (per chi legge questo file tra sei mesi)
--   Nessuna operazione massiva tocca le righe esistenti. La conversione avviene
--   UNA RIGA ALLA VOLTA, e solo quando quell'utente fa login con successo:
--   il codice verifica la password legacy, scrive l'hash bcrypt su
--   utente_password_hash e ripulisce utente_password per quella singola riga.
--   Chi non fa mai login resta intatto e continua ad accedere come prima.
-- =============================================================================

SELECT '--- 1. Avanzamento complessivo ---' AS sezione;
SELECT
  `utente_password_algo`                     AS algoritmo,
  COUNT(*)                                   AS utenti,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM utenti), 1) AS percentuale
FROM utenti
GROUP BY `utente_password_algo`
ORDER BY utenti DESC;

SELECT '--- 2. Avanzamento sugli utenti ATTIVI (quelli che contano) ---' AS sezione;
-- Convenzione legacy: -1 = attivo, 0 = disattivo.
SELECT
  SUM(`utente_password_hash` IS NOT NULL) AS gia_su_bcrypt,
  SUM(`utente_password_hash` IS NULL)     AS ancora_legacy,
  COUNT(*)                                AS totale_attivi
FROM utenti
WHERE `utente_attivoSN` = -1;

SELECT '--- 3. Avanzamento per ruolo ---' AS sezione;
-- Utile per capire se gli attuatori (1,2,3,5) stanno convertendo piu' in
-- fretta dei sottoscrittori, come e' lecito attendersi.
SELECT
  COALESCE(r.`ruolo_codice`, '(senza cliente)')  AS ruolo,
  COUNT(*)                                       AS utenti,
  SUM(u.`utente_password_hash` IS NOT NULL)      AS su_bcrypt,
  SUM(u.`utente_password_hash` IS NULL)          AS ancora_legacy
FROM utenti u
LEFT JOIN clienti c ON c.`utente_id`  = u.`utente_id`
LEFT JOIN ruoli   r ON r.`ruolo_id`   = c.`cliente_ruolo`
WHERE u.`utente_attivoSN` = -1
GROUP BY ruolo
ORDER BY ancora_legacy DESC;

SELECT '--- 4. Righe incoerenti (non dovrebbero esistere) ---' AS sezione;
-- Un hash presente E la password in chiaro ancora valorizzata significa che il
-- login ha scritto l'hash ma non ha ripulito il legacy: e' un bug nel codice,
-- non un dato da sistemare a mano. Atteso: 0.
SELECT COUNT(*) AS hash_presente_ma_chiaro_non_ripulito
FROM utenti
WHERE `utente_password_hash` IS NOT NULL
  AND `utente_password` <> '';

SELECT '--- 5. Utenti legacy che non accedono da tempo ---' AS sezione;
-- Sono le righe che non convertiranno mai da sole. NON vanno cancellate:
-- servono solo a decidere, un domani, se contattarle o disattivarle.
SELECT
  CASE
    WHEN `utente_ultimo_login` IS NULL                          THEN 'mai loggato'
    WHEN `utente_ultimo_login` < CURDATE() - INTERVAL 2 YEAR    THEN 'oltre 2 anni'
    WHEN `utente_ultimo_login` < CURDATE() - INTERVAL 1 YEAR    THEN 'tra 1 e 2 anni'
    WHEN `utente_ultimo_login` < CURDATE() - INTERVAL 6 MONTH   THEN 'tra 6 e 12 mesi'
    ELSE 'ultimi 6 mesi'
  END        AS ultimo_accesso,
  COUNT(*)   AS utenti
FROM utenti
WHERE `utente_password_hash` IS NULL
  AND `utente_attivoSN` = -1
GROUP BY ultimo_accesso
ORDER BY utenti DESC;

SELECT '--- 6. Cambi password recenti ---' AS sezione;
SELECT
  `utente_password_changed_via` AS origine,
  COUNT(*)                      AS n,
  MAX(`utente_password_changed_at`) AS ultimo
FROM utenti
WHERE `utente_password_changed_at` IS NOT NULL
GROUP BY `utente_password_changed_via`
ORDER BY n DESC;

-- =============================================================================
-- E POI?
-- =============================================================================
-- Quando la query 2 mostra "ancora_legacy" vicino a zero, si potra' valutare
-- se rimuovere del tutto la colonna in chiaro. Quella decisione NON e' presa
-- qui e non esiste nessuno script che la esegua: va discussa quando i numeri
-- saranno noti, perche' comporta far ripartire da un recupero password gli
-- utenti rimasti indietro — e i ruoli non attuatori, per scelta, la mail di
-- reset non la ricevono.
--
-- Fino ad allora la colonna `utente_password` resta dov'e'. Ogni riga si
-- converte per conto suo al primo login riuscito.
