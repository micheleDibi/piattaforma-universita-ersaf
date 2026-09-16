from datetime import date
from datetime import date as date_
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field
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
        for member in cls:
            if member.value.lower() == str(value).strip().lower():
                return member
        return cls.ALTRO


def _normalizza_enum(v, info):
    """Stringa vuota -> None, confronto senza maiuscole sui valori dell'enum."""
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


def _valida_codice_fiscale(v):
    """Solo lunghezza. Usata SOLO negli schemi di scrittura (creazione e
    modifica): mai su ClienteResponse, altrimenti un CF gia' presente nel
    DB in formato non standard fa fallire la lettura di ogni cliente."""
    if v is None or v.strip() == "":
        return v
    v = v.strip().upper()
    if len(v) != 16:
        raise ValueError("Codice fiscale non valido: deve essere lungo 16 caratteri.")
    return v


def _valida_scadenza_documento(v):
    """Usata SOLO in scrittura, per lo stesso motivo: un documento gia'
    scaduto nel DB e' un dato storico legittimo da poter comunque leggere
    e mostrare, non un errore di validazione in lettura."""
    if v is not None and v < date_.today():
        raise ValueError("Il documento è scaduto: inserisci una data di scadenza valida.")
    return v


class ClienteBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cliente_codice: Optional[str] = None
    cliente_codice_fiscale: Optional[str] = None
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

    # Solo normalizzazione (stringa vuota -> None): innocua anche in lettura,
    # non solleva mai errori sui dati storici.
    _valida_enum_vuoti = field_validator(
        "cliente_tipoDocumento", "cliente_sesso", mode="before"
    )(_normalizza_enum)

    # NIENTE validator di CF e scadenza qui: ClienteResponse eredita da
    # questa classe e verrebbe rotta dai dati storici gia' presenti nel DB.


class ClienteCreate(ClienteBase):
    _valida_cf = field_validator("cliente_codice_fiscale")(_valida_codice_fiscale)
    _valida_scadenza = field_validator("cliente_dataScadenzaDocumento")(_valida_scadenza_documento)


class ClienteUpdate(UniversitaBase):
    """Aggiornamento parziale: tutti i campi opzionali, curriculum compreso."""

    model_config = ConfigDict(from_attributes=True)

    cliente_codice: Optional[str] = None
    cliente_codice_fiscale: Optional[str] = None
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

    # NIENTE validator di CF/scadenza qui: il frontend rimanda sempre tutti
    # i campi, quindi validarli qui bloccherebbe ogni modifica su un
    # cliente storico con documento gia' scaduto o CF malformato, anche
    # quando l'utente non ha toccato quei campi. Il controllo "e' cambiato
    # in peggio?" si fa nel router, confrontando col valore gia' salvato.
    _valida_enum_vuoti = field_validator(
        "cliente_tipoDocumento", "cliente_sesso", mode="before"
    )(_normalizza_enum)


class ClienteResponse(ClienteBase):
    cliente_id: int
    email_verificata: bool = False
    cellulare_verificato: bool = False
    azienda: Optional[AziendaResponse] = None
    ruolo: Optional[RuoloResponse] = None
    utente: Optional[UtenteResponse] = None


class ClienteDettaglioResponse(ClienteResponse):
    curriculum: Optional[UniversitaResponse] = None


class ClienteConUtenteCreate(ClienteBase, UniversitaBase):
    utente_username: Optional[str] = None
    utente_password: Optional[str] = None

    _valida_cf = field_validator("cliente_codice_fiscale")(_valida_codice_fiscale)
    _valida_scadenza = field_validator("cliente_dataScadenzaDocumento")(_valida_scadenza_documento)


class PermessiPraticheResponse(BaseModel):
    abilPraticheUniv: bool
    ecampus: bool
    link_campus: bool
    corsi_speciali: bool
    a4u: bool