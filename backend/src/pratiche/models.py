from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.dialects.mysql import LONGBLOB, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.database import Base
from src.clienti.models import Cliente
# ATTENZIONE percorsi da confermare: dedotti per analogia con src.clienti.models
# (clienti); src.listino_tipoCorso.models e src.nome_universita.models sono
# confermati perche' compaiono nei bottom-import del tuo listini_testa/models.py.
from src.utenti.models import Utente
from src.aziende.models import Azienda
from src.listini_testa.models import ListinoTestaDB
from src.listino_tipoCorso.models import ListinoTipoCorsoDB
from src.nome_universita.models import NomeUniversitaDB
from src.pratiche_stati.models import PraticaStato


class Pratica(Base):
    """Tabella centrale pratiche."""

    __tablename__ = "pratiche"

    pratica_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # DEFAULT '1999-12-31' nel database, come le date-placeholder di Cliente/PraticaRegistroMise.
    pratica_dataCreazione: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    pratica_annoAccademico: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    pratica_corso1_24CFU: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pratica_corso2_24CFU: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pratica_corso3_24CFU: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pratica_corso4_24CFU: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pratica_sedeErogazione: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # --- Relazione "principale" col corso (listini_testa) ---------------------
    listTesta_id: Mapped[int] = mapped_column(
        ForeignKey("listini_testa.listTesta_id"), nullable=False, server_default=text("1")
    )
    listTesta_corso2_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("listini_testa.listTesta_id"), nullable=True
    )
    listTesta_corso3_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("listini_testa.listTesta_id"), nullable=True
    )

    # --- Relazioni con clienti (3 ruoli diversi, stessa tabella) --------------
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clienti.cliente_id"), nullable=False, server_default=text("1")
    )
    cliente_emittente_aderente_id: Mapped[int] = mapped_column(
        ForeignKey("clienti.cliente_id"), nullable=False, server_default=text("1")
    )
    cliente_consulente_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("clienti.cliente_id"), nullable=True
    )

    pratica_numero: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    pratica_stato_id: Mapped[int] = mapped_column(
        ForeignKey("pratiche_stati.pratica_stato_id"), nullable=False, server_default=text("1")
    )

    pratica_firma: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)
    pratica_upload_1: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)
    pratica_upload_2: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)
    pratica_upload_3: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)
    pratica_upload_4: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)
    pratica_upload_5: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)

    nome_universita_id: Mapped[int] = mapped_column(
        ForeignKey("nome_universita.nome_universita_id"), nullable=False, server_default=text("1")
    )
    azienda_id: Mapped[Optional[int]] = mapped_column(ForeignKey("aziende.azienda_id"), nullable=True)

    pratica_prezzo: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0.00000000")
    )
    pratica_forzeDellOrdine: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    pratica_missFlag_upload_1: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload_2: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload_3: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload_4: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload_5: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_dilazioni: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_firma: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_codiceASG: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    # Questo, a differenza dei fratelli 2-5, e' DEFAULT NULL nel database (non 0).
    pratica_missFlag_upload1_cliente: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pratica_missFlag_upload2_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload3_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload4_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload5_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_firma_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    pratica_pathFile: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pratica_rinnPrimoAnno: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_rinnSecondoAnno: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_rinnTerzoAnno: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    # --- Relazioni con utenti (4 ruoli diversi, stessa tabella) ---------------
    utente_id: Mapped[Optional[int]] = mapped_column(ForeignKey("utenti.utente_id"), nullable=True)
    utente_consulente_id: Mapped[Optional[int]] = mapped_column(ForeignKey("utenti.utente_id"), nullable=True)
    pratica_created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("utenti.utente_id"), nullable=True)
    pratica_updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("utenti.utente_id"), nullable=True)

    # DEFAULT NULL nel database: qui, come in Utente, valorizziamo comunque
    # lato applicazione per avere sempre data+ora di creazione/modifica.
    pratica_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    pratica_updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=text("CURRENT_TIMESTAMP")
    )

    listino_tipo_corso_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("listini_tipicorsi.listino_tipoCorso_id"), nullable=True
    )
    pratica_note: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True)
    pratica_pathFile_rateizzazione: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ---------------------------------------------------------------------
    # Relazioni "principali" (back_populates verso l'unica collezione gia'
    # dichiarata nei modelli esistenti: Cliente.pratiche, Utente.pratiche,
    # ListinoTestaDB.pratiche, Azienda.pratiche, PraticaStato.pratiche).
    # foreign_keys esplicito qui e' OBBLIGATORIO: essendoci piu' FK verso la
    # stessa tabella, senza specificarlo SQLAlchemy solleva
    # AmbiguousForeignKeysError in fase di configurazione dei mapper.
    # ---------------------------------------------------------------------
    cliente: Mapped["Cliente"] = relationship(
        "Cliente", foreign_keys=[cliente_id], back_populates="pratiche"
    )
    utente: Mapped[Optional["Utente"]] = relationship(
        "Utente", foreign_keys=[utente_id], back_populates="pratiche"
    )
    listino_testa: Mapped["ListinoTestaDB"] = relationship(
        "ListinoTestaDB", foreign_keys=[listTesta_id], back_populates="pratiche"
    )
    azienda: Mapped[Optional["Azienda"]] = relationship(
        "Azienda", foreign_keys=[azienda_id], back_populates="pratiche"
    )
    stato: Mapped["PraticaStato"] = relationship("PraticaStato", back_populates="pratiche")

    # ---------------------------------------------------------------------
    # Relazioni "secondarie": stessa tabella target, ma senza una collezione
    # dedicata dall'altra parte -> mono-direzionali (nessun back_populates).
    # ---------------------------------------------------------------------
    cliente_emittente_aderente: Mapped["Cliente"] = relationship(
        "Cliente", foreign_keys=[cliente_emittente_aderente_id]
    )
    cliente_consulente: Mapped[Optional["Cliente"]] = relationship(
        "Cliente", foreign_keys=[cliente_consulente_id]
    )
    corso2: Mapped[Optional["ListinoTestaDB"]] = relationship(
        "ListinoTestaDB", foreign_keys=[listTesta_corso2_id]
    )
    corso3: Mapped[Optional["ListinoTestaDB"]] = relationship(
        "ListinoTestaDB", foreign_keys=[listTesta_corso3_id]
    )
    utente_consulente: Mapped[Optional["Utente"]] = relationship(
        "Utente", foreign_keys=[utente_consulente_id]
    )
    creata_da: Mapped[Optional["Utente"]] = relationship("Utente", foreign_keys=[pratica_created_by])
    modificata_da: Mapped[Optional["Utente"]] = relationship("Utente", foreign_keys=[pratica_updated_by])
    universita: Mapped["NomeUniversitaDB"] = relationship(
        "NomeUniversitaDB", foreign_keys=[nome_universita_id], back_populates="pratiche"
    )
    tipo_corso: Mapped[Optional["ListinoTipoCorsoDB"]] = relationship(
        "ListinoTipoCorsoDB", foreign_keys=[listino_tipo_corso_id], back_populates="pratiche"
    )

    # --- Figlie dirette (una per cartella, back_populates definito su entrambi i lati) ---
    allegati: Mapped[List["PraticaAllegato"]] = relationship("PraticaAllegato", back_populates="pratica")
    corsi_studenti: Mapped[List["PraticaCorsoStudente"]] = relationship(
        "PraticaCorsoStudente", back_populates="pratica"
    )
    corsi_singoli: Mapped[List["PraticaCorsoSingolo"]] = relationship(
        "PraticaCorsoSingolo", back_populates="pratica"
    )
    listini: Mapped[List["PraticaListino"]] = relationship("PraticaListino", back_populates="pratica")
    storico_stati: Mapped[List["PraticaStatoStorico"]] = relationship(
        "PraticaStatoStorico", back_populates="pratica"
    )
    registro_mise: Mapped[Optional["PraticaRegistroMise"]] = relationship(
        "PraticaRegistroMise", back_populates="pratica", uselist=False
    )


# Bottom-import per registrare le classi figlie referenziate solo per stringa
# sopra (stesso pattern usato in src/listini_testa/models.py per "Pratica").
import src.pratiche_allegati.models  # noqa: E402,F401
import src.pratiche_corsi_studenti.models  # noqa: E402,F401
import src.pratiche_corsisingoli.models  # noqa: E402,F401
import src.pratiche_listini.models  # noqa: E402,F401
import src.pratiche_stati_storico.models  # noqa: E402,F401
import src.pratiche_registri_mise.models  # noqa: E402,F401


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

    # Campi piatti estratti dalle relazioni, per non costringere il frontend
    # a fare N+1 fetch solo per mostrare un nome invece di un id in tabella.
    # Popolati SOLO se il chiamante ha fatto joinedload/selectinload sulla
    # relazione corrispondente (altrimenti restano None, non sollevano errori:
    # niente lazy-load in un contesto async/di risposta gia' fuori sessione).
    cliente_nome_completo: Optional[str] = None
    pratica_stato_descrizione: Optional[str] = None
    listTesta_descrizione: Optional[str] = None

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

        return item_dict