from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database import get_db
from src.utenti.models import Utente

router = APIRouter(prefix="/auth", tags=["Login"])

class LoginRequest(BaseModel):
    utente_username: str
    utente_password: str

@router.post("/login")
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Utente).filter(Utente.utente_username == creds.utente_username).first()
    
    if not user or user.utente_password != creds.utente_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password errati"
        )
        
    ruolo_codice = user.clienti.ruolo.ruolo_codice
    
    if ruolo_codice and ruolo_codice.lower() == "nazionale":
        print("ALERT: Richiesta verifica a due fattori (2FA) per utente Nazionale")
        return {
            "requires_2fa": True,
            "message": "Verifica a due fattori richiesta (2FA)",
            "utente_username": user.utente_username
        }

    return {
        "message": "Login effettuato con successo",
        "utente_id": user.utente_id,
        "utente_username": user.utente_username,
        "ruolo_codice": ruolo_codice
    }