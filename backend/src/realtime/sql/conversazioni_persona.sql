SELECT latest.messaggio_doc_id AS conversation_id,
       CASE WHEN latest.utente_mitt_id = :u
            THEN latest.utente_dest_denominazione
            ELSE latest.utente_mitt_denominazione END AS conversation_label,
       NULL AS is_public, latest.messaggio_id AS last_message_id,
       latest.utente_mitt_id AS sender_user_id,
       latest.utente_mitt_denominazione AS sender_name,
       COALESCE(NULLIF(TRIM(latest.messaggio_testo), ''),
                'Messaggio senza testo') AS message_content,
       latest.messaggio_data_creazione AS message_at,
       NULL AS resource_code,
       CASE WHEN latest.utente_mitt_id = :u
            THEN latest.utente_dest_id ELSE latest.utente_mitt_id END AS peer_user_id
  FROM (
        SELECT m.messaggio_doc_id, MAX(m.messaggio_id) AS last_id
          FROM {ticket}messaggio m
          JOIN {entity}realtime_person_contact_acl acl
            ON acl.utente_low_id = LEAST(m.utente_mitt_id, m.utente_dest_id)
           AND acl.utente_high_id = GREATEST(m.utente_mitt_id, m.utente_dest_id)
           AND acl.revoked_at IS NULL
         WHERE (m.utente_mitt_id = :u OR m.utente_dest_id = :u)
           AND m.utente_mitt_id <> m.utente_dest_id
           AND EXISTS (SELECT 1 FROM {entity}utenti peer
               JOIN {entity}clienti pc ON pc.utente_id=peer.utente_id
               JOIN {entity}ruoli pr ON pr.ruolo_id=pc.cliente_ruolo
               WHERE peer.utente_id=CASE WHEN m.utente_mitt_id=:u THEN m.utente_dest_id ELSE m.utente_mitt_id END
               AND peer.utente_attivoSN=-1
               AND (SELECT COUNT(*) FROM {entity}clienti uc WHERE uc.utente_id=peer.utente_id)=1)
           AND (:ricerca IS NULL OR LOWER(CASE WHEN m.utente_mitt_id = :u
                    THEN m.utente_dest_denominazione
                    ELSE m.utente_mitt_denominazione END)
                    LIKE :ricerca ESCAPE '!')
         GROUP BY m.messaggio_doc_id
        HAVING MAX(m.messaggio_id) < :prima
         ORDER BY last_id DESC LIMIT :n
  ) page
  JOIN {ticket}messaggio latest ON latest.messaggio_id = page.last_id
 ORDER BY latest.messaggio_id DESC
