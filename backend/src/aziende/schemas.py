from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class AziendaBase(BaseModel):
    azienda_ragione_sociale: str
    azienda_partitaIVA: Optional[str] = None
    azienda_codiceFiscale: Optional[str] = None
    azienda_fatturazioneSDI: Optional[str] = None
    azienda_via: str
    azienda_civico: Optional[str] = None
    azienda_citta: str
    azienda_CAP: str | None = None
    azienda_provincia: str | None = None
    azienda_sitoWeb: Optional[str] = None
    azienda_email: Optional[str] = None
    azienda_telefono: Optional[str] = None
    azienda_pec: Optional[str] = None
    azienda_logo: Optional[str] = None
    azienda_codice_nazionale: str
    azienda_iban: Optional[str] = None
    azienda_codice_bic: Optional[str] = None

class AziendaCreate(AziendaBase):
    pass

class AziendaResponse(AziendaBase):
    azienda_id: int
    
    model_config = ConfigDict(from_attributes=True)

class Config:
        from_attributes = True