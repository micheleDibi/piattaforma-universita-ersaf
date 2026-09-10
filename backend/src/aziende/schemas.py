from pydantic import BaseModel, ConfigDict
from typing import Optional


class AziendaBase(BaseModel):
    """Obbligatorio qui = NOT NULL nel database.

    Prima non era cosi': CAP, provincia e partita IVA erano opzionali nello
    schema e NOT NULL nella tabella, quindi una richiesta che li ometteva
    passava la validazione e moriva in IntegrityError, cioe' 500 invece di 422.
    Il codice nazionale faceva il contrario: obbligatorio qui, DEFAULT NULL e
    vuoto su tutte e 205 le righe reali.

    azienda_logo non compare: e' un longblob e non ha senso in un JSON. Si
    aggiungera' un endpoint dedicato quando servira' davvero.
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
    pass


class AziendaUpdate(BaseModel):
    """Tutti i campi opzionali: un PUT parziale non deve azzerare il resto.

    Il PUT riusava AziendaCreate con model_dump() senza exclude_unset, quindi
    ogni campo non inviato veniva riscritto con il default dello schema. Su
    CAP, provincia, via, citta' e partita IVA - NOT NULL nel database - il
    risultato era un IntegrityError e un 500.
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


class AziendaResponse(AziendaBase):
    azienda_id: int
