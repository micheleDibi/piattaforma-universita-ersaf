from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DECIMAL, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  # Adatta l'import al tuo progetto



# SQLALCHEMY MODEL
class PraticaListino(Base):
    __tablename__ = "pratiche_listini"

    pratiche_listini_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    pratica_listini_prezzo: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(20, 8), nullable=True
    )
    listTesta_id: Mapped[int] = mapped_column(Integer, nullable=False)
    pratica_id: Mapped[int] = mapped_column(Integer, nullable=False)

    pratiche_listini_createdBy: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    pratiche_listini_createdAt: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    pratiche_listini_updatedBy: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    pratiche_listini_updatedAt: Mapped[date] = mapped_column(
        Date, nullable=False
    )


# PYDANTIC SCHEMAS
class PraticaListinoBase(BaseModel):
    pratica_listini_prezzo: Optional[Decimal] = Field(
        default=None, max_digits=20, decimal_places=8
    )
    listTesta_id: int
    pratica_id: int


class PraticaListinoCreate(PraticaListinoBase):
    pratiche_listini_createdBy: int
    pratiche_listini_createdAt: date


class PraticaListinoUpdate(BaseModel):
    pratica_listini_prezzo: Optional[Decimal] = Field(
        default=None, max_digits=20, decimal_places=8
    )
    listTesta_id: Optional[int] = None
    pratica_id: Optional[int] = None
    pratiche_listini_updatedBy: int
    pratiche_listini_updatedAt: date


class PraticaListinoResponse(PraticaListinoBase):
    pratiche_listini_id: int
    pratiche_listini_createdBy: int
    pratiche_listini_createdAt: date
    pratiche_listini_updatedBy: int
    pratiche_listini_updatedAt: date

    model_config = ConfigDict(from_attributes=True)