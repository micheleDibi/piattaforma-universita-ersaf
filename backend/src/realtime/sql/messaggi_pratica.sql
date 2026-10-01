SELECT m.messaggio_id AS message_id,
       COALESCE(sender.utente_id, 0) AS sender_user_id,
       COALESCE(NULLIF(TRIM(CONCAT_WS(' ', sender.cliente_nome,
                     sender.cliente_cognome)), ''),
                'Utente non disponibile') AS sender_name,
       recipient.utente_id AS recipient_user_id,
       COALESCE(NULLIF(TRIM(m.messaggio_testo), ''),
                'Messaggio senza testo') AS message_content,
       m.messaggio_dataInvio AS message_at,
       NULL AS message_read
  FROM {entity}messaggi m
  LEFT JOIN {entity}clienti sender
    ON sender.cliente_id = m.cliente_mittente_id
  LEFT JOIN {entity}clienti recipient
    ON recipient.cliente_id = m.cliente_destinatario_id
 WHERE m.pratica_id = :id AND m.messaggio_id < :prima
 ORDER BY m.messaggio_id DESC LIMIT :n
