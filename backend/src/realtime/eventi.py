"""Fan-out tra worker; ordine di commit serializzato per destinatario."""

import json
from datetime import timedelta

from src.realtime.dati import esegui, ora


def blocca(db, uid):
    esegui(
        db,
        """INSERT INTO realtime_flusso_utente VALUES (:u,0)
        ON DUPLICATE KEY UPDATE revisione=revisione+1""",
        {"u": uid},
    )


def aggiungi(db, uid, payload):
    blocca(db, uid)
    esegui(
        db,
        "INSERT INTO realtime_evento (utente_id,payload,scadenza) VALUES (:u,:p,:s)",
        dict(u=uid, p=json.dumps(payload), s=ora() + timedelta(minutes=2)),
    )


def ultimi(db, uid, dopo, limite=24):
    return esegui(
        db,
        """SELECT id,payload FROM realtime_evento WHERE utente_id=:u
        AND id>:id AND scadenza>:now ORDER BY id LIMIT :n""",
        dict(u=uid, id=dopo, now=ora(), n=limite),
    ).all()


def posizione(db, uid):
    return esegui(
        db, "SELECT COALESCE(MAX(id),0) FROM realtime_evento WHERE utente_id=:u", {"u": uid}
    ).scalar()


def cambiato(db, uid, dominio, riferimento=None):
    tipo = "notification_state_changed" if dominio == "notification" else "message_state_changed"
    payload = dict(type=tipo)
    if riferimento is not None:
        payload.update(riferimento)
    aggiungi(db, uid, dict(channel="system", payload=payload))
