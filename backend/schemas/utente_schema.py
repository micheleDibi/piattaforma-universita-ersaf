from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class UtenteCreate(BaseModel):
    utente_username: str
    utente_password: str
    utente_padre: Optional[int] = None
    utente_attivoSN: Optional[int] = 1

class UtenteResponse(BaseModel):
    utente_id: int
    utente_username: str
    utente_ultimo_login: Optional[datetime] = None
    utente_ultimo_logout: Optional[datetime] = None
    utente_padre: Optional[int] = None
    utente_attivoSN: Optional[int] = None
    utente_created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UtenteLogin(BaseModel):
    utente_username: str
    utente_password: str


