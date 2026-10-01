import json
import uuid

from src.chat_pratiche.configurazione import configurazione
from src.database import SessionLocal
from src.realtime import (
    comandi,
    consegne,
    eventi,
    presenza,
    quorum,
    scrittura,
    sessioni,
    token,
)
from src.realtime.conversazioni import autorizza
from src.realtime.dati import esegui, iso, ora
from src.realtime.errori import richiedi
from src.realtime.transazioni import ritenta


@ritenta
def avvia(accesso, conn=None):
    conn, claims = conn or str(uuid.uuid4()), token.decodifica(accesso)
    with sessioni.transazione(accesso, attivita=True) as (db, i):
        eventi.blocca(db, 0)
        eventi.blocca(db, i.utente_id)
        totale, utente, sessione = esegui(
            db,
            """SELECT COUNT(*),COALESCE(SUM(utente_id=:u),0),COALESCE(SUM(session_id=:sid),0)
            FROM realtime_presenza WHERE scadenza>UTC_TIMESTAMP(6)""",
            dict(u=i.utente_id, sid=claims["sid"]),
        ).one()
        c = configurazione()
        richiedi(
            totale < c.realtime_max_connections
            and utente < c.realtime_max_connections_per_user
            and sessione < c.realtime_max_connections_per_auth_session,
            "too_many_connections",
            429,
        )
        posizione = eventi.posizione(db, i.utente_id)
        presenza.rinnova(db, i, conn, claims["sid"])
    return i, conn, claims["sid"], posizione


@ritenta
def aggiorna(accesso, coordinate, dopo, aggiorna_presenza):
    conn, sid = coordinate
    with sessioni.transazione(accesso) as (db, i):
        # Quorum e ACK prendono prima questo lock e poi leggono la presenza.
        # Rinnovare la lease prima del lock invertiva l'ordine tra dispositivi.
        eventi.blocca(db, i.utente_id)
        online = None
        if aggiorna_presenza:
            presenza.rinnova(db, i, conn, sid)
            online = presenza.online(db, i)
        frames = configurazione().realtime_outbound_queue_frames
        lotto = min(24, (frames - min(8, frames // 2)) // 2)
        righe = eventi.ultimi(db, i.utente_id, dopo, lotto)
        nuovi = []
        for r in righe:
            d = json.loads(r.payload)
            if d["payload"].get("deliveryId"):
                continue
            if d["channel"] == "system" or consegne.consentita(db, i.utente_id, d):
                nuovi.append(d)
        return (
            nuovi + consegne.pendenti(db, i.utente_id, conn, lotto),
            (righe[-1].id if righe else dopo),
            online,
        )


@ritenta
def conferma(accesso, coordinate):
    conn, did = coordinate
    with sessioni.transazione(accesso) as (db, i):
        eventi.blocca(db, i.utente_id)
        proprio = esegui(
            db,
            "SELECT 1 FROM realtime_delivery WHERE delivery_id=:id AND recipient_user_id=:u",
            dict(id=did, u=i.utente_id),
        ).scalar()
        richiedi(proprio, "delivery_not_received", 403)
        quorum.riconcilia(db, i.utente_id, did)
        if quorum.conferma(db, (did, conn)):
            consegne.conferma(db, i.utente_id, did)


@ritenta
def prepara(accesso, coordinate):
    with sessioni.transazione(accesso) as (db, i):
        return consegne.prepara(db, i.utente_id, coordinate)


@ritenta
def chiudi(conn):
    with SessionLocal.begin() as db:
        esegui(db, "DELETE FROM realtime_presenza WHERE connessione=:c", dict(c=conn))


@ritenta
def elabora(accesso, envelope):
    richiedi(set(envelope) == {"channel", "payload"}, "invalid_envelope")
    richiedi(envelope["channel"] == "chat", "client_notification_forbidden", 403)
    with sessioni.transazione(accesso) as (db, i):
        d = comandi.valida(envelope["payload"], i.utente_id)
        if d["type"] == "LIST_USERS":
            return presenza.lista(i, presenza.online(db, i))
        if d["type"] == "CHAT":
            return dict(channel="chat", payload=scrittura.salva(db, i, d))
        c = autorizza(db, i.utente_id, comandi.destinazione(d))
        richiedi(
            c.tipo != "PRACTICE" or c.codice == d["codice"],
            "practice_reference_mismatch",
            403,
        )
        d["timestamp"] = iso(ora())
        for p in c.persone:
            if p.utente_id != i.utente_id:
                eventi.aggiungi(db, p.utente_id, dict(channel="chat", payload=d))
    return None
