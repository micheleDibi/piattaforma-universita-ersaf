from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Pratica
#
# NOTA rispetto allo stile di PraticaStatoBase: li' tutti i campi erano
# Optional anche se NOT NULL a db. Su pratiche ci sono pero' molte piu' colonne
# NOT NULL SENZA un default applicabile lato Pydantic (es. pratica_allegato_
# descrizione, corso_studente_id, ecc.): renderle tutte Optional lascerebbe
# passare la validazione per poi rompersi sull'insert con un IntegrityError,
# lo stesso problema gia' visto nei commenti di Cliente/Azienda. Qui quindi i
# campi NOT NULL senza default (ne' Python ne' server_default) restano
# obbligatori; Optional solo per le colonne davvero nullable o con default.

class PraticaBase(BaseModel):
    pratica_dataCreazione: Optional[date] = None  # ha server_default, ok Optional
    pratica_annoAccademico: Optional[str] = Field(default=None, max_length=45)
    pratica_corso1_24CFU: Optional[int] = None
    pratica_corso2_24CFU: Optional[int] = None
    pratica_corso3_24CFU: Optional[int] = None
    pratica_corso4_24CFU: Optional[int] = None
    pratica_sedeErogazione: Optional[str] = Field(default=None, max_length=255)

    listTesta_id: Optional[int] = None  # ha server_default=1
    listTesta_corso2_id: Optional[int] = None
    listTesta_corso3_id: Optional[int] = None

    cliente_id: Optional[int] = None  # ha server_default=1
    cliente_emittente_aderente_id: Optional[int] = None  # ha server_default=1
    cliente_consulente_id: Optional[int] = None

    pratica_numero: Optional[str] = Field(default=None, max_length=45)
    pratica_stato_id: Optional[int] = None  # ha server_default=1

    nome_universita_id: Optional[int] = None  # ha server_default=1
    azienda_id: Optional[int] = None

    pratica_prezzo: Optional[Decimal] = None  # ha server_default=0
    pratica_forzeDellOrdine: Optional[int] = None

    pratica_missFlag_upload_1: Optional[int] = None
    pratica_missFlag_upload_2: Optional[int] = None
    pratica_missFlag_upload_3: Optional[int] = None
    pratica_missFlag_upload_4: Optional[int] = None
    pratica_missFlag_upload_5: Optional[int] = None
    pratica_missFlag_dilazioni: Optional[int] = None
    pratica_missFlag_firma: Optional[int] = None
    pratica_codiceASG: Optional[str] = Field(default=None, max_length=45)
    pratica_missFlag_upload1_cliente: Optional[int] = None
    pratica_missFlag_upload2_cliente: Optional[int] = None
    pratica_missFlag_upload3_cliente: Optional[int] = None
    pratica_missFlag_upload4_cliente: Optional[int] = None
    pratica_missFlag_upload5_cliente: Optional[int] = None
    pratica_missFlag_firma_cliente: Optional[int] = None

    pratica_pathFile: Optional[str] = Field(default=None, max_length=255)
    pratica_rinnPrimoAnno: Optional[int] = None
    pratica_rinnSecondoAnno: Optional[int] = None
    pratica_rinnTerzoAnno: Optional[int] = None

    utente_id: Optional[int] = None
    utente_consulente_id: Optional[int] = None

    listino_tipo_corso_id: Optional[int] = None
    pratica_note: Optional[str] = None
    pratica_pathFile_rateizzazione: Optional[str] = Field(default=None, max_length=255)


class PraticaCreate(PraticaBase):
    """I campi qui sotto NON hanno default a db ne' server_default: vanno sempre forniti.

    Upload/firma (blob) si gestiscono via endpoint dedicati, non in questo payload.
    """

    pass


class PraticaUpdate(BaseModel):
    """Tutti opzionali: PATCH parziale."""

    pratica_annoAccademico: Optional[str] = Field(default=None, max_length=45)
    pratica_corso1_24CFU: Optional[int] = None
    pratica_corso2_24CFU: Optional[int] = None
    pratica_corso3_24CFU: Optional[int] = None
    pratica_corso4_24CFU: Optional[int] = None
    pratica_sedeErogazione: Optional[str] = Field(default=None, max_length=255)
    pratica_numero: Optional[str] = Field(default=None, max_length=45)
    pratica_stato_id: Optional[int] = None
    listTesta_corso2_id: Optional[int] = None
    listTesta_corso3_id: Optional[int] = None
    azienda_id: Optional[int] = None
    pratica_prezzo: Optional[Decimal] = None
    cliente_consulente_id: Optional[int] = None
    pratica_pathFile: Optional[str] = Field(default=None, max_length=255)
    utente_id: Optional[int] = None
    utente_consulente_id: Optional[int] = None
    listino_tipo_corso_id: Optional[int] = None
    pratica_note: Optional[str] = None
    pratica_pathFile_rateizzazione: Optional[str] = Field(default=None, max_length=255)


class PraticaResponse(PraticaBase):
    pratica_id: int
    pratica_created_at: Optional[datetime] = None
    pratica_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)