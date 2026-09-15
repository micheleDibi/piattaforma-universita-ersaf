from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime

from src.auth.dipendenze import get_current_utente
from src.auth.autorizzazioni import richiedi_nazionale
from src.database import get_db
from src.aziende.models import Azienda
from src.aziende_xcod.models import AziendaXCod
from src.aziende_xcod.schemas import AziendaXCodResponse, AziendaXCodCambiaPadre
from src.aziende_xcod.servizi import discendenti_ids

router = APIRouter(
    prefix="/aziende-xcod",
    tags=["Gerarchia aziende"],
    dependencies=[Depends(get_current_utente)],
)


@router.get("/{azienda_id}/padre", response_model=Optional[AziendaXCodResponse])
def leggi_padre(azienda_id: int, db: Session = Depends(get_db)):
    if not db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Azienda non trovata.")

    return (
        db.query(AziendaXCod)
        .filter(AziendaXCod.azienda_figlia_id == azienda_id)
        .order_by(AziendaXCod.azienda_xCod_id.desc())
        .first()
    )


@router.put("/{azienda_id}/padre", response_model=AziendaXCodResponse)
def cambia_padre(
    azienda_id: int,
    dati: AziendaXCodCambiaPadre,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    richiedi_nazionale(db, utente_corrente, "cambio padre azienda")

    if not db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Azienda non trovata.")

    nuovo_padre_id = dati.nuovo_padre_id
    if nuovo_padre_id is not None:
        if nuovo_padre_id == azienda_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un'azienda non può essere padre di se stessa.",
            )
        if not db.query(Azienda).filter(Azienda.azienda_id == nuovo_padre_id).first():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Il nuovo padre indicato non esiste.")
        if nuovo_padre_id in discendenti_ids(db, azienda_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Il nuovo padre è un discendente di questa azienda: creerebbe un ciclo.",
            )

    ora = datetime.datetime.utcnow()
    arco = (
        db.query(AziendaXCod)
        .filter(AziendaXCod.azienda_figlia_id == azienda_id)
        .order_by(AziendaXCod.azienda_xCod_id.desc())
        .first()
    )
    if arco is None:
        arco = AziendaXCod(
            azienda_figlia_id=azienda_id,
            azienda_padre_id=nuovo_padre_id,
            azienda_xCod_created_by=utente_corrente.utente_id,
            azienda_xCod_created_at=ora,
            azienda_xCod_updated_by=utente_corrente.utente_id,
            azienda_xCod_updated_at=ora,
        )
        db.add(arco)
    else:
        arco.azienda_padre_id = nuovo_padre_id
        arco.azienda_xCod_updated_by = utente_corrente.utente_id
        arco.azienda_xCod_updated_at = ora

    db.commit()
    db.refresh(arco)
    return arco