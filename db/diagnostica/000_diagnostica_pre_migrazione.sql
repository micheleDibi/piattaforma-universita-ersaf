-- =============================================================================
-- 000 - DIAGNOSTICA PRE-MIGRAZIONE (SOLA LETTURA)
-- =============================================================================
-- Progetto : piattaforma-universita-ersaf
-- DB       : admin_entedb (MariaDB 10.11, InnoDB, utf8mb4_unicode_ci)
-- Scopo    : fotografare lo stato dei dati PRIMA di applicare le migrazioni
--            001..006. Nessuna DDL, nessuna scrittura.
--
-- Esecuzione:
--   mariadb -u <user> -p admin_entedb < db/diagnostica/000_diagnostica_pre_migrazione.sql
--
-- I valori attesi sono quelli rilevati sul dump del 2026-09-03; se il tuo
-- risultato diverge in modo sensibile, fermati e rivedi le migrazioni.
-- =============================================================================

SELECT '--- 1. Volumi di base ---' AS sezione;
SELECT
  (SELECT COUNT(*) FROM utenti)  AS utenti_totali,        -- atteso ~4771
  (SELECT COUNT(*) FROM clienti) AS clienti_totali,       -- atteso ~3906
  (SELECT COUNT(*) FROM ruoli)   AS ruoli_totali;         -- atteso 7

SELECT '--- 2. Password: quante sono gia hashate? ---' AS sezione;
-- Atteso: plaintext = 100%. Se compaiono righe bcrypt qualcuno ha gia migrato:
-- FERMATI e allinea la migrazione 001.
SELECT
  CASE
    WHEN utente_password LIKE '$2a$%'
      OR utente_password LIKE '$2b$%'
      OR utente_password LIKE '$2y$%' THEN 'bcrypt'
    WHEN utente_password LIKE '$argon2%'            THEN 'argon2'
    WHEN CHAR_LENGTH(utente_password) = 32
      AND utente_password REGEXP '^[0-9a-fA-F]{32}$' THEN 'md5_probabile'
    WHEN CHAR_LENGTH(utente_password) = 40
      AND utente_password REGEXP '^[0-9a-fA-F]{40}$' THEN 'sha1_probabile'
    WHEN CHAR_LENGTH(utente_password) = 64
      AND utente_password REGEXP '^[0-9a-fA-F]{64}$' THEN 'sha256_probabile'
    ELSE 'PLAINTEXT'
  END AS formato,
  COUNT(*) AS n,
  MIN(CHAR_LENGTH(utente_password)) AS len_min,
  MAX(CHAR_LENGTH(utente_password)) AS len_max
FROM utenti
GROUP BY formato
ORDER BY n DESC;

SELECT '--- 3. Password oltre il limite bcrypt di 72 byte ---' AS sezione;
-- bcrypt TRONCA silenziosamente oltre 72 byte. Atteso: 0 righe.
SELECT COUNT(*) AS password_oltre_72_byte
FROM utenti
WHERE LENGTH(utente_password) > 72;

SELECT '--- 4. Username duplicati (blocca la UNIQUE su utente_username) ---' AS sezione;
-- Atteso: 6 gruppi. Il modello SQLAlchemy dichiara unique=True ma il DB NON ha
-- il vincolo: vanno bonificati prima di poterlo aggiungere (migrazione 005).
SELECT LOWER(utente_username) AS username_norm,
       COUNT(*)               AS occorrenze,
       GROUP_CONCAT(utente_id ORDER BY utente_id) AS utente_ids
FROM utenti
GROUP BY LOWER(utente_username)
HAVING COUNT(*) > 1
ORDER BY occorrenze DESC, username_norm;

SELECT '--- 5. Utenti senza riga clienti (=> nessuna email raggiungibile) ---' AS sezione;
-- Atteso: ~869. Sono anche le righe che fanno esplodere /auth/login con 500
-- (user.clienti.ruolo.ruolo_codice su clienti = None).
SELECT COUNT(*) AS utenti_orfani
FROM utenti u
LEFT JOIN clienti c ON c.utente_id = u.utente_id
WHERE c.cliente_id IS NULL;

SELECT '--- 6. Utenti con PIU di una riga clienti ---' AS sezione;
-- La relazione SQLAlchemy e' uselist=False: con >1 riga il comportamento
-- e' non deterministico. Atteso: 4 gruppi.
SELECT utente_id, COUNT(*) AS n_clienti,
       GROUP_CONCAT(cliente_id ORDER BY cliente_id) AS cliente_ids
FROM clienti
GROUP BY utente_id
HAVING COUNT(*) > 1
ORDER BY n_clienti DESC;

SELECT '--- 7. Qualita delle email (chiave del recupero password) ---' AS sezione;
SELECT
  SUM(cliente_email IS NULL OR TRIM(cliente_email) = '')            AS email_vuote,      -- atteso ~43
  SUM(cliente_email NOT LIKE '%@%.%' AND TRIM(cliente_email) <> '') AS email_malformate, -- atteso ~10
  COUNT(DISTINCT LOWER(TRIM(cliente_email)))                        AS email_distinte
FROM clienti;

SELECT '--- 8. Email condivise da piu clienti ---' AS sezione;
-- Atteso: ~40 valori su ~105 clienti (max 11 clienti sulla stessa email).
-- Su questi indirizzi il recupero password NON deve inviare nulla.
SELECT LOWER(TRIM(cliente_email)) AS email_norm,
       COUNT(*)                   AS n_clienti,
       GROUP_CONCAT(cliente_id ORDER BY cliente_id) AS cliente_ids
FROM clienti
WHERE cliente_email LIKE '%@%.%'
GROUP BY LOWER(TRIM(cliente_email))
HAVING COUNT(*) > 1
ORDER BY n_clienti DESC;

SELECT '--- 9. Perimetro ATTUATORI (ruoli 1,2,3,5) ---' AS sezione;
-- Definizione allineata al filtro solo_attuatori gia presente in
-- backend/src/clienti/routers.py: Aderente, Regionale, Provinciale, Nazionale.
SELECT r.ruolo_id, r.ruolo_codice,
       COUNT(*)                                        AS n_clienti,
       SUM(c.cliente_email LIKE '%@%.%')               AS con_email_valida,
       SUM(u.`utente_attivoSN` = -1)                   AS utenti_attivi
FROM clienti c
JOIN ruoli   r ON r.ruolo_id  = c.cliente_ruolo
JOIN utenti  u ON u.utente_id = c.utente_id
WHERE c.cliente_ruolo IN (1,2,3,5)
GROUP BY r.ruolo_id, r.ruolo_codice
ORDER BY r.ruolo_id;

SELECT '--- 10. Attuatori NON contattabili (email assente/malformata) ---' AS sezione;
-- Atteso: 1. Vanno sistemati a mano: per loro il recupero password non
-- funzionera' mai.
SELECT c.cliente_id, c.utente_id, r.ruolo_codice, c.cliente_email
FROM clienti c
JOIN ruoli r ON r.ruolo_id = c.cliente_ruolo
WHERE c.cliente_ruolo IN (1,2,3,5)
  AND (c.cliente_email IS NULL OR c.cliente_email NOT LIKE '%@%.%')
ORDER BY c.cliente_id;

SELECT '--- 11. Attuatori la cui email e condivisa con un altro cliente ---' AS sezione;
-- Atteso: ~20. Su queste email la richiesta di reset e' AMBIGUA: non si invia,
-- si logga e si gestisce a mano.
SELECT LOWER(TRIM(c.cliente_email)) AS email_norm,
       COUNT(*)                     AS n_clienti,
       SUM(c.cliente_ruolo IN (1,2,3,5)) AS di_cui_attuatori,
       GROUP_CONCAT(CONCAT(c.cliente_id, ':', c.cliente_ruolo) ORDER BY c.cliente_id) AS cliente_id_ruolo
FROM clienti c
WHERE c.cliente_email LIKE '%@%.%'
  AND LOWER(TRIM(c.cliente_email)) IN (
        SELECT LOWER(TRIM(cliente_email))
        FROM clienti
        WHERE cliente_ruolo IN (1,2,3,5) AND cliente_email LIKE '%@%.%'
      )
GROUP BY LOWER(TRIM(c.cliente_email))
HAVING COUNT(*) > 1
ORDER BY n_clienti DESC;

SELECT '--- 12. Stato attivazione utenti ---' AS sezione;
-- Convenzione Instant Developer: -1 = TRUE (attivo), 0 = FALSE (disattivo).
-- Atteso: -1 => ~4750, 0 => ~21.
SELECT `utente_attivoSN`, COUNT(*) AS n FROM utenti GROUP BY `utente_attivoSN` ORDER BY n DESC;

SELECT '--- 13. Indici gia presenti sulle tabelle coinvolte ---' AS sezione;
-- Atteso: clienti ha SOLO la PRIMARY KEY (nessun indice su cliente_email,
-- utente_id, cliente_ruolo) -> la lookup del recupero password sarebbe un
-- full scan. La migrazione 005 li aggiunge.
SELECT TABLE_NAME, INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS colonne, NON_UNIQUE
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN ('utenti','clienti','ruoli','messaggi_email','utente_session')
GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE
ORDER BY TABLE_NAME, INDEX_NAME;

SELECT '--- 14. La tabella legacy utente_session e ancora viva? ---' AS sezione;
-- Se qui trovi righe recenti, la vecchia piattaforma Instant Developer la sta
-- ancora usando: NON riusarla. La migrazione 004 crea auth_sessioni separata.
SELECT COUNT(*) AS righe,
       MAX(utente_session_created_at) AS ultima_creazione,
       SUM(utente_session_expired = -1) AS scadute
FROM utente_session;

SELECT '--- 15. Codici template email gia usati ---' AS sezione;
-- La migrazione 006 aggiunge password_reset_richiesta / password_reset_eseguito.
SELECT messaggio_email_id, messaggio_email_codice, messaggio_email_oggetto
FROM messaggi_email
ORDER BY messaggio_email_id;
