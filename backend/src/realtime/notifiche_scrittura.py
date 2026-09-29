"""Notifiche applicative con ricevuta del produttore e bridge legacy condiviso."""

import hashlib
import hmac
import json
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

from src.realtime.consegne import accoda
from src.realtime.dati import esegui, json_compatibile, ora
from src.realtime.errori import richiedi

OPERAZIONI = dict(PERSON="messaggioPersonale", PRACTICE="messaggioPratiche", TICKET="messaggioTicket")


def registra(db, comando, contesto=None):
    cliente = destinatario(db, comando["target"], comando["createdBy"])
    adesso = ora()
    pid = esegui(
        db,
        """INSERT INTO notifiche_parameters
        (notifica_parameter_operation,notifica_parameter_id_ref,notifica_parameter_message)
        VALUES (:operation,:idRef,:message)""",
        comando,
    ).lastrowid
    locale = adesso.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Europe/Rome")).replace(tzinfo=None)
    nid = esegui(
        db,
        """INSERT INTO notifiche (notifica_title,notifica_body,notifica_created_by,
        notifica_created_at,notifica_updated_by,notifica_updated_at,notifica_parameter_id,notifica_letta,cliente_id)
        VALUES (:title,:message,:createdBy,:now,:createdBy,:now,:pid,0,:cid)""",
        dict(comando, now=locale, pid=pid, cid=cliente),
    ).lastrowid
    payload = dict(
        notificationId=nid,
        fromUserId=comando["createdBy"],
        utenteCreatedBy=comando["createdBy"],
        utenteId=comando["target"],
        operation=comando["operation"],
        idRef=comando["idRef"],
        title=comando["title"],
        message=comando["message"],
        timestamp=int(adesso.replace(tzinfo=timezone.utc).timestamp() * 1000),
    )
    if contesto:
        payload["messageContext"] = contesto
    esegui(
        db,
        "INSERT INTO realtime_notification_bridge VALUES (:id,:now,'DELIVERED',NULL)",
        dict(id=nid, now=adesso),
    )
    accoda(db, comando["target"], "notification", payload)
    return payload, pid


def destinatario(db, target, autore):
    # Il creatore deve essere attivo; solo il destinatario deve avere un
    # cliente unico. Il produttore puo essere un utente di servizio senza ruolo.
    righe = esegui(
        db,
        """SELECT u.utente_id,u.utente_attivoSN,c.cliente_id
        FROM utenti u LEFT JOIN clienti c ON c.utente_id=u.utente_id
        WHERE u.utente_id IN (:t,:a) ORDER BY u.utente_id,c.cliente_id FOR UPDATE""",
        dict(t=target, a=autore),
    ).all()
    destinatari = [r for r in righe if r.utente_id == target]
    richiedi(
        len(destinatari) == 1
        and destinatari[0].utente_attivoSN == -1
        and destinatari[0].cliente_id is not None,
        "target_not_found",
        422,
    )
    richiedi(
        any(r.utente_id == autore and r.utente_attivoSN == -1 for r in righe), "created_by_not_found", 422
    )
    return destinatari[0].cliente_id


def dal_messaggio(db, c, d):
    sender = int(d["from"])
    nome = next(p.nome for p in c.persone if p.utente_id == sender)
    for p in c.persone:
        if p.utente_id == sender:
            continue
        context = dict(
            destinationType=c.tipo,
            conversationId=d["codice"] if c.tipo == "PERSON" else c.risorsa,
            cryptoContext=c.crypto(p.utente_id),
        )
        if c.tipo == "TICKET":
            context["isPublic"] = c.pubblico
        registra(
            db,
            dict(
                target=p.utente_id,
                createdBy=sender,
                operation=OPERAZIONI[c.tipo],
                idRef=d["messaggioId"],
                title=nome or f"Utente {sender}",
                message=d["content"],
            ),
            context,
        )


def produttore(db, comando):
    # Serializza l'idempotenza, anche tra processi, senza lock globale del servizio.
    from src.realtime.eventi import blocca

    blocca(db, comando["target"])
    canonico = {k: comando[k] for k in ("target", "createdBy", "operation", "idRef", "title", "message")}
    digest = hashlib.sha256(json_compatibile(canonico).encode()).digest()
    vecchio = esegui(
        db,
        """SELECT request_hash,canonical_payload FROM realtime_notification_command
        WHERE producer_event_id=:id FOR UPDATE""",
        dict(id=comando["producerEventId"]),
    ).first()
    if vecchio:
        richiedi(hmac.compare_digest(vecchio.request_hash, digest), "producer_event_conflict", 409)
        richiedi(vecchio.canonical_payload is not None, "command_incomplete", 503)
        return json.loads(vecchio.canonical_payload), True
    payload, pid = registra(db, comando)
    esegui(
        db,
        """INSERT INTO realtime_notification_command VALUES (:id,:h,:u,:n,:p,:json,:now,:exp)""",
        dict(
            id=comando["producerEventId"],
            h=digest,
            u=comando["target"],
            n=payload["notificationId"],
            p=pid,
            json=json.dumps(payload),
            now=ora(),
            exp=ora() + timedelta(days=30),
        ),
    )
    return payload, False
