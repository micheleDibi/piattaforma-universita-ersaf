from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict, Field

from src.database import Base
from src.utenti.models import Utente

if TYPE_CHECKING:
    from src.pratiche.models import Pratica


class PraticaCorsoStudente(Base):
    __tablename__ = "pratiche_corsi_studenti"

    pratica_corso_studente_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pratica_id: Mapped[int] = mapped_column(ForeignKey("pratiche.pratica_id"), nullable=False)
    corso_studente_id: Mapped[int] = mapped_column(Integer, nullable=False)
    pratica_corso_studente_created_by: Mapped[int] = mapped_column(
        ForeignKey("utenti.utente_id"), nullable=False
    )
    pratica_corso_studente_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    pratica_corso_studente_updated_by: Mapped[int] = mapped_column(
        ForeignKey("utenti.utente_id"), nullable=False
    )
    pratica_corso_studente_updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=text("CURRENT_TIMESTAMP")
    )

    pratica: Mapped["Pratica"] = relationship(
        "Pratica", foreign_keys=[pratica_id], back_populates="corsi_studenti"
    )


# ---------------------------------------------------------------------------
# Schemi Pydantic
# ---------------------------------------------------------------------------

# pratiche_corsi_studenti

class PraticaCorsoStudenteCreate(BaseModel):
    pratica_id: int
    corso_studente_id: int
    pratica_corso_studente_created_by: int


class PraticaCorsoStudenteResponse(BaseModel):
    pratica_corso_studente_id: int
    pratica_id: int
    corso_studente_id: int
    pratica_corso_studente_created_at: Optional[datetime] = None
    pratica_corso_studente_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)