import re
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


# =============================================================================
# Codice Fiscale: struttura (con omocodia) + carattere di controllo ufficiale
# =============================================================================
_CF_PATTERN = re.compile(
    r"^[A-Z]{6}[0-9A-Z]{2}[A-EHLMPR-T][0-9A-Z]{2}[A-Z][0-9A-Z]{3}[A-Z]$"
)

_CF_DISPARI = {
    "0": 1, "1": 0, "2": 5, "3": 7, "4": 9, "5": 13, "6": 15, "7": 17, "8": 19, "9": 21,
    "A": 1, "B": 0, "C": 5, "D": 7, "E": 9, "F": 13, "G": 15, "H": 17, "I": 19, "J": 21,
    "K": 2, "L": 4, "M": 18, "N": 20, "O": 11, "P": 3, "Q": 6, "R": 8, "S": 12, "T": 14,
    "U": 16, "V": 10, "W": 22, "X": 25, "Y": 24, "Z": 23,
}
_CF_PARI = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8, "J": 9,
    "K": 10, "L": 11, "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17, "S": 18, "T": 19,
    "U": 20, "V": 21, "W": 22, "X": 23, "Y": 24, "Z": 25,
}
_CF_RESTO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _valida_codice_fiscale(v):
    """Controllo completo, omocodia inclusa: struttura + ricalcolo del
    carattere di controllo con le tabelle ufficiali. Si assume cittadinanza
    italiana: nessuna gestione di codici fiscali esteri."""
    if v is None or v.strip() == "":
        return v
    v = v.strip().upper()

    if len(v) != 16:
        raise ValueError("Codice fiscale non valido: deve essere lungo 16 caratteri.")

    if not _CF_PATTERN.match(v):
        raise ValueError("Codice fiscale non valido: formato non conforme.")

    somma = 0
    for i, carattere in enumerate(v[:15]):
        somma += _CF_DISPARI[carattere] if i % 2 == 0 else _CF_PARI[carattere]

    atteso = _CF_RESTO[somma % 26]
    if atteso != v[15]:
        raise ValueError("Codice fiscale non valido: carattere di controllo errato.")

    return v


def _valida_scadenza_documento(v):
    if v is not None and v < date_.today():
        raise ValueError("Il documento è scaduto: inserisci una data di scadenza valida.")
    return v


# =============================================================================
# Email: formato standard qualcosa@dominio.estensione
# =============================================================================
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _valida_email(v):
    if v is None or v.strip() == "":
        return v
    v = v.strip()
    if not _EMAIL_PATTERN.match(v):
        raise ValueError("Email non valida: formato non conforme.")
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
    # non solleva mai errori sui dati storici. NIENTE validator di CF,
    # scadenza o email qui: ClienteResponse eredita da questa classe e
    # verrebbe rotta dai dati storici gia' presenti nel DB.
    _valida_enum_vuoti = field_validator(
        "cliente_tipoDocumento", "cliente_sesso", mode="before"
    )(_normalizza_enum)


class ClienteCreate(ClienteBase):
    _valida_cf = field_validator("cliente_codice_fiscale")(_valida_codice_fiscale)
    _valida_scadenza = field_validator("cliente_dataScadenzaDocumento")(_valida_scadenza_documento)
    _valida_email = field_validator("cliente_email")(_valida_email)


class ClienteUpdate(UniversitaBase):
    """Aggiornamento parziale: tutti i campi opzionali, curriculum compreso.

    Niente validator di CF/scadenza/email a livello di schema: il frontend
    rimanda sempre tutti i campi del form, non solo quelli modificati.
    Validarli qui bloccherebbe ogni PUT su un cliente storico che ha gia'
    un CF o un'email non conformi ai nuovi controlli, anche quando
    l'operatore non ha toccato quei campi. Il controllo si fa nel router,
    confrontando col valore gia' salvato: un peggioramento nuovo si
    blocca, un dato storico invariato passa.
    """

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
    # Calcolate a runtime nel router (_annota_anomalie), non colonne del
    # database: elenco di stringhe leggibili, vuoto se il cliente e' pulito.
    anomalie: list[str] = []


class ClienteDettaglioResponse(ClienteResponse):
    """Come ClienteResponse, piu' il curriculum formativo.

    Sta a parte perche' `curriculum` e' una relazione lazy: metterlo in
    ClienteResponse avrebbe aggiunto una query per riga all'elenco paginato.
    Qui si legge una riga sola.
    """

    curriculum: Optional[UniversitaResponse] = None


class ClienteConUtenteCreate(ClienteBase, UniversitaBase):
    utente_username: Optional[str] = None
    utente_password: Optional[str] = None

    _valida_cf = field_validator("cliente_codice_fiscale")(_valida_codice_fiscale)
    _valida_scadenza = field_validator("cliente_dataScadenzaDocumento")(_valida_scadenza_documento)
    _valida_email = field_validator("cliente_email")(_valida_email)


class PermessiPraticheResponse(BaseModel):
    abilPraticheUniv: bool
    ecampus: bool
    link_campus: bool
    corsi_speciali: bool
    a4u: bool