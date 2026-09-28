"""Preflight: abilitazione esplicita e archivio capace di conservare il ciphertext."""
from urllib.parse import urlsplit

from sqlalchemy import text

from src.database import SessionLocal
from src.chat_pratiche.configurazione import configurazione, chiavi, leggi_segreto


def verifica():
    config = configurazione()
    if not config.chat_abilitata:
        return
    chiavi()
    if not 300 <= config.chat_universo_inattivita_secondi <= 604800:
        raise ValueError("Scadenza della sessione Universo fuori limite.")
    for origine in filter(None, map(str.strip, config.chat_universo_origini.split(","))):
        uri = urlsplit(origine)
        if uri.scheme != "https" or not uri.hostname or uri.username or uri.path or uri.query or uri.fragment or "*" in origine:
            raise ValueError("Le origini Universo devono essere origini HTTPS esplicite.")
    if config.chat_universo_jwt_file:
        leggi_segreto(config.chat_universo_jwt_file, massimo=128)
    with SessionLocal() as db:
        verifica_schema(db)


def verifica_schema(db):
    tipo = db.scalar(text("""SELECT DATA_TYPE FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='messaggi' AND COLUMN_NAME='messaggio_testo'"""))
    if tipo not in {"text", "mediumtext", "longtext"}:
        raise ValueError("Archivio chat assente o colonna testo insufficiente: verificare le migrazioni Universo.")
    for tabella, colonna in (("notifiche", "notifica_body"), ("notifiche_parameters", "notifica_parameter_message")):
        capienza = db.scalar(text("""SELECT CHARACTER_MAXIMUM_LENGTH FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND COLUMN_NAME=:c"""), dict(t=tabella,c=colonna))
        if capienza is None or capienza < 1403:
            raise ValueError("Archivio notifiche assente o colonna testo insufficiente.")
    for query in (
        "SELECT utente_id,canonical_context,key_version,epoch_hour FROM realtime_message_key_grant LIMIT 0",
        "SELECT destination_type,message_id,sent_at_utc FROM realtime_message_time LIMIT 0",
        "SELECT utente_id,pratica_id,client_id,impronta,messaggio_id FROM chat_pratica_comando LIMIT 0",
        "SELECT utente_id,finestra,tentativi FROM chat_pratica_limite LIMIT 0",
        "SELECT delivery_id,recipient_user_id,payload_json,acknowledged_at FROM realtime_delivery LIMIT 0",
        "SELECT utente_id,item_id,read_at FROM realtime_message_state LIMIT 0",
    ):
        db.execute(text(query))
    if configurazione().chat_universo_jwt_file:
        db.execute(text("SELECT session_id,utente_id,cliente_id,azienda_id,ruolo_codice,device_id,refresh_expires_at,last_used_at,revoked_at,revocation_reason FROM realtime_auth_session LIMIT 0"))
