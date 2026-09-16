from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime


class AziendaXCodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    azienda_xCod_id: int
    azienda_padre_id: Optional[int] = None
    azienda_figlia_id: Optional[int] = None
    azienda_xCod_created_at: Optional[datetime.datetime] = None
    azienda_xCod_updated_at: Optional[datetime.datetime] = None


class AziendaXCodCambiaPadre(BaseModel):
    """Body per il cambio padre di un'azienda esistente.

    nuovo_padre_id=None rende l'azienda una radice (nessun padre): e'
    un'operazione legittima, riservata al nazionale come tutto il resto
    di questo endpoint.
    """

    nuovo_padre_id: Optional[int] = None