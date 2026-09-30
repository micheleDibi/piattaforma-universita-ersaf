"""Pagine di conversazioni e messaggi con ACL e cursori legati all'identita."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src.realtime import paginazione
from src.realtime.conversazioni import da_storico
from src.realtime.dati import esegui, iso, query
from src.realtime.errori import ErroreRealtime, richiedi

NOMI = dict(PERSON="persona", PRACTICE="pratica", TICKET="ticket")
TIPI = dict(PERSON=0, PRACTICE=1, TICKET=2)


def tipo(richiesta):
    valore = richiesta.get("destinationType")
    richiedi(valore in NOMI, "invalid_destinationType")
    return valore


def riferimento(richiesta):
    t, id = tipo(richiesta), richiesta.get("conversationId", "")
    import re

    modello = r"[A-Za-z0-9][A-Za-z0-9._:-]{0,59}" if t == "PERSON" else r"[1-9][0-9]{0,18}"
    richiedi(re.fullmatch(modello, id), "invalid_conversationId")
    pubblico = richiesta.get("isPublic")
    richiedi(pubblico in ("true", "false") if t == "TICKET" else pubblico is None, "invalid_isPublic")
    return t, id, (pubblico == "true") if t == "TICKET" else None


def istante(db, tipo, mid, data):
    esatto = esegui(
        db,
        "SELECT sent_at_utc FROM realtime_message_time WHERE destination_type=:t AND message_id=:m",
        dict(t=tipo, m=mid),
    ).scalar()
    if esatto:
        return iso(esatto)
    if not data:
        return None
    try:
        locale = data if isinstance(data, datetime) else datetime.fromisoformat(data)
        if locale.tzinfo:
            return iso(locale.astimezone(timezone.utc).replace(tzinfo=None))
        zona = ZoneInfo("Europe/Rome")
        # Stessa scelta di Java LocalDateTime.atZone: primo offset nell'ora
        # autunnale ripetuta, traslazione in avanti nel salto primaverile.
        return iso(locale.replace(tzinfo=zona, fold=0).astimezone(timezone.utc).replace(tzinfo=None))
    except (ValueError, TypeError):
        raise ErroreRealtime("invalid_legacy_timestamp", 503) from None


def letto(db, uid, tipo, mid):
    return bool(
        esegui(
            db,
            "SELECT 1 FROM realtime_message_state WHERE utente_id=:u AND item_id=:id AND read_at IS NOT NULL",
            dict(u=uid, id=mid * 4 + TIPI[tipo]),
        ).scalar()
    )


def messaggi(db, identita, richiesta):
    t, id, pubblico = riferimento(richiesta)
    c = da_storico(db, identita.utente_id, (t, id, pubblico))
    ambito = f"messages:{t}:{id}" + (f":{str(pubblico).lower()}" if pubblico is not None else "")
    p = paginazione.parametri(identita, ambito, richiesta)
    p.update(id=id, pubblico=-1 if pubblico else 0)
    righe = esegui(db, query("messaggi_" + NOMI[t]), p).mappings().all()
    elementi = [messaggio(db, identita, t, r) for r in righe]
    return dict(
        **paginazione.pagina(identita, (ambito, p["n"] - 1), elementi, "messageId"),
        cryptoContext=c.crypto(identita.utente_id),
    )


def messaggio(db, i, t, r):
    mid, mittente = r["message_id"], r["sender_user_id"]
    stato = (
        True
        if mittente == i.utente_id or letto(db, i.utente_id, t, mid)
        else (bool(r["message_read"]) if r["message_read"] is not None else None)
    )
    return dict(
        messageId=mid,
        senderUserId=mittente,
        senderName=r["sender_name"] or "Utente non disponibile",
        recipientUserId=r["recipient_user_id"],
        content=r["message_content"],
        createdAt=istante(db, t, mid, r["message_at"]),
        read=stato,
    )


def conversazioni(db, identita, richiesta):
    t, ricerca = tipo(richiesta), richiesta.get("q", "").lower()
    richiedi(
        ricerca == ricerca.strip()
        and len(ricerca) <= 80
        and not any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in ricerca),
        "invalid_q",
    )
    richiedi(richiesta.get("includeReadState") in (None, "1"), "invalid_read_state_option")
    ambito = f"conversations:{t}:{ricerca}"
    p = paginazione.parametri(identita, ambito, richiesta)
    p["ricerca"] = (
        "%" + ricerca.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%" if ricerca else None
    )
    elementi = conversazioni_visibili(db, identita, (t, richiesta.get("includeReadState")), p)
    return paginazione.pagina(identita, (ambito, p["n"] - 1), elementi, "lastMessageId")


def conversazioni_visibili(db, identita, opzioni, parametri):
    tipo, _ = opzioni
    p = dict(parametri)
    elementi, esaminate = [], 0
    while len(elementi) < p["n"]:
        righe = esegui(db, query("conversazioni_" + NOMI[tipo]), p).mappings().all()
        esaminate += len(righe)
        richiedi(esaminate <= 4096, "conversation_page_too_large", 503)
        elementi.extend(filtra_conversazioni(db, identita, opzioni, righe))
        if len(righe) < p["n"]:
            break
        p["prima"] = righe[-1]["last_message_id"]
    return elementi


def filtra_conversazioni(db, identita, opzioni, righe):
    t, _ = opzioni
    elementi = []
    for r in righe:
        try:
            da_storico(
                db,
                identita.utente_id,
                (t, str(r["conversation_id"]), None if r["is_public"] is None else bool(r["is_public"])),
            )
            elementi.append(conversazione(db, identita, opzioni, r))
        except ErroreRealtime as e:
            if e.status_code not in (403, 404):
                raise
    return elementi


def conversazione(db, i, opzioni, r):
    t, stato = opzioni
    mid = r["last_message_id"]
    d = dict(
        destinationType=t,
        conversationId=str(r["conversation_id"]),
        label=r["conversation_label"],
        isPublic=None if r["is_public"] is None else bool(r["is_public"]),
        lastMessageId=mid,
        lastMessageSenderUserId=r["sender_user_id"],
        lastMessageSenderName=r["sender_name"],
        lastMessageContent=r["message_content"],
        lastMessageAt=istante(db, t, mid, r["message_at"]),
        resourceCode=r["resource_code"],
        peerUserId=r["peer_user_id"],
    )
    if stato:
        legacy = (
            t == "PERSON"
            and esegui(
                db, "SELECT messaggio_lettoSN FROM {ticket}messaggio WHERE messaggio_id=:id", dict(id=mid)
            ).scalar()
        )
        d["lastMessageRead"] = (
            bool(legacy) or r["sender_user_id"] == i.utente_id or letto(db, i.utente_id, t, mid)
        )
    return d
