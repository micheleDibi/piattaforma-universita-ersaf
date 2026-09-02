from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.ruolo.schemas import  RuoloCreate, RuoloResponse
from src.database import get_db
from src.ruolo.models import Ruolo

router = APIRouter(prefix="/ruoli", tags=["Ruoli"])

@router.post("/", response_model=RuoloResponse, status_code=status.HTTP_201_CREATED)
def crea_ruolo(ruolo: RuoloCreate, db: Session = Depends(get_db)):
    db_ruolo = Ruolo(**ruolo.model_dump())
    db.add(db_ruolo)
    db.commit()
    db.refresh(db_ruolo)
    return db_ruolo

#GET ALL
@router.get("/", response_model=List[RuoloResponse])
def leggi_ruoli(db:Session = Depends(get_db)):
    ruoli = db.query(Ruolo).all()
    return ruoli

#GET BY ID
@router.get("/{ruolo_id}", response_model=RuoloResponse)
def leggi_ruolo(ruolo_id: int, db: Session = Depends(get_db)):
    db_ruolo = db.query(Ruolo).filter(Ruolo.ruolo_id == ruolo_id).first()
    if not db_ruolo:
        raise HTTPException(status_code=404, detail="Ruolo non trovato")
    return db_ruolo

#PUT
@router.put("/{ruolo_id}", response_model=RuoloResponse)
def aggiorna_ruolo(ruolo_id: int, ruolo: RuoloCreate, db: Session = Depends(get_db)):
    db_ruolo = db.query(Ruolo).filter(Ruolo.ruolo_id == ruolo_id).first()
    if not db_ruolo:
        raise HTTPException(status_code=404, detail="Ruolo non trovato")
    
    for key, value in ruolo.model_dump().items():
        setattr(db_ruolo, key, value)
        
    db.commit()
    db.refresh(db_ruolo)
    return db_ruolo

#DELETE
@router.delete("/{ruolo_id}", status_code=status.HTTP_204_NO_CONTENT)
def elimina_ruolo(ruolo_id: int, db: Session = Depends(get_db)):
    db_ruolo = db.query(Ruolo).filter(Ruolo.ruolo_id == ruolo_id).first()
    if not db_ruolo:
        raise HTTPException(status_code=404, detail="Ruolo non trovato")
    
    db.delete(db_ruolo)
    db.commit()
    return None