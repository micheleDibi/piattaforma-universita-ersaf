from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db 
from src.universita.models import Universita as UniversitaModel
from src.universita.schemas import Universita, UniversitaCreate, UniversitaUpdate

router = APIRouter(
    prefix="/universita",tags=["Universita"])

# GET ALL 
@router.get("/", response_model=List[Universita])
def get_universita_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    universita_list = db.query(UniversitaModel).offset(skip).limit(limit).all()
    return universita_list

# GET BY ID
@router.get("/{universita_id}", response_model=Universita)
def get_universita_by_id(universita_id: int, db: Session = Depends(get_db)):
    universita = db.query(UniversitaModel).filter(UniversitaModel.universita_id == universita_id).first()
    if not universita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Università con id {universita_id} non trovata"
        )
    return universita

# POST 
@router.post("/", response_model=Universita, status_code=status.HTTP_201_CREATED)
def create_universita(universita_data: UniversitaCreate, db: Session = Depends(get_db)):
    # Converte i dati ricevuti dallo schema in un'istanza del modello SQLAlchemy
    db_universita = UniversitaModel(**universita_data.model_dump())
    db.add(db_universita)
    db.commit()
    db.refresh(db_universita)
    return db_universita

# PUT 
@router.put("/{universita_id}", response_model=Universita)
def update_universita(universita_id: int, universita_data: UniversitaUpdate, db: Session = Depends(get_db)):
    db_universita = db.query(UniversitaModel).filter(UniversitaModel.universita_id == universita_id).first()
    if not db_universita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Università con id {universita_id} non trovata"
        )
    
    # Aggiorna solo i campi forniti nella richiesta (escludendo quelli non impostati)
    update_data = universita_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_universita, key, value)
        
    db.commit()
    db.refresh(db_universita)
    return db_universita