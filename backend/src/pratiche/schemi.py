"""Contratti HTTP della pratica, separati dalla mappatura del database."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.comune.flag_legacy import a_flag_legacy
from src.pratiche.rinnovi import CAMPI_RINNOVO, verifica_rinnovo

# ---------------------------------------------------------------------------
# Schemi Pydantic
# ---------------------------------------------------------------------------

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

    # Solo normalizzazione (sicura anche in lettura): il controllo "un solo
    # anno alla volta" sta invece su PraticaCreate/PraticaUpdate, non qui, per
    # non rischiare di bloccare la GET di una pratica che avesse gia' un dato
    # storico incoerente su questi campi.
    @field_validator(*CAMPI_RINNOVO, mode="before")
    @classmethod
    def _normalizza_flag_rinnovo(cls, v):
        return a_flag_legacy(v)


class CorsoSingoloSelezionato(BaseModel):
    """Un corso scelto per una pratica di tipo Corsi Singoli (vedi crea_pratica
    in routers.py): diventa una riga in pratiche_listini. Il prezzo arriva dal
    client gia' calcolato (il dettaglio del listino valido oggi, la stessa
    regola di pratica_prezzo per le altre pratiche: vedi dettaglioAttuale in
    frontend/src/lib/praticaForm.js), il server non lo ricalcola."""

    listTesta_id: int
    prezzo: Optional[Decimal] = None


class PraticaCreate(PraticaBase):
    """I campi qui sotto NON hanno default a db ne' server_default: vanno sempre forniti.

    Upload/firma (blob) si gestiscono via endpoint dedicati, non in questo payload.
    """

    # Solo per una pratica di tipo Corsi Singoli: TUTTI i corsi scelti,
    # compreso il primo (che il router copia anche in listTesta_id, come per
    # ogni altra pratica: e' la riga "principale" della pratica). Assente per
    # tutti gli altri tipi di corso. Non e' un campo di PraticaUpdate: dopo la
    # creazione l'elenco dei corsi non si modifica piu' da qui.
    corsi_singoli: Optional[List[CorsoSingoloSelezionato]] = None

    @model_validator(mode="after")
    def _valida_rinnovo_singolo(self):
        verifica_rinnovo({campo: getattr(self, campo) for campo in CAMPI_RINNOVO})
        return self


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
    pratica_rinnPrimoAnno: Optional[int] = None
    pratica_rinnSecondoAnno: Optional[int] = None
    pratica_rinnTerzoAnno: Optional[int] = None

    @field_validator(*CAMPI_RINNOVO, mode="before")
    @classmethod
    def _normalizza_flag_rinnovo(cls, v):
        return a_flag_legacy(v)

    @model_validator(mode="after")
    def _valida_rinnovo_singolo(self):
        verifica_rinnovo({campo: getattr(self, campo) for campo in CAMPI_RINNOVO})
        return self


class EmittenteBreve(BaseModel):
    """I dati dell'aderente emittente che servono alla scheda pratica.

    Stanno nella risposta della pratica perche' la scheda deve mostrare
    l'emittente anche quando non e' fra i clienti che l'utente vede: prima il
    frontend lo chiedeva a GET /clienti/{id}, che con il filtro di visibilita'
    risponderebbe 404 e farebbe fallire l'intera scheda. Oggetto annidato e non
    campi piatti: `cliente_id` di primo livello e' lo studente.
    """

    cliente_id: int
    cliente_nome: Optional[str] = None
    cliente_cognome: Optional[str] = None
    cliente_codice: Optional[str] = None


class PraticaResponse(PraticaBase):
    pratica_id: int
    pratica_created_at: Optional[datetime] = None
    pratica_updated_at: Optional[datetime] = None

    # Campi piatti estratti dalle relazioni, per non costringere il frontend
    # a fare N+1 fetch solo per mostrare un nome invece di un id in tabella.
    # Popolati SOLO se il chiamante ha fatto joinedload/selectinload sulla
    # relazione corrispondente (altrimenti restano None, non sollevano errori:
    # niente lazy-load in un contesto async/di risposta gia' fuori sessione).
    cliente_nome_completo: Optional[str] = None
    pratica_stato_descrizione: Optional[str] = None
    listTesta_descrizione: Optional[str] = None
    nome_universita_descrizione: Optional[str] = None
    listino_tipoCorso_descrizione: Optional[str] = None
    emittente: Optional[EmittenteBreve] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def estrai_relazioni(cls, data):
        if isinstance(data, dict):
            return data

        item_dict = {campo: getattr(data, campo, None) for campo in data.__table__.columns.keys()}

        cliente_obj = getattr(data, "cliente", None)
        if cliente_obj:
            item_dict["cliente_nome_completo"] = f"{cliente_obj.cliente_nome} {cliente_obj.cliente_cognome}"

        stato_obj = getattr(data, "stato", None)
        if stato_obj:
            item_dict["pratica_stato_descrizione"] = stato_obj.pratica_stato_descrizione

        listino_obj = getattr(data, "listino_testa", None)
        if listino_obj:
            item_dict["listTesta_descrizione"] = listino_obj.listTesta_descrizione

        universita_obj = getattr(data, "universita", None)
        if universita_obj:
            item_dict["nome_universita_descrizione"] = universita_obj.nome_universita_descrizione

        tipo_corso_obj = getattr(data, "tipo_corso", None)
        if tipo_corso_obj:
            item_dict["listino_tipoCorso_descrizione"] = tipo_corso_obj.listino_tipoCorso_descrizione

        emittente_obj = getattr(data, "cliente_emittente_aderente", None)
        if emittente_obj:
            item_dict["emittente"] = {
                "cliente_id": emittente_obj.cliente_id,
                "cliente_nome": emittente_obj.cliente_nome,
                "cliente_cognome": emittente_obj.cliente_cognome,
                "cliente_codice": emittente_obj.cliente_codice,
            }

        return item_dict


class ConteggioPratiche(BaseModel):
    """Quante pratiche visibili hanno una data universita', tipo di corso e stato.

    Una riga per combinazione presente: le combinazioni senza pratiche non ci
    sono. Il tipo di corso e' None per le pratiche create da un percorso senza.
    """

    nome_universita_id: int
    listino_tipo_corso_id: Optional[int] = None
    pratica_stato_id: int
    totale: int
