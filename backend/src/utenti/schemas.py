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
    # utente_salt NON e' piu' accettato dal chiamante: e' un residuo Instant
    # Developer che bcrypt non usa, e lasciarlo scegliere dall'esterno non ha
    # alcun senso. Viene generato dal server.


class UtenteUpdate(UtenteBase):
    """Aggiornamento di un utente.

    SENZA `utente_password` e SENZA `utente_salt`. Prima il PUT accettava
    `UtenteCreate` e un ciclo di setattr scriveva la password in chiaro nella
    colonna a ogni aggiornamento, senza hashing e senza validazione. La
    password si cambia solo dai flussi dedicati: il rehash al login e
    /auth/password-reset/confirm.
    """

    utente_username: Optional[str] = None
    utente_attivoSN: Optional[int] = None


class UtenteResponse(UtenteBase):
    utente_id: int
    utente_ultimo_login: Optional[datetime] = None
    utente_ultimo_logout: Optional[datetime] = None
    utente_created_by: Optional[int] = None
    utente_created_at: Optional[datetime] = None
    utente_updated_by: Optional[int] = None
    utente_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
