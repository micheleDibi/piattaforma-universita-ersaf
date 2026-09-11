from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from src.database import Base
from src.pratiche_stati.models import PraticaStato
from src.utenti.models import Utente

if TYPE_CHECKING:
    from src.pratiche.models import Pratica


class PraticaStatoStorico(Base):
    """Storico dei cambi di stato di una pratica (distinto dalla lookup pratiche_stati)."""

    __tablename__ = "pratiche_stati_storico"

    pratica_stato_storico_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pratica_id: Mapped[int] = mapped_column(ForeignKey("pratiche.pratica_id"), nullable=False)
    pratica_stato_id: Mapped[int] = mapped_column(
        ForeignKey("pratiche_stati.pratica_stato_id"), nullable=False
    )
    pratica_stato_storico_created_by: Mapped[int] = mapped_column(
        ForeignKey("utenti.utente_id"), nullable=False
    )
    pratica_stato_storico_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    pratica_stato_storico_updated_by: Mapped[int] = mapped_column(
        ForeignKey("utenti.utente_id"), nullable=False
    )
    pratica_stato_storico_updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=text("CURRENT_TIMESTAMP")
    )

    pratica: Mapped["Pratica"] = relationship(
        "Pratica", foreign_keys=[pratica_id], back_populates="storico_stati"
    )
    stato: Mapped["PraticaStato"] = relationship("PraticaStato", foreign_keys=[pratica_stato_id])


# ---------------------------------------------------------------------------
# Schemi Pydantic
# ---------------------------------------------------------------------------

# pratiche_stati_storico

class PraticaStatoStoricoCreate(BaseModel):
    pratica_id: int
    pratica_stato_id: int
    pratica_stato_storico_created_by: int


class PraticaStatoStoricoResponse(BaseModel):
    pratica_stato_storico_id: int
    pratica_id: int
    pratica_stato_id: int
    pratica_stato_storico_created_at: Optional[datetime] = None
    pratica_stato_storico_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)