from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UtenteBase(BaseModel):
    utente_username: str
    utente_padre: Optional[int] = None
    utente_attivoSN: Optional[int] = -1

class UtenteCreate(UtenteBase):
    utente_password: str
    utente_created_by: Optional[int] = None
    utente_updated_by: Optional[int] = None
    utente_salt: str

class UtenteResponse(UtenteBase):
    utente_id: int
    utente_ultimo_login: Optional[datetime] = None
    utente_ultimo_logout: Optional[datetime] = None
    utente_created_by: Optional[int] = None
    utente_created_at: Optional[datetime] = None
    utente_updated_by: Optional[int] = None
    utente_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)