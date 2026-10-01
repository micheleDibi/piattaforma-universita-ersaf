SELECT m.ticket_messaggio_id AS message_id,
       m.utente_id AS sender_user_id,
       m.utente_denomazione AS sender_name,
       NULL AS recipient_user_id,
       COALESCE(NULLIF(TRIM(m.ticket_messagglio_testo), ''),
                'Messaggio senza testo') AS message_content,
       m.ticket_messaggio_data_creazione AS message_at,
       NULL AS message_read
  FROM {ticket}ticket_messaggio m
 WHERE m.ticket_id = :id
   AND m.ticket_messaggio_is_public = :pubblico
   AND m.ticket_messaggio_id < :prima
 ORDER BY m.ticket_messaggio_id DESC LIMIT :n
