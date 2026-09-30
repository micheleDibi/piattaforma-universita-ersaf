"""Consegna persistente e recupero dopo disconnessione, senza dipendere da Java."""

import json
import uuid
from datetime import timedelta

from fastapi import HTTPException
from src.realtime import eventi, quorum
from src.realtime.conversazioni import autorizza
from src.realtime.dati import esegui, ora
from src.realtime.identita import carica


def accoda(db, uid, canale, payload):
    adesso, did = ora(), str(uuid.uuid4())
    payload = dict(payload, deliveryId=did)
    esegui(
        db,
        """INSERT INTO realtime_delivery
        (delivery_id,recipient_user_id,channel,payload_json,created_at,expires_at,next_attempt_at)
        VALUES (:id,:u,:c,:p,:now,:exp,:now)""",
        dict(
            id=did,
            u=uid,
            c=canale,
            p=json.dumps(payload),
            now=adesso,
            exp=adesso + timedelta(days=30),
        ),
    )
    eventi.aggiungi(db, uid, dict(channel=canale, payload=payload))
    return payload


def consentita(db, uid, envelope):
    try:
        carica(db, uid)
        p = envelope["payload"]
        if envelope["channel"] == "notification":
            return (
                esegui(
                    db,
                    """SELECT 1 FROM notifiche n JOIN clienti c ON c.cliente_id=n.cliente_id
                WHERE n.notifica_id=:id AND c.utente_id=:u""",
                    dict(id=p["notificationId"], u=uid),
                ).scalar()
                == 1
            )
        tipo = p["destinationType"]
        risorsa = (
            (p["to"] if int(p["from"]) == uid else p["from"]) if tipo == "PERSON" else p["destinationId"]
        )
        c = autorizza(db, uid, (tipo, risorsa, p.get("isPublic")))
        return tipo != "PRACTICE" or c.codice == p["codice"]
    except HTTPException as e:
        if e.status_code not in (401, 403, 404):
            raise
        return False


def pendenti(db, uid, connessione=None, limite=24):
    eventi.blocca(db, uid)
    quorum.concludi(db, uid)
    righe = esegui(
        db,
        """SELECT d.delivery_id,d.channel,d.payload_json FROM realtime_delivery d
        LEFT JOIN realtime_delivery_connessione q ON q.delivery_id=d.delivery_id AND q.connessione=:c
        WHERE recipient_user_id=:u AND acknowledged_at IS NULL AND expires_at>:now
        AND q.confermata_at IS NULL AND (q.prossimo_at IS NULL OR q.prossimo_at<=:now)
        ORDER BY created_at,delivery_id LIMIT :n""",
        dict(u=uid, c=connessione, now=ora(), n=limite),
    ).all()
    risultato = []
    for r in righe:
        envelope = dict(channel=r.channel, payload=json.loads(r.payload_json))
        if consentita(db, uid, envelope):
            risultato.append(envelope)
        else:
            conferma(db, uid, r.delivery_id)
    return risultato


def tentativo(db, uid, did):
    esegui(
        db,
        """UPDATE realtime_delivery SET last_attempt_at=:now,
        next_attempt_at=TIMESTAMPADD(SECOND,LEAST(300,5*POW(2,LEAST(attempt_count,6))),:now),
        attempt_count=attempt_count+1
        WHERE delivery_id=:id AND recipient_user_id=:u""",
        dict(u=uid, id=did, now=ora()),
    )


def conferma(db, uid, did):
    esegui(
        db,
        """UPDATE realtime_delivery SET acknowledged_at=COALESCE(acknowledged_at,:now)
        WHERE delivery_id=:id AND recipient_user_id=:u""",
        dict(u=uid, id=did, now=ora()),
    )


def prepara(db, uid, coordinate):
    conn, did = coordinate
    eventi.blocca(db, uid)
    r = esegui(
        db,
        """SELECT channel,payload_json FROM realtime_delivery WHERE delivery_id=:id
        AND recipient_user_id=:u AND acknowledged_at IS NULL AND expires_at>:now FOR UPDATE""",
        dict(id=did, u=uid, now=ora()),
    ).first()
    if r is None:
        return False
    if not consentita(db, uid, dict(channel=r.channel, payload=json.loads(r.payload_json))):
        conferma(db, uid, did)
        return False
    if quorum.riconcilia(db, uid, did):
        conferma(db, uid, did)
        return False
    if not quorum.dovuta(db, (did, conn)):
        return False
    quorum.tentativo(db, (did, conn))
    tentativo(db, uid, did)
    return True
