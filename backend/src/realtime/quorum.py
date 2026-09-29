"""ACK per connessione: il primo dispositivo non consuma la consegna degli altri."""

from src.realtime.dati import esegui, ora
from src.realtime.errori import richiedi


def riconcilia(db, uid, did):
    # Il chiamante serializza l'utente con eventi.blocca, anche in altri worker.
    esegui(
        db,
        """DELETE q FROM realtime_delivery_connessione q
        LEFT JOIN realtime_presenza p ON p.connessione=q.connessione AND p.scadenza>:now
        WHERE q.delivery_id=:id AND p.connessione IS NULL""",
        dict(id=did, now=ora()),
    )
    esegui(
        db,
        """INSERT IGNORE INTO realtime_delivery_connessione (delivery_id,connessione,prossimo_at)
        SELECT :id,connessione,:now FROM realtime_presenza WHERE utente_id=:u AND scadenza>:now""",
        dict(id=did, u=uid, now=ora()),
    )
    return completo(db, did)


def concludi(db, uid):
    # Conta anche una connessione appena arrivata, ancora priva di riga quorum.
    esegui(
        db,
        """UPDATE realtime_delivery d SET acknowledged_at=:now
        WHERE d.recipient_user_id=:u AND d.acknowledged_at IS NULL AND d.expires_at>:now
        AND EXISTS (SELECT 1 FROM realtime_presenza p JOIN realtime_delivery_connessione q
            ON q.connessione=p.connessione AND q.delivery_id=d.delivery_id
            WHERE p.utente_id=:u AND p.scadenza>:now AND q.confermata_at IS NOT NULL)
        AND NOT EXISTS (SELECT 1 FROM realtime_presenza p LEFT JOIN realtime_delivery_connessione q
            ON q.connessione=p.connessione AND q.delivery_id=d.delivery_id
            WHERE p.utente_id=:u AND p.scadenza>:now AND q.confermata_at IS NULL)
        LIMIT 64""",
        dict(u=uid, now=ora()),
    )


def completo(db, did):
    n, confermate = esegui(
        db,
        """SELECT COUNT(*),SUM(confermata_at IS NOT NULL)
        FROM realtime_delivery_connessione WHERE delivery_id=:id""",
        dict(id=did),
    ).one()
    return n > 0 and n == confermate


def dovuta(db, coordinate):
    did, conn = coordinate
    return bool(
        esegui(
            db,
            """SELECT 1 FROM realtime_delivery_connessione
        WHERE delivery_id=:id AND connessione=:c AND confermata_at IS NULL AND prossimo_at<=:now""",
            dict(id=did, c=conn, now=ora()),
        ).scalar()
    )


def tentativo(db, coordinate):
    did, conn = coordinate
    esegui(
        db,
        """UPDATE realtime_delivery_connessione SET inviata_at=:now,
        prossimo_at=TIMESTAMPADD(SECOND,LEAST(300,5*POW(2,LEAST(tentativi,6))),:now),tentativi=tentativi+1
        WHERE delivery_id=:id AND connessione=:c AND confermata_at IS NULL""",
        dict(id=did, c=conn, now=ora()),
    )


def conferma(db, coordinate):
    did, conn = coordinate
    r = esegui(
        db,
        """SELECT inviata_at FROM realtime_delivery_connessione
        WHERE delivery_id=:id AND connessione=:c FOR UPDATE""",
        dict(id=did, c=conn),
    ).first()
    richiedi(r is not None and r.inviata_at is not None, "delivery_not_received", 403)
    esegui(
        db,
        """UPDATE realtime_delivery_connessione SET confermata_at=COALESCE(confermata_at,:now)
        WHERE delivery_id=:id AND connessione=:c""",
        dict(id=did, c=conn, now=ora()),
    )
    return completo(db, did)
