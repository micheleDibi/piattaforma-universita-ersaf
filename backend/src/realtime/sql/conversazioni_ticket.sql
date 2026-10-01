SELECT t.ticket_id AS conversation_id,
       CONCAT('Ticket ', t.ticket_codice) AS conversation_label,
       latest.ticket_messaggio_is_public AS is_public,
       latest.ticket_messaggio_id AS last_message_id,
       latest.utente_id AS sender_user_id,
       latest.utente_denomazione AS sender_name,
       COALESCE(NULLIF(TRIM(latest.ticket_messagglio_testo), ''),
                'Messaggio senza testo') AS message_content,
       latest.ticket_messaggio_data_creazione AS message_at,
       t.ticket_codice AS resource_code, NULL AS peer_user_id
  FROM (
        SELECT m.ticket_id, m.ticket_messaggio_is_public,
               MAX(m.ticket_messaggio_id) AS last_id
          FROM {ticket}ticket_messaggio m
          JOIN {ticket}ticket visible ON visible.ticket_id = m.ticket_id
         WHERE ((m.ticket_messaggio_is_public = -1 AND
                (visible.utente_id = :u OR EXISTS (
                    SELECT 1 FROM {ticket}ticket_uditore ua
                     WHERE ua.ticket_id = visible.ticket_id
                       AND ua.utente_id = :u
                       AND ua.ticket_uditore_attivoSN = -1)))
            OR (m.ticket_messaggio_is_public = 0 AND EXISTS (
                    SELECT 1 FROM {ticket}ticket_uditore up
                    JOIN {entity}clienti c ON c.utente_id = up.utente_id
                    JOIN {entity}ruoli r ON r.ruolo_id = c.cliente_ruolo
                     WHERE up.ticket_id = visible.ticket_id
                       AND up.utente_id = :u
                       AND up.ticket_uditore_attivoSN = -1
                       AND r.ruolo_codice IN ('Aderente','Regionale','Provinciale',
                           'Consulente','Nazionale','Operatore')
                       AND (SELECT COUNT(*) FROM {entity}clienti uc
                             WHERE uc.utente_id = up.utente_id) = 1)))
           AND (:ricerca IS NULL OR LOWER(CONCAT('Ticket ',
                    visible.ticket_codice)) LIKE :ricerca ESCAPE '!')
         GROUP BY m.ticket_id, m.ticket_messaggio_is_public
        HAVING MAX(m.ticket_messaggio_id) < :prima
         ORDER BY last_id DESC LIMIT :n
  ) page
  JOIN {ticket}ticket t ON t.ticket_id = page.ticket_id
  JOIN {ticket}ticket_messaggio latest ON latest.ticket_messaggio_id = page.last_id
 ORDER BY latest.ticket_messaggio_id DESC
