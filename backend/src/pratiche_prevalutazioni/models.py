from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Date, Integer, LargeBinary, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  # Adatta l'import al tuo progetto



# SQLALCHEMY MODEL
class PraticaPrevalutazione(Base):
    __tablename__ = "pratiche_prevalutazioni"

    praticaPrev_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Campi BLOB (file binari)
    praticaPrev_allegato1: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )
    praticaPrev_allegato2: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )
    praticaPrev_firma: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )

    praticaPrev_data: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    praticaPrev_luogo: Mapped[str] = mapped_column(String(255), nullable=False)

    clienteEmittente_id: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    clienteDest_id: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )

    praticaPrev_inviata: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    praticaPrev_ecampus: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

    praticaPrev_risposta: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )
    praticaPrev_segnalazioni: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    praticaPrev_verificaRisposta: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    praticaPrev_pathFile: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    pratica_stato_id: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1"), index=True
    )
    nome_universita_id: Mapped[int] = mapped_column(Integer, nullable=False)



# PYDANTIC SCHEMAS
class PraticaPrevalutazioneBase(BaseModel):
    praticaPrev_data: date = Field(default=date(1999, 12, 31))
    praticaPrev_luogo: str = Field(..., max_length=255)

    clienteEmittente_id: int = 1
    clienteDest_id: int = 1

    praticaPrev_inviata: int = 0
    praticaPrev_ecampus: int = 0

    praticaPrev_segnalazioni: Optional[str] = Field(default=None, max_length=255)
    praticaPrev_verificaRisposta: int = 0
    praticaPrev_pathFile: Optional[str] = Field(default=None, max_length=255)

    pratica_stato_id: int = 1
    nome_universita_id: int


class PraticaPrevalutazioneCreate(PraticaPrevalutazioneBase):
    pass


class PraticaPrevalutazioneUpdate(BaseModel):
    praticaPrev_data: Optional[date] = None
    praticaPrev_luogo: Optional[str] = Field(default=None, max_length=255)

    clienteEmittente_id: Optional[int] = None
    clienteDest_id: Optional[int] = None

    praticaPrev_inviata: Optional[int] = None
    praticaPrev_ecampus: Optional[int] = None

    praticaPrev_segnalazioni: Optional[str] = Field(default=None, max_length=255)
    praticaPrev_verificaRisposta: Optional[int] = None
    praticaPrev_pathFile: Optional[str] = Field(default=None, max_length=255)

    pratica_stato_id: Optional[int] = None
    nome_universita_id: Optional[int] = None


class PraticaPrevalutazioneResponse(PraticaPrevalutazioneBase):
    praticaPrev_id: int

    model_config = ConfigDict(from_attributes=True)