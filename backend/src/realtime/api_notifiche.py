import hmac
import re
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from src.chat_pratiche.configurazione import configurazione
from src.database import SessionLocal
from src.realtime import testi
from src.realtime.contratti import corpo, stringa, uuid_canonico
from src.realtime.errori import richiedi
from src.realtime.notifiche_scrittura import produttore
from src.realtime.transazioni import ritenta

router = APIRouter()


def autentica(request: Request):
    file = configurazione().realtime_producer_token_file
    richiedi(bool(file), "producer_unavailable", 503)
    try:
        token = Path(file).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        richiedi(False, "producer_unavailable", 503)
    richiedi(32 <= len(token) <= 512 and not any(c.isspace() for c in token), "producer_unavailable", 503)
    header = request.headers.getlist("authorization")
    richiedi(
        len(header) == 1
        and len(header[0]) <= 1024
        and header[0].lower().startswith("bearer ")
        and hmac.compare_digest(header[0][7:].encode(), token.encode()),
        "invalid_producer_token",
        401,
    )


def invia(d):
    d = dict(d)
    richiedi(set(d) == {"producerEventId", "target", "createdBy", "operation", "idRef", "title", "message"})
    d["producerEventId"] = uuid_canonico(stringa(d, "producerEventId", 36).lower())
    for campo in ("target", "createdBy"):
        richiedi(type(d[campo]) in (int, float) and 0 < d[campo] <= 2147483647 and int(d[campo]) == d[campo])
        d[campo] = int(d[campo])
    for campo, pattern in (
        ("operation", r"[A-Za-z][A-Za-z0-9_-]{0,63}"),
        ("idRef", r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,44}"),
    ):
        richiedi(re.fullmatch(pattern, stringa(d, campo)))
    for campo in ("title", "message"):
        d[campo] = testi.produttore(d[campo], multilinea=campo == "message")
    payload, duplicato = registra_con_retry(d)
    return JSONResponse(
        status_code=200 if duplicato else 201,
        content=dict(
            producerEventId=d["producerEventId"],
            notificationId=payload["notificationId"],
            status="duplicate" if duplicato else "accepted",
        ),
    )


@ritenta
def registra_con_retry(comando):
    # Un ID produttore e globale: due destinatari diversi possono concorrere.
    # Ripetere l'intera transazione legge la ricevuta vincente e restituisce 409.
    with SessionLocal.begin() as db:
        return produttore(db, comando)


@router.post("/internal/notifications", dependencies=[Depends(autentica)])
async def notifica(request: Request):
    return await run_in_threadpool(invia, await corpo(request))
