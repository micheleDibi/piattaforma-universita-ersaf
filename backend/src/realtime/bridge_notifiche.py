"""Importazione incrementale delle notifiche prodotte ancora dal gestionale legacy."""

from datetime import datetime, timezone

from src.realtime import testi
from src.realtime.consegne import accoda
from src.realtime.dati import esegui, ora
from src.realtime.identita import carica
from src.realtime.lettura import istante
from src.realtime.notifiche_lettura import contesto_messaggio


def inizializza(db):
    esegui(
        db,
        """INSERT IGNORE INTO realtime_notification_bridge_state
        SELECT 1,COALESCE(MAX(notifica_id),0),COALESCE(MAX(notifica_id),0),1,:now FROM notifiche""",
        dict(now=ora()),
    )


def importa(db, audit=False):
    stato = esegui(
        db,
        "SELECT baseline_id,scan_floor_id FROM realtime_notification_bridge_state WHERE singleton_id=1 AND initialized=1 FOR UPDATE",
    ).one()
    minimo = stato.baseline_id if audit else stato.scan_floor_id
    righe = (
        esegui(
            db,
            """SELECT n.*,p.notifica_parameter_operation,p.notifica_parameter_id_ref,
        c.utente_id FROM notifiche n LEFT JOIN notifiche_parameters p ON p.notifica_parameter_id=n.notifica_parameter_id
        LEFT JOIN clienti c ON c.cliente_id=n.cliente_id LEFT JOIN realtime_notification_bridge b ON b.notification_id=n.notifica_id
        WHERE n.notifica_id>:id AND b.notification_id IS NULL ORDER BY n.notifica_id LIMIT 32""",
            dict(id=minimo),
        )
        .mappings()
        .all()
    )
    for r in righe:
        payload = prepara(db, r)
        esegui(
            db,
            "INSERT IGNORE INTO realtime_notification_bridge VALUES (:id,:now,:stato,:errore)",
            dict(
                id=r["notifica_id"],
                now=ora(),
                stato="DELIVERED" if payload else "REJECTED",
                errore=None if payload else "invalid_legacy_notification",
            ),
        )
        if payload:
            accoda(db, r["utente_id"], "notification", payload)
    if not audit and len(righe) < 32:
        massimo = esegui(db, "SELECT COALESCE(MAX(notifica_id),0) FROM notifiche").scalar()
        esegui(
            db,
            "UPDATE realtime_notification_bridge_state SET scan_floor_id=:f,updated_at=:now WHERE singleton_id=1",
            dict(f=max(stato.baseline_id, massimo - 1024), now=ora()),
        )
    return len(righe)


def prepara(db, r):
    from src.realtime.errori import ErroreRealtime

    try:
        destinatario = carica(db, r["utente_id"])
        if not r["notifica_created_by"] or r["notifica_created_by"] <= 0:
            return None
        valori = (r["notifica_title"], r["notifica_parameter_operation"], r["notifica_parameter_id_ref"])
        valori = tuple(testi.strutturato(v, limite) for v, limite in zip(valori, (255, 64, 128)))
        messaggio = testi.testo(r["notifica_body"], multilinea=True)
        data = istante(db, "NOTIFICATION", r["notifica_id"], r["notifica_created_at"])
        timestamp = (
            datetime.fromisoformat(data).timestamp()
            if data
            else ora().replace(tzinfo=timezone.utc).timestamp()
        )
        if timestamp <= 0:
            return None
        d = dict(
            notificationId=r["notifica_id"],
            fromUserId=r["notifica_created_by"],
            utenteCreatedBy=r["notifica_created_by"],
            utenteId=r["utente_id"],
            operation=valori[1],
            idRef=valori[2],
            title=valori[0],
            message=messaggio,
            timestamp=int(timestamp * 1000),
        )
        context = contesto_messaggio(db, destinatario, valori[1], valori[2])
        if context:
            d["messageContext"] = context
        return d
    except ErroreRealtime as e:
        if e.status_code in (400, 403, 404):
            return None
        raise
