"""Presenza con lease su MariaDB, condivisa tra tutti i worker."""

from datetime import timedelta

from src.chat_pratiche.configurazione import configurazione
from src.realtime.conversazioni import autorizza
from src.realtime.dati import esegui, iso, ora
from src.realtime.errori import ErroreRealtime, richiedi


def visibili(db, i):
    uid, cid = i.utente_id, i.cliente_id
    ids = set(
        esegui(
            db,
            """SELECT CASE WHEN utente_low_id=:u THEN utente_high_id ELSE utente_low_id END
        FROM realtime_person_contact_acl WHERE (utente_low_id=:u OR utente_high_id=:u) AND revoked_at IS NULL LIMIT 4097""",
            dict(u=uid),
        ).scalars()
    )
    pratiche = (
        esegui(
            db,
            """SELECT pratica_id FROM pratiche WHERE utente_id=:u OR utente_consulente_id=:u
        OR cliente_id=:c OR cliente_emittente_aderente_id=:c OR cliente_consulente_id=:c LIMIT 4097""",
            dict(u=uid, c=cid),
        )
        .scalars()
        .all()
    )
    ticket = (
        esegui(
            db,
            """SELECT ticket_id FROM {ticket}ticket t WHERE t.utente_id=:u OR EXISTS (
        SELECT 1 FROM {ticket}ticket_uditore ud WHERE ud.ticket_id=t.ticket_id AND ud.utente_id=:u
        AND ud.ticket_uditore_attivoSN=-1) LIMIT 4097""",
            dict(u=uid),
        )
        .scalars()
        .all()
    )
    richiedi(max(len(ids), len(pratiche), len(ticket)) <= 4096, "audience_too_large", 403)
    gruppi = [("PRACTICE", p) for p in pratiche] + [("TICKET", t) for t in ticket]
    for tipo, gruppo in gruppi:
        try:
            c = autorizza(db, uid, (tipo, gruppo, True if tipo == "TICKET" else None))
            ids.update(p.utente_id for p in c.persone)
        except ErroreRealtime as e:
            if e.status_code != 403:
                raise
        richiedi(len(ids) <= 4096, "audience_too_large", 403)
    return ids


def rinnova(db, i, connessione, sid):
    esegui(
        db,
        """INSERT INTO realtime_presenza VALUES (:conn,:sid,:u,:scad)
        ON DUPLICATE KEY UPDATE scadenza=VALUES(scadenza)""",
        dict(conn=connessione, sid=sid, u=i.utente_id, scad=ora() + timedelta(seconds=30)),
    )


def online(db, i):
    permessi = visibili(db, i)
    candidati = esegui(
        db,
        """SELECT DISTINCT p.utente_id FROM realtime_presenza p
        JOIN realtime_auth_session s ON s.session_id=p.session_id
        JOIN utenti u ON u.utente_id=p.utente_id AND u.utente_attivoSN=-1
        JOIN clienti c ON c.utente_id=u.utente_id AND c.cliente_id=s.cliente_id
        JOIN ruoli r ON r.ruolo_id=c.cliente_ruolo AND BINARY r.ruolo_codice=BINARY s.ruolo_codice
        WHERE p.scadenza>:now AND s.revoked_at IS NULL AND s.revocation_reason IS NULL
        AND s.refresh_expires_at>:now AND s.last_used_at>:idle
        AND COALESCE(c.azienda_id,0)=s.azienda_id
        AND (u.utente_password_changed_at IS NULL OR u.utente_password_changed_at<=s.created_at)
        AND (SELECT COUNT(*) FROM clienti uc WHERE uc.utente_id=u.utente_id)=1""",
        dict(now=ora(), idle=ora() - timedelta(seconds=configurazione().chat_universo_inattivita_secondi)),
    ).scalars()
    return set(candidati) & permessi


def lista(i, ids):
    import json

    return dict(
        channel="chat",
        payload=dict(
            type="LIST_USERS",
            **{"from": "Server", "to": str(i.utente_id)},
            content=json.dumps(sorted(map(str, ids))),
            timestamp=iso(ora()),
        ),
    )


def transizioni(precedenti, attuali):
    for u in sorted(precedenti ^ attuali):
        yield dict(
            channel="presence",
            payload=dict(userId=str(u), status="online" if u in attuali else "offline", timestamp=iso(ora())),
        )
