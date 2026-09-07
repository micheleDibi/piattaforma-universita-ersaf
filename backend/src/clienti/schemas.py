from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, PositiveInt, field_validator
from src.aziende.schemas import AziendaResponse
from src.ruolo.schemas import RuoloResponse
from src.clienti.models import SessoEnum, TipoDocumentoEnum

class ClienteBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
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
    cliente_provinciaNascita: Optional[str] = None
    cliente_dataNascita: date
    cliente_cittadinanza: str

    cliente_tipoDocumento: Optional[TipoDocumentoEnum] = None
    cliente_documento: str
    cliente_comuneRilascio: str
    cliente_dataRilascio: date
    cliente_dataScadenzaDocumento: date
    cliente_sesso: Optional[SessoEnum] = None
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

    @field_validator('cliente_tipoDocumento', 'cliente_sesso', mode='before')
    @classmethod
    def valida_enum_vuoti(cls, v, info):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        
        # Se riceve già un'istanza di un Enum, la restituisce
        if isinstance(v, (TipoDocumentoEnum, SessoEnum)):
            return v
            
        # Determina quale Enum mappare in base al campo in validazione
        target_enum = TipoDocumentoEnum if info.field_name == 'cliente_tipoDocumento' else SessoEnum
        
        # Cerca il membro corrispondente ignorando maiuscole/minuscole e spazi
        val_str = str(v).strip()
        for member in target_enum:
            if member.value.lower() == val_str.lower():
                return member
                
        # Fallback se non trova corrispondenza esatta
        return v

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    cliente_id: int
    azienda: Optional[AziendaResponse] = None
    ruolo: Optional[RuoloResponse] = None

class ClienteConUtenteCreate(ClienteBase):
    utente_id: Optional[int] = None
    utente_username: Optional[str] = None  
    utente_password: Optional[str] = None