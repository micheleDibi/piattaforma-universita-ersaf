from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DECIMAL, Date, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  # Adatta l'import al tuo progetto


# ==============================================================================
# SQLALCHEMY MODEL
# ==============================================================================
class PraticaConsulente(Base):
    __tablename__ = "pratiche_consulenti"

    pratica_consulente_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    pratica_consulente_numero: Mapped[str] = mapped_column(
        String(45), nullable=False
    )
    pratica_consulente_data: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    pratica_consulente_competenza: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(20, 8), nullable=True
    )
    listino_competenza_id: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0"), index=True
    )
    profilazione_id: Mapped[int] = mapped_column(Integer, nullable=False)
    profilazione_cliente_gg_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_stato_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_consulente_percentuale: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8), nullable=False
    )


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================
class PraticaConsulenteBase(BaseModel):
    pratica_consulente_numero: str = Field(..., max_length=45)
    pratica_consulente_data: date = Field(default=date(1999, 12, 31))
    pratica_consulente_competenza: Optional[Decimal] = Field(
        default=None, max_digits=20, decimal_places=8
    )
    listino_competenza_id: int = 0
    profilazione_id: int
    profilazione_cliente_gg_id: int
    pratica_stato_id: int
    pratica_consulente_percentuale: Decimal = Field(
        ..., max_digits=20, decimal_places=8
    )


class PraticaConsulenteCreate(PraticaConsulenteBase):
    pass


class PraticaConsulenteUpdate(BaseModel):
    pratica_consulente_numero: Optional[str] = Field(default=None, max_length=45)
    pratica_consulente_data: Optional[date] = None
    pratica_consulente_competenza: Optional[Decimal] = Field(
        default=None, max_digits=20, decimal_places=8
    )
    listino_competenza_id: Optional[int] = None
    profilazione_id: Optional[int] = None
    profilazione_cliente_gg_id: Optional[int] = None
    pratica_stato_id: Optional[int] = None
    pratica_consulente_percentuale: Optional[Decimal] = Field(
        default=None, max_digits=20, decimal_places=8
    )


class PraticaConsulenteResponse(PraticaConsulenteBase):
    pratica_consulente_id: int

    model_config = ConfigDict(from_attributes=True)