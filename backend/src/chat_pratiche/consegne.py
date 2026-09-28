"""Coda transazionale condivisa, indipendente dal processo che espone la socket."""
import json
import uuid
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import text

from src.chat_pratiche.partecipanti import autorizza
from src.chat_pratiche.models import Messaggio


def accoda(db, contesto, dati):
    messaggio, comando, persone, ora = dati
    for persona in persone:
        identificativo = str(uuid.uuid4())
        payload = dict(type="CHAT", destinationType="PRACTICE", from_=str(contesto.utente_id),
            to=str(persona.utente_id), destinationId=str(contesto.pratica_id), codice=contesto.numero,
            clientMessageId=comando["clientMessageId"], messaggioId=str(messaggio.messaggio_id),
            content=messaggio.messaggio_testo, timestamp=ora.isoformat() + "Z", deliveryId=identificativo)
        payload["from"] = payload.pop("from_")
        db.execute(text("""INSERT INTO realtime_delivery
            (delivery_id,recipient_user_id,channel,payload_json,created_at,expires_at,next_attempt_at)
            VALUES (:id,:u,'chat',:payload,:ora,:scadenza,:ora)"""),
            dict(id=identificativo, u=persona.utente_id, payload=json.dumps(payload),
                 ora=ora, scadenza=ora+timedelta(days=30)))


def pendenti(db, utente_id):
    righe = db.execute(text("""SELECT delivery_id,payload_json FROM realtime_delivery
        WHERE recipient_user_id=:u AND channel='chat' AND acknowledged_at IS NULL
        AND expires_at>UTC_TIMESTAMP(6)
        AND JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.destinationType'))='PRACTICE'
        ORDER BY created_at,delivery_id LIMIT 128"""), dict(u=utente_id)).all()
    risultati = []
    for riga in righe:
        payload = json.loads(riga.payload_json)
        try:
            contesto, _ = autorizza(db, utente_id, int(payload["destinationId"]))
            if contesto.numero == payload["codice"]:
                risultati.append(dict(channel="chat", payload=payload))
            else:
                conferma(db, utente_id, riga.delivery_id)
        except HTTPException as errore:
            if errore.status_code not in (403, 404):
                raise
            # L'ACL è stata revocata: questa consegna non va più riproposta.
            conferma(db, utente_id, riga.delivery_id)
    return risultati


def conferma(db, utente_id, identificativo):
    db.execute(text("""UPDATE realtime_delivery SET acknowledged_at=UTC_TIMESTAMP(6)
        WHERE delivery_id=:id AND recipient_user_id=:u AND acknowledged_at IS NULL"""),
        dict(id=identificativo, u=utente_id))


def conferma_invio(db, contesto, identificativo, client_id):
    payload = db.scalar(text("""SELECT payload_json FROM realtime_delivery WHERE recipient_user_id=:u
        AND channel='chat' AND JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.destinationType'))='PRACTICE'
        AND JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.messaggioId'))=:m LIMIT 1"""),
        dict(u=contesto.utente_id, m=str(identificativo)))
    if payload:
        return dict(channel="chat", payload=json.loads(payload))
    # Un retry resta idempotente anche dopo la pulizia della coda a 30 giorni.
    messaggio = db.get(Messaggio, identificativo)
    ora = db.scalar(text("SELECT sent_at_utc FROM realtime_message_time WHERE destination_type='PRACTICE' AND message_id=:m"), dict(m=identificativo))
    return dict(channel="chat", payload={"type":"CHAT", "destinationType":"PRACTICE",
        "from":str(contesto.utente_id), "to":str(contesto.utente_id), "destinationId":str(contesto.pratica_id),
        "codice":contesto.numero, "clientMessageId":client_id, "messaggioId":str(identificativo),
        "content":messaggio.messaggio_testo, "timestamp":ora.isoformat()+"Z", "deliveryId":str(uuid.uuid4())})
