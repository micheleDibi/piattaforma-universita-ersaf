SELECT m.messaggio_id AS message_id,
       m.utente_mitt_id AS sender_user_id,
       m.utente_mitt_denominazione AS sender_name,
       m.utente_dest_id AS recipient_user_id,
       COALESCE(NULLIF(TRIM(m.messaggio_testo), ''),
                'Messaggio senza testo') AS message_content,
       m.messaggio_data_creazione AS message_at,
       m.messaggio_lettoSN AS message_read
  FROM {ticket}messaggio m
 WHERE m.messaggio_doc_id = :id
   AND (m.utente_mitt_id = :u OR m.utente_dest_id = :u)
   AND m.messaggio_id < :prima
 ORDER BY m.messaggio_id DESC LIMIT :n
