from datetime import date, time
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DECIMAL, Date, Integer, String, Time, text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  # Adatta l'import al tuo progetto


# ==============================================================================
# SQLALCHEMY MODEL
# ==============================================================================
class PraticaGG(Base):
    __tablename__ = "pratiche_gg"

    pratica_gg_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    pratica_gg_dataCreazione: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    pratica_gg_dataFine: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    pratica_gg_dataErogazione: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    pratica_gg_orarioInizio: Mapped[time] = mapped_column(
        Time, nullable=False, server_default=text("'00:00:00'")
    )
    pratica_gg_orarioFine: Mapped[time] = mapped_column(
        Time, nullable=False, server_default=text("'00:00:00'")
    )
    pratica_gg_tipoPoliticaAttiva: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    pratica_gg_totaleOre: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8), nullable=False, server_default=text("'0.00000000'")
    )
    attuatore_id: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    cliente_id: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    operatore_id: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================
class PraticaGGBase(BaseModel):
    pratica_gg_dataCreazione: date = Field(default=date(1999, 12, 31))
    pratica_gg_dataFine: date = Field(default=date(1999, 12, 31))
    pratica_gg_dataErogazione: date = Field(default=date(1999, 12, 31))
    pratica_gg_orarioInizio: time = Field(default=time(0, 0, 0))
    pratica_gg_orarioFine: time = Field(default=time(0, 0, 0))
    pratica_gg_tipoPoliticaAttiva: str = Field(..., max_length=255)
    pratica_gg_totaleOre: Decimal = Field(
        default=Decimal("0.00000000"), max_digits=20, decimal_places=8
    )
    attuatore_id: int = 1
    cliente_id: int = 1
    operatore_id: int = 0


class PraticaGGCreate(PraticaGGBase):
    pass


class PraticaGGUpdate(BaseModel):
    pratica_gg_dataCreazione: Optional[date] = None
    pratica_gg_dataFine: Optional[date] = None
    pratica_gg_dataErogazione: Optional[date] = None
    pratica_gg_orarioInizio: Optional[time] = None
    pratica_gg_orarioFine: Optional[time] = None
    pratica_gg_tipoPoliticaAttiva: Optional[str] = Field(
        default=None, max_length=255
    )
    pratica_gg_totaleOre: Optional[Decimal] = Field(
        default=None, max_digits=20, decimal_places=8
    )
    attuatore_id: Optional[int] = None
    cliente_id: Optional[int] = None
    operatore_id: Optional[int] = None


class PraticaGGResponse(PraticaGGBase):
    pratica_gg_id: int

    model_config = ConfigDict(from_attributes=True)