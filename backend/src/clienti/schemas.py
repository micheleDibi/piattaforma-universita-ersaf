from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, PositiveInt, Field

class ClienteBase(BaseModel):
    cliente_codice: str
    cliente_nome: str
    cliente_cognome: str
    cliente_email: Optional[str] = None
    cliente_telefono: Optional[str] = None
    cliente_pec: Optional[str] = None
    cliente_indirizzo: str
    cliente_civico: str
    cliente_citta: str
    cliente_CAP: Optional[str] = None
    cliente_provincia: Optional[str] = None
    cliente_cellulare: Optional[str] = None
    
    utente_id: PositiveInt
    cliente_luogoNascita: str
    cliente_provinciaNascita:Optional[str] = None
    cliente_dataNascita: date
    cliente_cittadinanza: str
    cliente_tipoDocumento:str
    cliente_documento: str
    cliente_comuneRilascio: str
    cliente_dataRilascio: date
    cliente_dataScadenzaDocumento: date
    cliente_sesso: str
    cliente_indirizzoDomicilio: Optional[str] = None
    cliente_civicoDomicilio: Optional[str] = None
    cliente_cittaDomicilio: Optional[str] = None
    cliente_CAPDomicilio: Optional[str] = None
    cliente_provinciaDomicilio: Optional[str] = None
    cliente_ruolo: int
    cliente_gg: Optional[int] = None
    attuatore_id: Optional[int] = None
    azienda_id: Optional[int] = None
    tessera_id: Optional[int] = None
    cliente_abilPraticheUniv: int
    cliente_pathCertificato: Optional[str] = None
    cliente_abilitazione_ecampus: int
    cliente_abilitazione_link_campus: int
    cliente_abilitazione_corsi_speciali: int
    cliente_abilitazione_a4u: int

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    cliente_id: int

    model_config = ConfigDict(from_attributes=True)
