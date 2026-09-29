import time

from fastapi import APIRouter, Depends, Request
from src.chat_pratiche.configurazione import configurazione
from src.database import SessionLocal
from src.realtime import accesso, api_chiavi, api_lettura, api_notifiche, socket
from src.realtime.dati import esegui
from src.realtime.errori import richiedi


def verifica_origine(request: Request):
    origine = request.headers.getlist("origin")
    origini = {o.strip() for o in configurazione().chat_universo_origini.split(",") if o.strip()}
    richiedi(not origine or (len(origine) == 1 and origine[0] in origini), "origin_not_allowed", 403)


router = APIRouter(prefix="/realtime", tags=["Realtime"])
http = APIRouter(dependencies=[Depends(verifica_origine)])
for modulo in (accesso, api_chiavi, api_lettura, api_notifiche):
    http.include_router(modulo.router)
router.include_router(http)
router.include_router(socket.router)


@router.get("/health")
def health():
    return dict(status="ok")


@router.get("/ready", dependencies=[Depends(verifica_origine)])
def ready(request: Request):
    stato = getattr(request.app.state, "realtime", {})
    richiedi(time.monotonic() - stato.get("ultimo_successo", 0) < 15, "realtime_not_ready", 503)
    with SessionLocal() as db:
        esegui(db, "SELECT 1")
    return dict(status="ready")
