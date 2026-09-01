from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.utente_schema import UtenteCreate, UtenteResponse
from services.utente_service import register_utente
from schemas.utente_schema import UtenteLogin
from services.utente_service import authenticate_utente

router = APIRouter(prefix="/utenti", tags=["Utenti"])

@router.post("/", response_model=UtenteResponse, status_code=status.HTTP_201_CREATED)
def create_utente(utente_dto: UtenteCreate, db: Session = Depends(get_db)):
    return register_utente(db=db, utente_dto=utente_dto)

@router.post("/login", status_code=status.HTTP_200_OK)
def login_utente(login_dto: UtenteLogin, db: Session = Depends(get_db)):
    return authenticate_utente(db=db, login_dto=login_dto)