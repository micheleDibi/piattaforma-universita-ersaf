from pydantic import BaseModel, ConfigDict

class RuoloBase(BaseModel):
    ruolo_codice: str
    ruolo_descrizione: str

class RuoloCreate(RuoloBase):
    pass

class RuoloResponse(RuoloBase):
    ruolo_id: int

    model_config = ConfigDict(from_attributes=True)