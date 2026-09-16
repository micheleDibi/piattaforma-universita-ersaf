"""Endpoint di lettura e modifica del padre di un'azienda nella gerarchia
aziende_xcod. Lista/ricerca/dettaglio delle aziende in se' vivono in
src.aziende.routers; qui sta solo cio' che riguarda l'arco padre-figlia."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import datetime

from src.auth.dipendenze import get_current_utente
from src.auth.autorizzazioni import richiedi_nazionale
from src.database import get_db
from src.aziende.models import Azienda
from src.aziende_xcod.models import AziendaXCod
from src.aziende_xcod.schemas import AziendaXCodResponse, AziendaXCodCambiaPadre
from src.aziende_xcod.servizi import (
    discendenti_ids,
    calcola_cascata_percentuali,
    applica_cascata_percentuali,
    descrivi_cascata,
    valori_percentuali_di,
)

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


@router.put("/{azienda_id}/padre")
def cambia_padre(
    azienda_id: int,
    dati: AziendaXCodCambiaPadre,
    conferma_reset: bool = Query(False),
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

    # Regola 1 (reset a 0 invece del blocco): si simula lo spostamento sotto
    # il NUOVO padre e si propaga a cascata sui discendenti. Se qualcosa
    # andrebbe azzerato, si chiede conferma prima di scrivere qualunque
    # cosa - sia il reset che il cambio padre stesso.
    valori_attuali = valori_percentuali_di(db, azienda_id)
    cascata = calcola_cascata_percentuali(db, azienda_id, valori_attuali, padre_id=nuovo_padre_id)

    if cascata and not conferma_reset:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"richiede_conferma": True, "reset": descrivi_cascata(db, cascata)},
        )

    if cascata:
        applica_cascata_percentuali(db, azienda_id, valori_attuali, cascata)

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
    return AziendaXCodResponse.model_validate(arco).model_dump()