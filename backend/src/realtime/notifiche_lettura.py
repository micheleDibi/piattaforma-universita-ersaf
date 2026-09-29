import hashlib
import re

from src.chat_pratiche.cifratura import codifica
from src.realtime import paginazione
from src.realtime.conversazioni import da_storico
from src.realtime.dati import esegui, query
from src.realtime.errori import ErroreRealtime, richiedi
from src.realtime.lettura import istante


def sorgente(filtro=""):
    return query("notifiche_raggruppate").replace("{filtro}", filtro)


def pagina(db, i, richiesta):
    operazioni = richiesta.get("operations", "").split(",") if "operations" in richiesta else []
    richiedi(
        len(richiesta.get("operations", "")) <= 2048
        and len(operazioni) <= 32
        and len(set(operazioni)) == len(operazioni)
        and all(re.fullmatch(r"[A-Za-z][A-Za-z0-9]{0,63}", o) for o in operazioni),
        "invalid_operations",
    )
    operazioni.sort()
    ambito = "notifications:" + codifica(hashlib.sha256(",".join(operazioni).encode()).digest()[:12])
    p = paginazione.parametri(i, ambito, richiesta)
    p.update({"op" + str(n): o for n, o in enumerate(operazioni)})
    filtro = (
        " AND p.notifica_parameter_operation IN ("
        + ",".join(":op" + str(n) for n in range(len(operazioni)))
        + ")"
        if operazioni
        else ""
    )
    righe = (
        esegui(
            db,
            sorgente(filtro)
            + "SELECT * FROM ranked WHERE row_number_in_group=1 AND notifica_id<:prima ORDER BY notifica_id DESC LIMIT :n",
            p,
        )
        .mappings()
        .all()
    )
    elementi = [elemento(db, i, r) for r in righe]
    conteggio = esegui(
        db,
        sorgente() + "SELECT COUNT(*) FROM ranked WHERE row_number_in_group=1 AND notifica_letta=0",
        dict(c=i.cliente_id),
    ).scalar()
    return dict(
        **paginazione.pagina(i, (ambito, p["n"] - 1), elementi, "notificationId"), unreadCount=conteggio
    )


def elemento(db, i, r):
    d = dict(
        notificationId=r["notifica_id"],
        title=r["notifica_title"],
        body=r["notifica_body"],
        createdByUserId=r["notifica_created_by"],
        createdAt=istante(db, "NOTIFICATION", r["notifica_id"], r["notifica_created_at"]),
        read=bool(r["notifica_letta"]),
        operation=r["notifica_parameter_operation"],
        referenceId=r["notifica_parameter_id_ref"],
        message=r["notifica_parameter_message"],
    )
    contesto = contesto_messaggio(db, i, d["operation"], d["referenceId"])
    if contesto:
        d["messageContext"] = contesto
    return d


def contesto_messaggio(db, i, operazione, mid):
    if not re.fullmatch(r"[1-9][0-9]{0,18}", str(mid)):
        return None
    mappa = dict(
        messaggioPersonale=("PERSON", "{ticket}messaggio", "messaggio_id", "messaggio_doc_id"),
        messaggioPratiche=("PRACTICE", "messaggi", "messaggio_id", "pratica_id"),
        messaggioTicket=("TICKET", "{ticket}ticket_messaggio", "ticket_messaggio_id", "ticket_id"),
    )
    if operazione not in mappa:
        return None
    t, tabella, pk, risorsa = mappa[operazione]
    pubblico = "ticket_messaggio_is_public" if t == "TICKET" else "NULL"
    r = esegui(
        db, f"SELECT {risorsa} AS id,{pubblico} AS pubblico FROM {tabella} WHERE {pk}=:id", dict(id=mid)
    ).first()
    if not r:
        return None
    try:
        c = da_storico(db, i.utente_id, (t, str(r.id), None if r.pubblico is None else bool(r.pubblico)))
    except ErroreRealtime as e:
        if e.status_code in (403, 404):
            return None
        raise
    d = dict(destinationType=t, conversationId=str(r.id), cryptoContext=c.crypto(i.utente_id))
    if t == "TICKET":
        d["isPublic"] = bool(r.pubblico)
    return d
