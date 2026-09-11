from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  


# ==============================================================================
# SQLALCHEMY MODEL
# ==============================================================================
class PraticaStatoStorico(Base):
    __tablename__ = "pratiche_stati_storico"

    pratica_stato_storico_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    pratica_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    pratica_stato_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )

    pratica_stato_storico_created_by: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_stato_storico_created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    pratica_stato_storico_updated_by: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_stato_storico_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================
class PraticaStatoStoricoBase(BaseModel):
    pratica_id: int
    pratica_stato_id: int


class PraticaStatoStoricoCreate(PraticaStatoStoricoBase):
    pratica_stato_storico_created_by: int


class PraticaStatoStoricoUpdate(BaseModel):
    pratica_id: Optional[int] = None
    pratica_stato_id: Optional[int] = None
    pratica_stato_storico_updated_by: int


class PraticaStatoStoricoResponse(PraticaStatoStoricoBase):
    pratica_stato_storico_id: int
    pratica_stato_storico_created_by: int
    pratica_stato_storico_created_at: Optional[datetime] = None
    pratica_stato_storico_updated_by: int
    pratica_stato_storico_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)