from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud import utente_crud
from schemas.utente_schema import UtenteCreate, UtenteLogin

def register_utente(db: Session, utente_dto: UtenteCreate):
    existing = utente_crud.get_utente_by_username(db, username=utente_dto.utente_username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"L'username '{utente_dto.utente_username}' è già in uso."
        )
    return utente_crud.create_utente(db=db, utente_dto=utente_dto)

def authenticate_utente(db: Session, login_dto: UtenteLogin):
    user = utente_crud.get_utente_by_username(db, username=login_dto.utente_username)
    
    if not user or user.utente_password != login_dto.utente_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password errati."
        )
    
    return {"message": "Login effettuato con successo", "username": user.utente_username}