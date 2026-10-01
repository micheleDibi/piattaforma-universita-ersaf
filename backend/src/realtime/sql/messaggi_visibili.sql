SELECT m.messaggio_id*4 AS item_id, m.messaggio_id AS message_id,
       'PERSON' AS kind, CONCAT('P:',m.messaggio_doc_id) AS conversation_key,
       (COALESCE(m.messaggio_lettoSN,0)<>0) AS legacy_read
  FROM {ticket}messaggio m
  CROSS JOIN identity p
  JOIN {entity}realtime_person_contact_acl acl
    ON acl.utente_low_id=LEAST(m.utente_mitt_id,m.utente_dest_id)
   AND acl.utente_high_id=GREATEST(m.utente_mitt_id,m.utente_dest_id)
   AND acl.revoked_at IS NULL
 WHERE m.utente_dest_id=p.uid AND m.utente_mitt_id<>p.uid
UNION ALL
SELECT m.messaggio_id*4+1, m.messaggio_id, 'PRACTICE',
       CONCAT('R:',m.pratica_id), 0
  FROM {entity}messaggi m
  JOIN {entity}pratiche v ON v.pratica_id=m.pratica_id
  CROSS JOIN identity p
  LEFT JOIN {entity}clienti sender ON sender.cliente_id=m.cliente_mittente_id
 WHERE COALESCE(sender.utente_id,0)<>p.uid
   AND (v.utente_id=p.uid OR v.utente_consulente_id=p.uid
        OR v.cliente_id=p.cid OR v.cliente_emittente_aderente_id=p.cid
        OR v.cliente_consulente_id=p.cid)
UNION ALL
SELECT m.ticket_messaggio_id*4+2, m.ticket_messaggio_id, 'TICKET',
       CONCAT('T:',m.ticket_id,':',m.ticket_messaggio_is_public), 0
  FROM {ticket}ticket_messaggio m
  JOIN {ticket}ticket v ON v.ticket_id=m.ticket_id
  CROSS JOIN identity p
 WHERE m.utente_id<>p.uid AND
   ((m.ticket_messaggio_is_public=-1 AND (v.utente_id=p.uid OR EXISTS (
       SELECT 1 FROM {ticket}ticket_uditore u
        WHERE u.ticket_id=v.ticket_id AND u.utente_id=p.uid
          AND u.ticket_uditore_attivoSN=-1)))
    OR (m.ticket_messaggio_is_public=0 AND EXISTS (
       SELECT 1 FROM {ticket}ticket_uditore u
       JOIN {entity}clienti c ON c.utente_id=u.utente_id
       JOIN {entity}ruoli r ON r.ruolo_id=c.cliente_ruolo
        WHERE u.ticket_id=v.ticket_id AND u.utente_id=p.uid
          AND u.ticket_uditore_attivoSN=-1
          AND r.ruolo_codice IN ('Aderente','Regionale','Provinciale',
              'Consulente','Nazionale','Operatore')
          AND (SELECT COUNT(*) FROM {entity}clienti uc WHERE uc.utente_id=p.uid)=1)))
