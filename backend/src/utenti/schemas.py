from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ClientePadreSchema(BaseModel):
    cliente_id: int
    cliente_nome: Optional[str] = None
    cliente_cognome: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UtentePadreSchema(BaseModel):
    """L'utente padre, e chi ha aggiornato la riga.

    Erano tipizzati ClientePadreSchema perche' la ForeignKey puntava a
    clienti.cliente_id. Il database punta a utenti.utente_id, quindi lo schema
    risolveva l'id contro la tabella sbagliata e mostrava nome e cognome di
    un'altra persona in circa il 90% dei casi. Il nome resta raggiungibile
    attraverso `cliente`.
    """

    utente_id: int
    utente_username: str
    cliente: Optional[ClientePadreSchema] = None

    model_config = ConfigDict(from_attributes=True)


class UtenteBase(BaseModel):
    utente_username: str
    utente_padre: Optional[int] = None
    utente_attivoSN: Optional[int] = -1


class UtenteCreate(UtenteBase):
    utente_password: str
    utente_created_by: Optional[int] = None
    utente_updated_by: Optional[int] = None


class UtenteUpdate(UtenteBase):
    utente_username: Optional[str] = None
    utente_attivoSN: Optional[int] = None


class UtenteResponse(BaseModel):
    utente_id: int
    utente_username: str
    utente_padre: Optional[int] = None
    padre: Optional[UtentePadreSchema] = None
    utente_updated_by: Optional[int] = None
    aggiornato_da: Optional[UtentePadreSchema] = None
    utente_attivoSN: int
    utente_created_at: Optional[date] = None
    utente_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)