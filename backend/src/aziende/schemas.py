from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


def _valida_partita_iva(v):
    valore = str(v or "").strip()
    if not valore:
        raise ValueError("La Partita IVA è obbligatoria.")
    if not valore.isdigit():
        raise ValueError("La Partita IVA deve contenere solo cifre.")
    if len(valore) != 11:
        raise ValueError("La Partita IVA deve essere di 11 cifre.")
    return valore


def _valida_codice_fiscale(v):
    valore = str(v or "").strip()
    if not valore:
        raise ValueError("Il Codice Fiscale è obbligatorio.")
    return valore


class AziendaBase(BaseModel):
    """Obbligatorio qui = NOT NULL nel database.

    Nessun validatore di Partita IVA/Codice Fiscale su questa classe: la
    eredita AziendaResponse, usata in lettura. Se il vincolo fosse qui, le
    righe gia' sporche nel database (P.IVA non conforme, CF vuoto) farebbero
    fallire la GET invece di essere semplicemente restituite cosi' come sono.
    Il vincolo vive solo su AziendaCreate e AziendaUpdate (scrittura).
    """

    model_config = ConfigDict(from_attributes=True)

    azienda_ragione_sociale: str
    azienda_partitaIVA: str
    azienda_via: str
    azienda_citta: str
    azienda_CAP: str
    azienda_provincia: str

    azienda_codiceFiscale: Optional[str] = None
    azienda_fatturazioneSDI: Optional[str] = None
    azienda_civico: Optional[str] = None
    azienda_sitoWeb: Optional[str] = None
    azienda_email: Optional[str] = None
    azienda_telefono: Optional[str] = None
    azienda_pec: Optional[str] = None
    azienda_codice_nazionale: Optional[str] = None
    azienda_iban: Optional[str] = None
    azienda_codice_bic: Optional[str] = None


class AziendaCreate(AziendaBase):
    # Ora obbligatorio: prima era Optional[str] ereditato da AziendaBase.
    azienda_codiceFiscale: str

    _valida_piva = field_validator("azienda_partitaIVA")(_valida_partita_iva)
    _valida_cf = field_validator("azienda_codiceFiscale")(_valida_codice_fiscale)


class AziendaUpdate(BaseModel):
    """Tutti i campi opzionali: un PUT parziale non deve azzerare il resto.

    I validatori qui scattano SOLO se il campo e' presente nel payload (per
    via di exclude_unset lato router, un campo omesso non attiva mai un
    field_validator). Questo blocca chi prova a INVIARE esplicitamente una
    Partita IVA non conforme o un Codice Fiscale vuoto. Non basta pero' a
    coprire il caso "il campo non viene nemmeno inviato, ma il valore gia'
    salvato e' sporco": quel caso lo controlla il router, sullo stato finale
    dell'azienda dopo aver applicato le modifiche.
    """

    model_config = ConfigDict(from_attributes=True)

    azienda_ragione_sociale: Optional[str] = None
    azienda_partitaIVA: Optional[str] = None
    azienda_codiceFiscale: Optional[str] = None
    azienda_fatturazioneSDI: Optional[str] = None
    azienda_via: Optional[str] = None
    azienda_civico: Optional[str] = None
    azienda_citta: Optional[str] = None
    azienda_CAP: Optional[str] = None
    azienda_provincia: Optional[str] = None
    azienda_sitoWeb: Optional[str] = None
    azienda_email: Optional[str] = None
    azienda_telefono: Optional[str] = None
    azienda_pec: Optional[str] = None
    azienda_codice_nazionale: Optional[str] = None
    azienda_iban: Optional[str] = None
    azienda_codice_bic: Optional[str] = None

    _valida_piva = field_validator("azienda_partitaIVA")(_valida_partita_iva)
    _valida_cf = field_validator("azienda_codiceFiscale")(_valida_codice_fiscale)


class AziendaResponse(AziendaBase):
    azienda_id: int
    # Calcolate a runtime nel router (_annota_anomalie), non colonne del
    # database: elenco di stringhe leggibili, vuoto se l'azienda e' pulita.
    anomalie: list[str] = []



class AderenteDettaglioBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    universita_ecampus_lauree: int = 0
    universita_ecampus_master: int = 0
    universita_link_lauree: int = 0
    universita_link_master: int = 0
    universita_SSML_lauree: int = 0
    universita_SSML_master: int = 0
    universita_A4U_master: int = 0
    universita_A4U_perfezionamenti: int = 0


class AderenteDettaglioUpdate(AderenteDettaglioBase):
    pass


class AderenteDettaglioResponse(AderenteDettaglioBase):
    aderente_dettaglio_id: Optional[int] = None
    azienda_id: int