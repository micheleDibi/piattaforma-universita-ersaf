from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from src.auth.dipendenze import get_current_utente
from src.auth.visibilita import visibilita_corrente
from src.database import get_db
from src.chat_pratiche.contesto import contesto_chat
from src.chat_pratiche.java import ServizioJava
from src.chat_pratiche.cifratura import cifra, decifra

router = APIRouter()


class MessaggioIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    testo: str = Field(min_length=1, max_length=1000)
    clientMessageId: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")


@router.post("/{pratica_id}/messaggi/prepara")
def prepara_messaggio(pratica_id: int, dati: MessaggioIn, response: Response,
                      db: Session = Depends(get_db), vis=Depends(visibilita_corrente), utente=Depends(get_current_utente)):
    java = ServizioJava(contesto_chat(db, pratica_id, vis, utente))
    try:
        response.headers["Cache-Control"] = "no-store"
        return {"cifrato": cifra(java, dati.testo, dati.clientMessageId), "clientMessageId": dati.clientMessageId}
    except ValueError:
        raise HTTPException(422, "Il messaggio è vuoto o supera 1000 byte.") from None
    finally:
        java.chiudi()


@router.get("/{pratica_id}/messaggi")
def messaggi(pratica_id: int, response: Response, cursor: str | None = Query(None, max_length=4096),
             db: Session = Depends(get_db), vis=Depends(visibilita_corrente), utente=Depends(get_current_utente)):
    contesto = contesto_chat(db, pratica_id, vis, utente)
    java = ServizioJava(contesto)
    try:
        parametri = dict(destinationType="PRACTICE", conversationId=str(pratica_id), limit=30)
        if cursor:
            parametri["cursor"] = cursor
        pagina = java.richiesta("GET", "/api/v1/messages", params=parametri)
        contesto_remoto = pagina.get("cryptoContext", {})
        if (contesto_remoto.get("destinationType") != "PRACTICE"
                or str(contesto_remoto.get("resourceId")) != str(pratica_id)
                or contesto_remoto.get("resourceCode") != contesto.numero):
            raise HTTPException(503, "La conversazione non corrisponde alla pratica richiesta.")
        elementi = []
        for record in pagina["items"]:
            try:
                testo = decifra(java, record)
            except HTTPException as errore:
                if errore.status_code != 403:
                    raise
                # I grant storici Universo possono escludere singoli messaggi
                # anche quando la partecipazione attuale alla chat e' valida.
                testo = "Messaggio non disponibile per questo account"
            except Exception:
                testo = "Messaggio non decifrabile"
            elementi.append(dict(id=str(record["messageId"]), autore=record["senderName"],
                mio=str(record["senderUserId"]) == str(contesto.utente_id), testo=testo, data=record["createdAt"]))
        response.headers["Cache-Control"] = "no-store"
        return dict(elementi=elementi, cursore=pagina.get("nextCursor"), altri=pagina["hasMore"])
    finally:
        java.chiudi()
