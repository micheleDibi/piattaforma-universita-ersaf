from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from src.aziende.schemas import AziendaResponse
from src.ruolo.schemas import RuoloResponse
from src.utenti.schemas import UtenteResponse
from src.universita.schemas import UniversitaBase, UniversitaResponse
import enum


class SessoEnum(str, enum.Enum):
    UOMO = "uomo"
    DONNA = "donna"

    @classmethod
    def _missing_(cls, value):
        if value is None or str(value).strip() == "":
            return None
        val_str = str(value).strip().lower()
        if val_str in ["m", "uomo", "male"]:
            return cls.UOMO
        if val_str in ["f", "donna", "female"]:
            return cls.DONNA
        return None


class TipoDocumentoEnum(str, enum.Enum):
    CARTA_IDENTITA = "Carta d'identità"
    CARTA_IDENTITA_ALT = "Carta d'Identità"
    PASSAPORTO = "Passaporto"
    PATENTE = "Patente"
    ALTRO = "Altro"

    @classmethod
    def _missing_(cls, value):
        if value is None or str(value).strip() == "":
            return None
        # Gestione case-insensitive per allineare eventuali varianti nel DB
        for member in cls:
            if member.value.lower() == str(value).strip().lower():
                return member
        return cls.ALTRO


def _normalizza_enum(v, info):
    """Stringa vuota -> None, confronto senza maiuscole sui valori dell'enum.

    Era un metodo di ClienteBase: ClienteUpdate ne aveva bisogno e duplicarlo
    avrebbe ripetuto il difetto tipico di questo backend, la regola in due
    copie corretta in una.
    """
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None

    if isinstance(v, (TipoDocumentoEnum, SessoEnum)):
        return v

    atteso = (
        TipoDocumentoEnum
        if info.field_name == "cliente_tipoDocumento"
        else SessoEnum
    )
    testo = str(v).strip()
    for membro in atteso:
        if membro.value.lower() == testo.lower():
            return membro

    return v


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
    
    # Reso opzionale alla base poiché viene generato programmaticamente nel backend
    utente_id: Optional[int] = None
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
    cliente_ruolo: Optional[int] = 0
    cliente_gg: Optional[int] = None
    attuatore_id: Optional[int] = None
    azienda_id: Optional[int] = None
    tessera_id: Optional[int] = None
    cliente_abilPraticheUniv: Optional[int] = None
    cliente_pathCertificato: Optional[str] = None
    cliente_abilitazione_ecampus: Optional[int] = None
    cliente_abilitazione_link_campus: Optional[int] = None
    cliente_abilitazione_corsi_speciali: Optional[int] = None
    cliente_abilitazione_a4u: Optional[int] = None

    _valida_enum_vuoti = field_validator(
        "cliente_tipoDocumento", "cliente_sesso", mode="before"
    )(_normalizza_enum)

class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(UniversitaBase):
    """Aggiornamento parziale: tutti i campi opzionali, curriculum compreso.

    Il PUT riusava ClienteCreate con model_dump() senza exclude_unset, quindi
    ogni campo non inviato veniva riscritto con il default dello schema:
    utente_id tornava None su una colonna NOT NULL (500), cliente_ruolo tornava
    0 declassando un attuatore a utente semplice, e azienda_id, attuatore_id e
    tessera_id perdevano l'associazione senza dire nulla.

    I campi universita_* ci sono perche' il form li invia: prima il PUT
    validava contro ClienteCreate, che non li ha, Pydantic li scartava in
    silenzio e rispondeva 200. Il curriculum si poteva scrivere solo alla
    creazione, mai piu'.
    """

    model_config = ConfigDict(from_attributes=True)

    cliente_codice: Optional[str] = None
    cliente_nome: Optional[str] = None
    cliente_cognome: Optional[str] = None
    cliente_email: Optional[str] = None
    cliente_telefono: Optional[str] = None
    cliente_pec: Optional[str] = None
    cliente_indirizzo: Optional[str] = None
    cliente_civico: Optional[str] = None
    cliente_citta: Optional[str] = None
    cliente_CAP: Optional[str] = None
    cliente_provincia: Optional[str] = None
    cliente_cellulare: Optional[str] = None
    utente_id: Optional[int] = None
    cliente_luogoNascita: Optional[str] = None
    cliente_provinciaNascita: Optional[str] = None
    cliente_dataNascita: Optional[date] = None
    cliente_cittadinanza: Optional[str] = None
    cliente_tipoDocumento: Optional[TipoDocumentoEnum] = None
    cliente_documento: Optional[str] = None
    cliente_comuneRilascio: Optional[str] = None
    cliente_dataRilascio: Optional[date] = None
    cliente_dataScadenzaDocumento: Optional[date] = None
    cliente_sesso: Optional[SessoEnum] = None
    cliente_indirizzoDomicilio: Optional[str] = None
    cliente_civicoDomicilio: Optional[str] = None
    cliente_cittaDomicilio: Optional[str] = None
    cliente_CAPDomicilio: Optional[str] = None
    cliente_provinciaDomicilio: Optional[str] = None
    cliente_ruolo: Optional[int] = None
    cliente_gg: Optional[int] = None
    attuatore_id: Optional[int] = None
    azienda_id: Optional[int] = None
    tessera_id: Optional[int] = None
    cliente_abilPraticheUniv: Optional[int] = None
    cliente_pathCertificato: Optional[str] = None
    cliente_abilitazione_ecampus: Optional[int] = None
    cliente_abilitazione_link_campus: Optional[int] = None
    cliente_abilitazione_corsi_speciali: Optional[int] = None
    cliente_abilitazione_a4u: Optional[int] = None

    _valida_enum_vuoti = field_validator(
        "cliente_tipoDocumento", "cliente_sesso", mode="before"
    )(_normalizza_enum)


class ClienteResponse(ClienteBase):
    cliente_id: int
    azienda: Optional[AziendaResponse] = None
    ruolo: Optional[RuoloResponse] = None
    utente: Optional[UtenteResponse] = None


class ClienteDettaglioResponse(ClienteResponse):
    """Come ClienteResponse, piu' il curriculum formativo.

    Sta a parte perche' `curriculum` e' una relazione lazy: metterlo in
    ClienteResponse avrebbe aggiunto una query per riga all'elenco paginato.
    Qui si legge una riga sola.
    """

    curriculum: Optional[UniversitaResponse] = None


class ClienteConUtenteCreate(ClienteBase, UniversitaBase):
    # utente_id è già gestito come Optional in ClienteBase, non serve ridefinirlo
    utente_username: Optional[str] = None
    utente_password: Optional[str] = None
