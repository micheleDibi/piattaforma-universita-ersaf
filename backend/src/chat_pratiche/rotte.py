from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from src.auth.dipendenze import get_current_utente
from src.database import get_db
from src.chat_pratiche.partecipanti import autorizza
from src.chat_pratiche.chiavi import ChiaviConversazione
from src.chat_pratiche.cifratura import cifra
from src.chat_pratiche.configurazione import chiavi
from src.chat_pratiche.storico import pagina

router = APIRouter()


class MessaggioIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    testo: str = Field(min_length=1, max_length=1000)
    clientMessageId: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")


@router.post("/{pratica_id}/messaggi/prepara")
def prepara_messaggio(pratica_id: int, dati: MessaggioIn, response: Response,
                      db: Session = Depends(get_db), utente=Depends(get_current_utente)):
    chiavi()
    contesto, _ = autorizza(db, utente.utente_id, pratica_id)
    try:
        response.headers["Cache-Control"] = "no-store"
        return {"cifrato": cifra(ChiaviConversazione(db, contesto), dati.testo, dati.clientMessageId), "clientMessageId": dati.clientMessageId}
    except ValueError:
        raise HTTPException(422, "Il messaggio è vuoto o supera 1000 byte.") from None


@router.get("/{pratica_id}/messaggi")
def messaggi(pratica_id: int, response: Response, cursor: str | None = Query(None, max_length=4096),
             db: Session = Depends(get_db), utente=Depends(get_current_utente)):
    chiavi()
    contesto, _ = autorizza(db, utente.utente_id, pratica_id)
    response.headers["Cache-Control"] = "no-store"
    return pagina(db, contesto, cursor)
