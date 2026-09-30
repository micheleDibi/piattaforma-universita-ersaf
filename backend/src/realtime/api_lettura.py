import re

from fastapi import APIRouter, Depends, Request
from src.database import SessionLocal
from src.realtime import attenzione, lettura, notifiche_lettura
from src.realtime.contratti import corpo_vuoto, parametri, positivo
from src.realtime.errori import richiedi
from src.realtime.sessioni import identita_http

router = APIRouter(prefix="/api/v1")


@router.get("/conversations")
def conversazioni(request: Request, i=Depends(identita_http)):
    p = parametri(request, {"destinationType", "q", "limit", "cursor", "includeReadState"})
    with SessionLocal() as db:
        return lettura.conversazioni(db, i, p)


@router.get("/messages")
def messaggi(request: Request, i=Depends(identita_http)):
    p = parametri(request, {"destinationType", "conversationId", "isPublic", "limit", "cursor"})
    with SessionLocal() as db:
        return lettura.messaggi(db, i, p)


@router.get("/notifications")
def notifiche(request: Request, i=Depends(identita_http)):
    p = parametri(request, {"operations", "limit", "cursor"})
    with SessionLocal() as db:
        return notifiche_lettura.pagina(db, i, p)


@router.get("/messages/attention")
def stato_messaggi(request: Request, i=Depends(identita_http)):
    parametri(request, set())
    with SessionLocal() as db:
        return attenzione.stato(db, i, "message")


@router.get("/notifications/attention")
def stato_notifiche(request: Request, i=Depends(identita_http)):
    parametri(request, set())
    with SessionLocal() as db:
        return attenzione.stato(db, i, "notification")


async def azione_snapshot(request, i, dominio):
    await corpo_vuoto(request)
    p = parametri(request, {"action", "snapshotId"})
    from fastapi.concurrency import run_in_threadpool

    def esegui():
        with SessionLocal.begin() as db:
            return attenzione.snapshot(db, i, dominio, p)

    return await run_in_threadpool(esegui)


@router.post("/messages/attention")
async def visti_messaggi(request: Request, i=Depends(identita_http)):
    return await azione_snapshot(request, i, "message")


@router.post("/notifications/attention")
async def viste_notifiche(request: Request, i=Depends(identita_http)):
    return await azione_snapshot(request, i, "notification")


@router.post("/notifications")
def leggi_notifica(request: Request, i=Depends(identita_http), _=Depends(corpo_vuoto)):
    p = parametri(request, {"notificationId"})
    with SessionLocal.begin() as db:
        return attenzione.leggi_notifica(db, i, numero(p, "notificationId"))


def numero(p, campo):
    n = positivo(p, campo)
    richiedi(n <= 2147483647, "invalid_" + campo)
    return n


@router.post("/messages/read")
def leggi_messaggio(request: Request, i=Depends(identita_http), _=Depends(corpo_vuoto)):
    p = parametri(request, {"destinationType", "messageId"})
    with SessionLocal.begin() as db:
        return attenzione.leggi_messaggio(db, i, p.get("destinationType"), numero(p, "messageId"))


@router.get("/messages/read")
def messaggi_letti(request: Request, i=Depends(identita_http)):
    p = parametri(request, {"destinationType", "ids"})
    ids = p.get("ids", "").split(",")
    richiedi(
        1 <= len(ids) <= 100 and all(re.fullmatch(r"[1-9][0-9]{0,9}", v) for v in ids), "invalid_message_ids"
    )
    with SessionLocal() as db:
        return attenzione.ids_letti(db, i, p.get("destinationType"), list(map(int, ids)))
