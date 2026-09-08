from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.listino_tipoCorso.models import ListinoTipoCorsoDB, ListinoTipoCorso, ListinoTipoCorsoCreate
from src.database import get_db

router = APIRouter(
    prefix="/listini-tipi-corsi",
    tags=["Listini Tipi Corsi"]
)

#  POST
@router.post("/", response_model=ListinoTipoCorso, status_code=status.HTTP_201_CREATED)
def create_listino_tipo_corso(corso: ListinoTipoCorsoCreate, db: Session = Depends(get_db)):
    db_corso = ListinoTipoCorsoDB(listino_tipoCorso_descrizione=corso.listino_tipoCorso_descrizione)
    db.add(db_corso)
    db.commit()
    db.refresh(db_corso)
    return db_corso

#  GET ALL
@router.get("/", response_model=List[ListinoTipoCorso])
def get_listino_tipi_corso(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    corsi = db.query(ListinoTipoCorsoDB).offset(skip).limit(limit).all()
    return corsi

# GET BY ID 
@router.get("/{corso_id}", response_model=ListinoTipoCorso)
def get_listino_tipo_corso_by_id(corso_id: int, db: Session = Depends(get_db)):
    db_corso = db.query(ListinoTipoCorsoDB).filter(ListinoTipoCorsoDB.listino_tipoCorso_id == corso_id).first()
    if db_corso is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo corso non trovato")
    return db_corso

# UPDATE 
@router.put("/{corso_id}", response_model=ListinoTipoCorso)
def update_listino_tipo_corso(corso_id: int, corso: ListinoTipoCorsoCreate, db: Session = Depends(get_db)):
    db_corso = db.query(ListinoTipoCorsoDB).filter(ListinoTipoCorsoDB.listino_tipoCorso_id == corso_id).first()
    if db_corso is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo corso non trovato")
    
    db_corso.listino_tipoCorso_descrizione = corso.listino_tipoCorso_descrizione
    db.commit()
    db.refresh(db_corso)
    return db_corso