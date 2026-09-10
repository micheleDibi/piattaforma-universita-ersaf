from pydantic import BaseModel, ConfigDict
from typing import Optional


class RuoloBase(BaseModel):
    ruolo_codice: str
    ruolo_descrizione: str


class RuoloCreate(RuoloBase):
    pass


class RuoloUpdate(BaseModel):
    """Tutti i campi opzionali: un PUT parziale non deve azzerare il resto.

    Il PUT riusava RuoloCreate con model_dump() senza exclude_unset. Su questa
    tabella la conseguenza era piu' seria che altrove: ruolo_codice decide il
    gate 2FA del login e il filtro degli attuatori, quindi riscriverlo per
    sbaglio cambia chi entra e cosa vede.
    """

    model_config = ConfigDict(from_attributes=True)

    ruolo_codice: Optional[str] = None
    ruolo_descrizione: Optional[str] = None


class RuoloResponse(RuoloBase):
    ruolo_id: int

    model_config = ConfigDict(from_attributes=True)
