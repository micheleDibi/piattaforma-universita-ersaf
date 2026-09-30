"""Stati letti/visti e snapshot immutabili: un retry non consuma nuovi eventi."""

import json
from datetime import timedelta

from src.realtime import eventi, snapshot_ids
from src.realtime.contratti import uuid_canonico
from src.realtime.dati import esegui, ora, query
from src.realtime.errori import richiedi
from src.realtime.notifiche_lettura import sorgente as notifiche


def visibili():
    return "WITH identity AS (SELECT :u AS uid,:c AS cid), visible AS (" + query("messaggi_visibili") + ") "


def sorgente(dominio):
    if dominio == "notification":
        return (
            notifiche()
            + """SELECT r.notifica_id AS id,CAST(r.notifica_id AS CHAR) AS gruppo,
            s.notification_id AS visto FROM ranked r LEFT JOIN realtime_notification_seen s
            ON s.notification_id=r.notifica_id AND s.utente_id=:u
            WHERE r.row_number_in_group=1 AND r.notifica_letta=0"""
        )
    return (
        visibili()
        + """SELECT v.item_id AS id,v.conversation_key AS gruppo,s.seen_at AS visto
        FROM visible v LEFT JOIN realtime_message_state s ON s.utente_id=:u AND s.item_id=v.item_id
        WHERE v.legacy_read=0 AND s.read_at IS NULL"""
    )


def stato(db, i, dominio):
    sql = (
        "SELECT COUNT(DISTINCT gruppo),COUNT(DISTINCT CASE WHEN visto IS NULL THEN gruppo END) FROM ("
        + sorgente(dominio)
        + ") contatori"
    )
    r = esegui(db, sql, dict(u=i.utente_id, c=i.cliente_id)).one()
    return dict(unreadCount=r[0], unseenCount=r[1])


def visti(db, i, dominio, ids):
    if dominio == "message":
        for inizio in range(0, len(ids), 500):
            visti_messaggi(db, i, ids[inizio : inizio + 500])
        return
    for mid in ids:
        if dominio == "notification":
            esegui(
                db,
                """INSERT IGNORE INTO realtime_notification_seen (utente_id,notification_id,seen_at)
                SELECT :u,notifica_id,:now FROM notifiche WHERE notifica_id=:id AND cliente_id=:c""",
                dict(u=i.utente_id, id=mid, c=i.cliente_id, now=ora()),
            )


def visti_messaggi(db, i, ids):
    p = {"m" + str(n): mid for n, mid in enumerate(ids)}
    vincolo = ",".join(":" + k for k in p)
    p.update(u=i.utente_id, c=i.cliente_id, now=ora())
    esegui(
        db,
        "INSERT INTO realtime_message_state (utente_id,item_id,seen_at,read_at) "
        + visibili()
        + "SELECT :u,item_id,:now,NULL FROM visible WHERE item_id IN ("
        + vincolo
        + ") "
        + "ON DUPLICATE KEY UPDATE seen_at=COALESCE(seen_at,VALUES(seen_at))",
        p,
    )


def snapshot(db, i, dominio, richiesta):
    richiedi(set(richiesta) == {"action", "snapshotId"})
    richiedi(richiesta["action"] in ("prepare", "seen"))
    sid = uuid_canonico(richiesta["snapshotId"])
    eventi.blocca(db, i.utente_id)
    tabella, campo = archivio(dominio)
    r = (
        esegui(db, f"SELECT * FROM {tabella} WHERE snapshot_id=:id FOR UPDATE", dict(id=sid))
        .mappings()
        .first()
    )
    if r is None:
        richiedi(richiesta["action"] == "prepare", dominio + "_snapshot_not_found", 404)
        prepara(db, i, dominio, sid)
    else:
        richiedi(
            r["utente_id"] == i.utente_id and r["cliente_id"] == i.cliente_id,
            dominio + "_snapshot_not_found",
            404,
        )
        richiedi(r["expires_at"] > ora(), dominio + "_snapshot_expired", 409)
        if richiesta["action"] == "seen" and r["applied_at"] is None:
            visti(db, i, dominio, snapshot_ids.decodifica(r[campo]))
            esegui(
                db,
                f"UPDATE {tabella} SET {campo}='[]',applied_at=:now WHERE snapshot_id=:id",
                dict(id=sid, now=ora()),
            )
            eventi.cambiato(db, i.utente_id, dominio)
    return dict(**stato(db, i, dominio), snapshotId=sid)


def archivio(dominio):
    richiedi(dominio in ("notification", "message"))
    return (
        "realtime_" + dominio + "_seen_snapshot",
        "notification_ids" if dominio == "notification" else "item_ids",
    )


def prepara(db, i, dominio, sid):
    tabella, campo = archivio(dominio)
    n = esegui(
        db,
        f"SELECT COUNT(*) FROM {tabella} WHERE utente_id=:u AND expires_at>:now",
        dict(u=i.utente_id, now=ora()),
    ).scalar()
    richiedi(n < 60, dominio + "_open_rate_limited", 429)
    ids = (
        esegui(
            db,
            "SELECT id FROM (" + sorgente(dominio) + ") elementi WHERE visto IS NULL ORDER BY id LIMIT 50001",
            dict(u=i.utente_id, c=i.cliente_id),
        )
        .scalars()
        .all()
    )
    richiedi(len(ids) <= 50000, dominio + "_snapshot_too_large", 413)
    esegui(
        db,
        f"INSERT INTO {tabella} (snapshot_id,utente_id,cliente_id,{campo},created_at,expires_at) VALUES (:id,:u,:c,:ids,:now,:exp)",
        dict(
            id=sid,
            u=i.utente_id,
            c=i.cliente_id,
            ids=json.dumps(ids),
            now=ora(),
            exp=ora() + timedelta(minutes=10),
        ),
    )


def leggi_notifica(db, i, nid):
    eventi.blocca(db, i.utente_id)
    trovato = esegui(
        db,
        "SELECT 1 FROM notifiche WHERE notifica_id=:id AND cliente_id=:c FOR UPDATE",
        dict(id=nid, c=i.cliente_id),
    ).scalar()
    richiedi(trovato, "notification_not_found", 404)
    esegui(db, "UPDATE notifiche SET notifica_letta=-1 WHERE notifica_id=:id", dict(id=nid))
    visti(db, i, "notification", [nid])
    eventi.cambiato(db, i.utente_id, "notification", dict(notificationId=nid, read=True))
    return dict(notificationId=nid, read=True)


def ids_letti(db, i, tipo, ids):
    from src.realtime.lettura import TIPI

    richiedi(
        tipo in TIPI and 1 <= len(ids) <= 100 and all(type(v) is int and 0 < v <= 2147483647 for v in ids),
        "invalid_message_ids",
    )
    parametri = dict(u=i.utente_id, c=i.cliente_id)
    parametri.update({"i" + str(n): mid * 4 + TIPI[tipo] for n, mid in enumerate(ids)})
    sql = (
        visibili()
        + "SELECT v.message_id FROM visible v JOIN realtime_message_state s ON s.item_id=v.item_id AND s.utente_id=:u WHERE s.read_at IS NOT NULL AND v.item_id IN ("
        + ",".join(":i" + str(n) for n in range(len(ids)))
        + ")"
    )
    return dict(readIds=list(esegui(db, sql, parametri).scalars()))


def leggi_messaggio(db, i, tipo, mid):
    from src.realtime.lettura import TIPI

    richiedi(tipo in TIPI and 0 < mid <= 2147483647, "invalid_message_id")
    eventi.blocca(db, i.utente_id)
    item = mid * 4 + TIPI[tipo]
    trovato = esegui(
        db,
        visibili() + "SELECT 1 FROM visible WHERE item_id=:id",
        dict(u=i.utente_id, c=i.cliente_id, id=item),
    ).scalar()
    richiedi(trovato, "message_not_found", 404)
    risultato = esegui(
        db,
        "INSERT INTO realtime_message_state (utente_id,item_id,seen_at,read_at) "
        + visibili()
        + """SELECT :u,item_id,:now,:now FROM visible WHERE item_id=:id ON DUPLICATE KEY UPDATE
        read_at=COALESCE(read_at,VALUES(read_at)),seen_at=COALESCE(seen_at,VALUES(seen_at))""",
        dict(u=i.utente_id, c=i.cliente_id, id=item, now=ora()),
    )
    richiedi(risultato.rowcount > 0, "message_not_found", 404)
    dati = dict(destinationType=tipo, messageId=mid, read=True)
    eventi.cambiato(db, i.utente_id, "message", dati)
    return dati
