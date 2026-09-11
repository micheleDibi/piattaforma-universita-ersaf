from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict, Field

from src.database import Base
from src.utenti.models import Utente

if TYPE_CHECKING:
    from src.pratiche.models import Pratica


class PraticaAllegato(Base):
    __tablename__ = "pratiche_allegati"

    pratica_allegato_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pratica_id: Mapped[int] = mapped_column(ForeignKey("pratiche.pratica_id"), nullable=False)
    pratica_allegato_pathfile: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pratica_allegato_nomefile: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pratica_allegato_checkfile: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_allegato_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)
    pratica_allegato_created_by: Mapped[int] = mapped_column(ForeignKey("utenti.utente_id"), nullable=False)
    pratica_allegato_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    pratica_allegato_updated_by: Mapped[int] = mapped_column(ForeignKey("utenti.utente_id"), nullable=False)
    pratica_allegato_updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=text("CURRENT_TIMESTAMP")
    )

    pratica: Mapped["Pratica"] = relationship("Pratica", foreign_keys=[pratica_id], back_populates="allegati")


# ---------------------------------------------------------------------------
# Schemi Pydantic
# ---------------------------------------------------------------------------

# pratiche_allegati

class PraticaAllegatoBase(BaseModel):
    pratica_allegato_pathfile: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_nomefile: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_checkfile: Optional[int] = None
    pratica_allegato_descrizione: str = Field(max_length=255)  # NOT NULL senza default


class PraticaAllegatoCreate(PraticaAllegatoBase):
    pratica_id: int
    pratica_allegato_created_by: int


class PraticaAllegatoUpdate(BaseModel):
    pratica_allegato_pathfile: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_nomefile: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_checkfile: Optional[int] = None
    pratica_allegato_descrizione: Optional[str] = Field(default=None, max_length=255)


class PraticaAllegatoResponse(PraticaAllegatoBase):
    pratica_allegato_id: int
    pratica_id: int
    pratica_allegato_created_at: Optional[datetime] = None
    pratica_allegato_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)