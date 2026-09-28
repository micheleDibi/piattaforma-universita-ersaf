"""Mantiene la notifica legacy: il distributore Universo esistente la rileva."""
from sqlalchemy import text


def registra(db, contesto, messaggio, persone):
    autore = next(p for p in persone if p.utente_id == contesto.utente_id)
    titolo = " ".join(filter(None, (autore.cliente_nome, autore.cliente_cognome))).strip()
    for persona in persone:
        if persona.utente_id == contesto.utente_id:
            continue
        parametro = db.execute(text("""INSERT INTO notifiche_parameters
            (notifica_parameter_operation,notifica_parameter_id_ref,notifica_parameter_message)
            VALUES ('messaggioPratiche',:id,:cifrato)"""),
            dict(id=str(messaggio.messaggio_id), cifrato=messaggio.messaggio_testo)).lastrowid
        db.execute(text("""INSERT INTO notifiche
            (notifica_title,notifica_body,notifica_created_by,notifica_created_at,
             notifica_updated_by,notifica_updated_at,notifica_parameter_id,notifica_letta,cliente_id)
            VALUES (:titolo,:cifrato,:u,:ora,:u,:ora,:p,0,:c)"""),
            dict(titolo=titolo or f"Utente {contesto.utente_id}", cifrato=messaggio.messaggio_testo,
                 u=contesto.utente_id, ora=messaggio.messaggio_dataInvio, p=parametro, c=persona.cliente_id))
