from fastapi import APIRouter, Depends, HTTPException, status
from src.utenti.models import Utente
from sqlalchemy.orm import Session
from src.utenti.schemas import UtenteResponse, UtenteBase, UtenteCreate
from src.database import get_db
from typing import List


router = APIRouter(
    prefix="/utenti", tags=["Utenti"]
)

#POST
@router.post("/", response_model=UtenteResponse, status_code=status.HTTP_201_CREATED)
def crea_utente(utente: UtenteCreate, db: Session = Depends(get_db)):
    db_utente = Utente(**utente.model_dump())
    db.add(db_utente)
    db.commit()
    db.refresh(db_utente)
    return db_utente

#GET ALL
@router.get("/", response_model=List[UtenteResponse])
def leggi_utenti(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    utenti = db.query(Utente).offset(skip).limit(limit).all()
    return utenti

#GET BY ID
@router.get("/{utente_id}", response_model=UtenteResponse)
def leggi_utente(utente_id: int, db: Session = Depends(get_db)):
    db_utente = db.query(Utente).filter(Utente.utente_id == utente_id).first()
    if not db_utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return db_utente

#PUT
@router.put("/{utente_id}", response_model=UtenteResponse)
def aggiorna_utente(utente_id: int, utente: UtenteCreate, db: Session = Depends(get_db)):
    db_utente = db.query(Utente).filter(Utente.utente_id == utente_id).first()
    if not db_utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    for key, value in utente.model_dump().items():
        setattr(db_utente, key, value)
        
    db.commit()
    db.refresh(db_utente)
    return db_utente

#DELETE
@router.delete("/{utente_id}", status_code=status.HTTP_204_NO_CONTENT)
def elimina_utente(utente_id: int, db: Session = Depends(get_db)):
    db_utente = db.query(Utente).filter(Utente.utente_id == utente_id).first()
    if not db_utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    db.delete(db_utente)
    db.commit()
    return None