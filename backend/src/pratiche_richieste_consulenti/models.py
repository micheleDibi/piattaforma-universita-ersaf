from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  



# SQLALCHEMY MODEL

class PraticaRichiestaConsulente(Base):
    __tablename__ = "pratiche_richieste_consulenti"

    praRicCons_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    praRicCons_createBy: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    praRicCons_createDate: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    praRicCons_updateBy: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    praRicCons_updateDate: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    praRicCons_nomeCliente: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    praRicCons_cognomeCliente: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    praRicCons_codiceFiscaleCliente: Mapped[str] = mapped_column(
        String(45), nullable=False
    )
    praRicCons_emailCliente: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    praRicCons_telefono: Mapped[str] = mapped_column(
        String(45), nullable=False
    )
    praRicCons_cellulare: Mapped[str] = mapped_column(
        String(45), nullable=False
    )

    cliente_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, index=True
    )
    azienda_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )



# PYDANTIC SCHEMAS

class PraticaRichiestaConsulenteBase(BaseModel):
    praRicCons_nomeCliente: str = Field(..., max_length=255)
    praRicCons_cognomeCliente: str = Field(..., max_length=255)
    praRicCons_codiceFiscaleCliente: str = Field(..., max_length=45)
    praRicCons_emailCliente: str = Field(..., max_length=255)
    praRicCons_telefono: str = Field(..., max_length=45)
    praRicCons_cellulare: str = Field(..., max_length=45)
    cliente_id: Optional[int] = None
    azienda_id: int


class PraticaRichiestaConsulenteCreate(PraticaRichiestaConsulenteBase):
    praRicCons_createBy: int
    praRicCons_createDate: datetime
    praRicCons_updateBy: int
    praRicCons_updateDate: datetime


class PraticaRichiestaConsulenteUpdate(BaseModel):
    praRicCons_nomeCliente: Optional[str] = Field(default=None, max_length=255)
    praRicCons_cognomeCliente: Optional[str] = Field(default=None, max_length=255)
    praRicCons_codiceFiscaleCliente: Optional[str] = Field(default=None, max_length=45)
    praRicCons_emailCliente: Optional[str] = Field(default=None, max_length=255)
    praRicCons_telefono: Optional[str] = Field(default=None, max_length=45)
    praRicCons_cellulare: Optional[str] = Field(default=None, max_length=45)
    cliente_id: Optional[int] = None
    azienda_id: Optional[int] = None
    praRicCons_updateBy: int
    praRicCons_updateDate: datetime


class PraticaRichiestaConsulenteResponse(PraticaRichiestaConsulenteBase):
    praRicCons_id: int
    praRicCons_createBy: int
    praRicCons_createDate: datetime
    praRicCons_updateBy: int
    praRicCons_updateDate: datetime

    model_config = ConfigDict(from_attributes=True)