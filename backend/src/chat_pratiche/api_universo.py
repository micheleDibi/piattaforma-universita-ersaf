"""Contratto di lettura/chiavi Universo limitato alle pratiche."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text

from src.database import SessionLocal
from src.chat_pratiche.identita_universo import identita_http
from src.chat_pratiche.partecipanti import autorizza
from src.chat_pratiche.chiavi import ChiaviConversazione
from src.chat_pratiche.configurazione import chiavi
from src.chat_pratiche.storico import SELECT, confine, cursore, data_record

router = APIRouter(prefix="/chat-universo", dependencies=[Depends(identita_http)])


class RichiestaChiave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destinationType: Literal["PRACTICE"]
    resourceId: str = Field(pattern=r"^[1-9][0-9]{0,9}$")
    resourceCode: str = Field(min_length=1, max_length=45)
    peerUserId: str | None = Field(default=None, pattern=r"^[1-9][0-9]{0,9}$")
    keyVersion: int | None = Field(default=None, ge=1, le=255)
    epochHour: int | None = Field(default=None, ge=490896, le=4294967295)


@router.post("/crypto/key")
def chiave_conversazione(dati: RichiestaChiave, response: Response, identita=Depends(identita_http)):
    chiavi()
    response.headers["Cache-Control"] = "no-store"
    with SessionLocal() as db:
        contesto, persone = autorizza(db, identita.utente_id, int(dati.resourceId))
        if contesto.numero != dati.resourceCode:
            raise HTTPException(403, "Pratica non corrispondente.")
        if dati.peerUserId and (int(dati.peerUserId) == identita.utente_id
                or int(dati.peerUserId) not in {p.utente_id for p in persone}):
            raise HTTPException(403, "Partecipante non autorizzato.")
        materiale = ChiaviConversazione(db, contesto).chiave(dati.keyVersion, dati.epochHour, dati.peerUserId)
        return dict(format="u2", algorithm="AES-256-GCM", **materiale)


@router.get("/api/v1/messages")
def storico_universo(response: Response, destinationType: Literal["PRACTICE"],
        conversationId: int = Query(gt=0), cursor: str | None = Query(None, max_length=512),
        limit: int = Query(30, ge=1, le=100), identita=Depends(identita_http)):
    chiavi()
    response.headers["Cache-Control"] = "no-store"
    with SessionLocal() as db:
        contesto, _ = autorizza(db, identita.utente_id, conversationId)
        righe = db.execute(text(SELECT + " AND m.messaggio_id < :prima ORDER BY m.messaggio_id DESC LIMIT :n"),
            dict(p=conversationId, prima=confine(contesto, cursor), n=limit+1)).mappings().all()
        altri, elementi = len(righe) > limit, righe[:limit]
        letti = set(db.scalars(text("""SELECT item_id FROM realtime_message_state
            WHERE utente_id=:u AND read_at IS NOT NULL AND item_id BETWEEN :min AND :max"""),
            dict(u=identita.utente_id, min=min((r["messageId"]*4+1 for r in elementi), default=0),
                 max=max((r["messageId"]*4+1 for r in elementi), default=0))))
        return dict(items=[dict(messageId=r["messageId"], senderUserId=r["senderUserId"],
            senderName=r["senderName"], recipientUserId=r["recipientUserId"], content=r["content"],
            createdAt=data_record(r), read=True if r["senderUserId"] == identita.utente_id
                or r["messageId"]*4+1 in letti else None) for r in elementi], hasMore=altri,
            nextCursor=cursore(contesto, elementi[-1]["messageId"]) if altri else None,
            cryptoContext=dict(destinationType="PRACTICE", resourceId=str(conversationId), resourceCode=contesto.numero))
