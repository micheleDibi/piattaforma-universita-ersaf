WITH ranked AS (
    SELECT n.notifica_id, n.notifica_title, n.notifica_body,
           n.notifica_created_by, n.notifica_created_at,
           n.notifica_letta, p.notifica_parameter_operation,
           p.notifica_parameter_id_ref, p.notifica_parameter_message,
           ROW_NUMBER() OVER (
               PARTITION BY CASE
                   WHEN personal.messaggio_id IS NOT NULL
                       THEN CONCAT('PERSON:', personal.messaggio_doc_id)
                   WHEN practice.messaggio_id IS NOT NULL
                       THEN CONCAT('PRACTICE:', practice.pratica_id)
                   WHEN ticket_message.ticket_messaggio_id IS NOT NULL
                       THEN CONCAT('TICKET:', ticket_message.ticket_id, ':',
                           ticket_message.ticket_messaggio_is_public)
                   ELSE CONCAT('NOTIFICATION:', n.notifica_id)
               END
               ORDER BY n.notifica_id DESC
           ) AS row_number_in_group
      FROM {entity}notifiche n
      JOIN {entity}notifiche_parameters p
        ON p.notifica_parameter_id = n.notifica_parameter_id
      LEFT JOIN {ticket}messaggio personal
        ON p.notifica_parameter_operation = 'messaggioPersonale'
       AND personal.messaggio_id = CASE
           WHEN p.notifica_parameter_id_ref REGEXP '^[1-9][0-9]{0,18}$'
           THEN CAST(p.notifica_parameter_id_ref AS UNSIGNED) END
      LEFT JOIN {entity}messaggi practice
        ON p.notifica_parameter_operation = 'messaggioPratiche'
       AND practice.messaggio_id = CASE
           WHEN p.notifica_parameter_id_ref REGEXP '^[1-9][0-9]{0,18}$'
           THEN CAST(p.notifica_parameter_id_ref AS UNSIGNED) END
      LEFT JOIN {ticket}ticket_messaggio ticket_message
        ON p.notifica_parameter_operation = 'messaggioTicket'
       AND ticket_message.ticket_messaggio_id = CASE
           WHEN p.notifica_parameter_id_ref REGEXP '^[1-9][0-9]{0,18}$'
           THEN CAST(p.notifica_parameter_id_ref AS UNSIGNED) END
     WHERE n.cliente_id = :c{filtro}
)
