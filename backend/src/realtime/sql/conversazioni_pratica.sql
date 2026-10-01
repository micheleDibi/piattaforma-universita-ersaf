SELECT p.pratica_id AS conversation_id,
       CONCAT('Pratica ', COALESCE(p.pratica_numero, p.pratica_id)) AS conversation_label,
       NULL AS is_public, latest.messaggio_id AS last_message_id,
       COALESCE(sender.utente_id, 0) AS sender_user_id,
       COALESCE(NULLIF(TRIM(CONCAT_WS(' ', sender.cliente_nome,
                    sender.cliente_cognome)), ''),
                'Utente non disponibile') AS sender_name,
       COALESCE(NULLIF(TRIM(latest.messaggio_testo), ''),
                'Messaggio senza testo') AS message_content,
       latest.messaggio_dataInvio AS message_at,
       p.pratica_numero AS resource_code, NULL AS peer_user_id
  FROM (
        SELECT m.pratica_id, MAX(m.messaggio_id) AS last_id
          FROM {entity}messaggi m
          JOIN {entity}pratiche visible ON visible.pratica_id = m.pratica_id
         WHERE (visible.utente_id = :u OR visible.utente_consulente_id = :u
            OR visible.cliente_id = :c
            OR visible.cliente_emittente_aderente_id = :c
            OR visible.cliente_consulente_id = :c)
           AND (:ricerca IS NULL OR LOWER(CONCAT('Pratica ',
                    COALESCE(visible.pratica_numero, visible.pratica_id)))
                    LIKE :ricerca ESCAPE '!')
         GROUP BY m.pratica_id
        HAVING MAX(m.messaggio_id) < :prima
         ORDER BY last_id DESC LIMIT :n
  ) page
  JOIN {entity}pratiche p ON p.pratica_id = page.pratica_id
  JOIN {entity}messaggi latest ON latest.messaggio_id = page.last_id
  LEFT JOIN {entity}clienti sender
    ON sender.cliente_id = latest.cliente_mittente_id
 ORDER BY latest.messaggio_id DESC
