"""Lettura e salvataggio firma con le autorizzazioni della scheda pratica."""

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from src.auth.visibilita import Visibilita, visibilita_corrente
from src.database import get_db
from src.pratiche.accesso import pratica_visibile
from src.pratiche.firma import MAX_BYTE, normalizza_firma, stato_firma, versione_firma

router = APIRouter()


class FirmaIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    immagine: str = Field(max_length=MAX_BYTE * 4 // 3 + 32)
    versione: str = Field(pattern=r"^[a-f0-9]{64}$")


@router.get("/{pratica_id}/firma")
def leggi_firma(pratica_id: int, response: Response, db: Session = Depends(get_db),
               vis: Visibilita = Depends(visibilita_corrente)):
    pratica = pratica_visibile(db, pratica_id, vis)
    response.headers["Cache-Control"] = "no-store"
    return stato_firma(pratica.pratica_firma)


@router.put("/{pratica_id}/firma")
def salva_firma(pratica_id: int, dati: FirmaIn, response: Response,
                db: Session = Depends(get_db), vis: Visibilita = Depends(visibilita_corrente)):
    pratica_visibile(db, pratica_id, vis)
    png = normalizza_firma(dati.immagine)
    pratica = pratica_visibile(db, pratica_id, vis, blocca=True)
    if versione_firma(pratica.pratica_firma) != dati.versione:
        raise HTTPException(409, "La firma è stata modificata. Ricaricala prima di salvare.")
    pratica.pratica_firma = png
    pratica.pratica_missFlag_firma = 0
    db.commit()
    response.headers["Cache-Control"] = "no-store"
    return stato_firma(png)
