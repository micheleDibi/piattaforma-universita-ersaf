from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    DECIMAL,
    Date,
    DateTime,
    Integer,
    LargeBinary,
    String,
    Text,
    text,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base



# SQLALCHEMY MODELS
class Pratica(Base):
    __tablename__ = "pratiche"

    pratica_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pratica_dataCreazione: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("'1999-12-31'"))
    pratica_annoAccademico: Mapped[Optional[str]] = mapped_column(String(45))
    pratica_corso1_24CFU: Mapped[Optional[int]] = mapped_column(Integer)
    pratica_corso2_24CFU: Mapped[Optional[int]] = mapped_column(Integer)
    pratica_corso3_24CFU: Mapped[Optional[int]] = mapped_column(Integer)
    pratica_corso4_24CFU: Mapped[Optional[int]] = mapped_column(Integer)
    pratica_sedeErogazione: Mapped[Optional[str]] = mapped_column(String(255))
    #Relazione
    listTesta_id: Mapped[int] = mapped_column(Integer, ForeignKey("listini_testa.listTesta_id"), nullable=False, server_default=text("1"))
    #Relazione
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey("clienti.cliente_id"), nullable=False, server_default=text("1"))
    pratica_numero: Mapped[Optional[str]] = mapped_column(String(45))
    #Relazione
    pratica_stato_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("pratiche_stati.pratica_stato_id"), 
        nullable=False, 
        server_default=text("1")
    )
    cliente_emittente_aderente_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    pratica_firma: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    pratica_upload_1: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    pratica_upload_2: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    pratica_upload_3: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    pratica_upload_4: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    #Relazione
    nome_universita_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("nome_universita.nome_universita_id"), 
        nullable=False, 
        server_default=text("1")
    )
    listTesta_corso2_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    listTesta_corso3_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)

    #Relazione
    azienda_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("aziende.azienda_id"), 
        index=True, 
        nullable=True
    )
    pratica_prezzo: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False, server_default=text("'0.00000000'"))
    pratica_forzeDellOrdine: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload_1: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload_2: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload_3: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload_4: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_dilazioni: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_firma: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_codiceASG: Mapped[Optional[str]] = mapped_column(String(45))
    pratica_missFlag_upload1_cliente: Mapped[Optional[int]] = mapped_column(Integer)
    pratica_missFlag_upload2_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload3_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload4_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_firma_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    cliente_consulente_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    pratica_pathFile: Mapped[Optional[str]] = mapped_column(String(255))
    pratica_rinnPrimoAnno: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_rinnSecondoAnno: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_rinnTerzoAnno: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_upload_5: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    pratica_missFlag_upload_5: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_missFlag_upload5_cliente: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    #Relazione
    utente_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("utenti.utente_id"), 
        index=True, 
        nullable=True
    )
    utente_consulente_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    pratica_created_by: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    pratica_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    pratica_updated_by: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    pratica_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    #Relazione
    listino_tipo_corso_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("listini_tipicorsi.listino_tipoCorso_id"), 
        index=True, 
        nullable=True
    )
    pratica_note: Mapped[Optional[str]] = mapped_column(Text)
    pratica_pathFile_rateizzazione: Mapped[Optional[str]] = mapped_column(String(255))

    #Relazioni
    listino_testa: Mapped["ListinoTestaDB"] = relationship("ListinoTestaDB", back_populates="pratiche")
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="pratiche")
    stato: Mapped["PraticaStato"] = relationship("PraticaStato", back_populates="pratiche")
    universita: Mapped["NomeUniversitaDB"] = relationship("NomeUniversitaDB", back_populates="pratiche")
    azienda: Mapped[Optional["Azienda"]] = relationship("Azienda", back_populates="pratiche")
    utente: Mapped[Optional["Utente"]] = relationship("Utente", back_populates="pratiche")
    tipo_corso: Mapped[Optional["ListinoTipoCorsoDB"]] = relationship("ListinoTipoCorsoDB", back_populates="pratiche")


# PYDANTIC SCHEMAS
class PraticaBase(BaseModel):
    """Campi comuni a tutte le operazioni sui dati di Pratica."""
    pratica_dataCreazione: Optional[date] = None
    pratica_annoAccademico: Optional[str] = None
    pratica_corso1_24CFU: Optional[int] = None
    pratica_corso2_24CFU: Optional[int] = None
    pratica_corso3_24CFU: Optional[int] = None
    pratica_corso4_24CFU: Optional[int] = None
    pratica_sedeErogazione: Optional[str] = None
    listTesta_id: int = 1
    cliente_id: int = 1
    pratica_numero: Optional[str] = None
    pratica_stato_id: int = 1
    cliente_emittente_aderente_id: int = 1
    nome_universita_id: int = 1
    listTesta_corso2_id: Optional[int] = None
    listTesta_corso3_id: Optional[int] = None
    azienda_id: Optional[int] = None
    pratica_prezzo: Decimal = Decimal("0.00000000")
    pratica_forzeDellOrdine: int = 0
    pratica_missFlag_upload_1: int = 0
    pratica_missFlag_upload_2: int = 0
    pratica_missFlag_upload_3: int = 0
    pratica_missFlag_upload_4: int = 0
    pratica_missFlag_dilazioni: int = 0
    pratica_missFlag_firma: int = 0
    pratica_codiceASG: Optional[str] = None
    pratica_missFlag_upload1_cliente: Optional[int] = None
    pratica_missFlag_upload2_cliente: int = 0
    pratica_missFlag_upload3_cliente: int = 0
    pratica_missFlag_upload4_cliente: int = 0
    pratica_missFlag_firma_cliente: int = 0
    cliente_consulente_id: Optional[int] = None
    pratica_pathFile: Optional[str] = None
    pratica_rinnPrimoAnno: int = 0
    pratica_rinnSecondoAnno: int = 0
    pratica_rinnTerzoAnno: int = 0
    pratica_missFlag_upload_5: int = 0
    pratica_missFlag_upload5_cliente: int = 0
    utente_id: Optional[int] = None
    utente_consulente_id: Optional[int] = None
    listino_tipo_corso_id: Optional[int] = None
    pratica_note: Optional[str] = None
    pratica_pathFile_rateizzazione: Optional[str] = None


class PraticaCreate(PraticaBase):
    """Schema per la creazione di una nuova pratica."""
    pratica_created_by: Optional[int] = None


class PraticaUpdate(BaseModel):
    """Schema per la modifica parziale di una pratica (tutti i campi opzionali)."""
    pratica_dataCreazione: Optional[date] = None
    pratica_annoAccademico: Optional[str] = None
    pratica_corso1_24CFU: Optional[int] = None
    pratica_corso2_24CFU: Optional[int] = None
    pratica_corso3_24CFU: Optional[int] = None
    pratica_corso4_24CFU: Optional[int] = None
    pratica_sedeErogazione: Optional[str] = None
    listTesta_id: Optional[int] = None
    cliente_id: Optional[int] = None
    pratica_numero: Optional[str] = None
    pratica_stato_id: Optional[int] = None
    cliente_emittente_aderente_id: Optional[int] = None
    nome_universita_id: Optional[int] = None
    listTesta_corso2_id: Optional[int] = None
    listTesta_corso3_id: Optional[int] = None
    azienda_id: Optional[int] = None
    pratica_prezzo: Optional[Decimal] = None
    pratica_forzeDellOrdine: Optional[int] = None
    pratica_missFlag_upload_1: Optional[int] = None
    pratica_missFlag_upload_2: Optional[int] = None
    pratica_missFlag_upload_3: Optional[int] = None
    pratica_missFlag_upload_4: Optional[int] = None
    pratica_missFlag_dilazioni: Optional[int] = None
    pratica_missFlag_firma: Optional[int] = None
    pratica_codiceASG: Optional[str] = None
    pratica_missFlag_upload1_cliente: Optional[int] = None
    pratica_missFlag_upload2_cliente: Optional[int] = None
    pratica_missFlag_upload3_cliente: Optional[int] = None
    pratica_missFlag_upload4_cliente: Optional[int] = None
    pratica_missFlag_firma_cliente: Optional[int] = None
    cliente_consulente_id: Optional[int] = None
    pratica_pathFile: Optional[str] = None
    pratica_rinnPrimoAnno: Optional[int] = None
    pratica_rinnSecondoAnno: Optional[int] = None
    pratica_rinnTerzoAnno: Optional[int] = None
    pratica_missFlag_upload_5: Optional[int] = None
    pratica_missFlag_upload5_cliente: Optional[int] = None
    utente_id: Optional[int] = None
    utente_consulente_id: Optional[int] = None
    pratica_updated_by: Optional[int] = None
    listino_tipo_corso_id: Optional[int] = None
    pratica_note: Optional[str] = None
    pratica_pathFile_rateizzazione: Optional[str] = None


class PraticaResponse(PraticaBase):
    
    pratica_id: int
    pratica_created_by: Optional[int] = None
    pratica_created_at: Optional[datetime] = None
    pratica_updated_by: Optional[int] = None
    pratica_updated_at: Optional[datetime] = None

    # Abilita la conversione automatica da oggetti SQLAlchemy ORM
    model_config = ConfigDict(from_attributes=True)