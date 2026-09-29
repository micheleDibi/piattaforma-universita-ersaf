from dataclasses import replace

from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool
from src.database import SessionLocal
from src.realtime import crypto
from src.realtime.contratti import corpo, positivo
from src.realtime.conversazioni import autorizza
from src.realtime.errori import richiedi
from src.realtime.sessioni import identita_http

router = APIRouter()


def materiale(i, dati):
    t = dati.get("destinationType")
    richiedi(
        isinstance(t, str) and t in {"PERSON", "PRACTICE", "TICKET"},
        "invalid_destinationType",
    )
    campi = {"destinationType", "keyVersion", "epochHour"}
    campi |= (
        {"peerUserId"}
        if t == "PERSON"
        else {"resourceId", "resourceCode", "peerUserId"}
        if t == "PRACTICE"
        else {"resourceId", "isPublic"}
    )
    richiedi(set(dati) <= campi)
    risorsa = positivo(dati, "peerUserId" if t == "PERSON" else "resourceId")
    with SessionLocal() as db:
        c = autorizza(db, i.utente_id, (t, risorsa, dati.get("isPublic")))
        if t == "PRACTICE":
            richiedi(c.codice == dati.get("resourceCode"), "practice_reference_mismatch", 403)
            if dati.get("peerUserId") is not None:
                peer = positivo(dati, "peerUserId")
                richiedi(
                    peer != i.utente_id and peer in {p.utente_id for p in c.persone},
                    "historical_key_access_denied",
                    403,
                )
                a, b = sorted((peer, i.utente_id))
                c = replace(c, dominio=f"PRACTICE:{risorsa}:{a}:{b}")
        return crypto.chiave(db, i.utente_id, c, (dati.get("keyVersion"), dati.get("epochHour")))


@router.post("/crypto/key")
async def chiave(request: Request, i=Depends(identita_http)):
    return await run_in_threadpool(materiale, i, await corpo(request, 4096))
