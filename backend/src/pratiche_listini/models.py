from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict, Field

from src.database import Base
from src.listini_testa.models import ListinoTestaDB
from src.utenti.models import Utente

if TYPE_CHECKING:
    from src.pratiche.models import Pratica


class PraticaListino(Base):
    __tablename__ = "pratiche_listini"

    pratiche_listini_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pratica_listini_prezzo: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8), nullable=True)
    listTesta_id: Mapped[int] = mapped_column(ForeignKey("listini_testa.listTesta_id"), nullable=False)
    pratica_id: Mapped[int] = mapped_column(ForeignKey("pratiche.pratica_id"), nullable=False)
    pratiche_listini_createdBy: Mapped[int] = mapped_column(ForeignKey("utenti.utente_id"), nullable=False)
    # NOT NULL nel db ma senza default: come utente_created_at, lo valorizziamo
    # lato applicazione. Qui e' DATE (confermato da describe), non DATETIME.
    pratiche_listini_createdAt: Mapped[date] = mapped_column(Date, default=date.today)
    pratiche_listini_updatedBy: Mapped[int] = mapped_column(ForeignKey("utenti.utente_id"), nullable=False)
    pratiche_listini_updatedAt: Mapped[date] = mapped_column(
        Date, default=date.today, onupdate=text("CURRENT_DATE")
    )

    pratica: Mapped["Pratica"] = relationship("Pratica", foreign_keys=[pratica_id], back_populates="listini")
    listino: Mapped["ListinoTestaDB"] = relationship("ListinoTestaDB", foreign_keys=[listTesta_id])


# ---------------------------------------------------------------------------
# Schemi Pydantic
# ---------------------------------------------------------------------------

# pratiche_listini

class PraticaListinoCreate(BaseModel):
    pratica_id: int
    listTesta_id: int
    pratica_listini_prezzo: Optional[Decimal] = None
    pratiche_listini_createdBy: int


class PraticaListinoResponse(BaseModel):
    pratiche_listini_id: int
    pratica_id: int
    listTesta_id: int
    pratica_listini_prezzo: Optional[Decimal] = None
    pratiche_listini_createdAt: date
    pratiche_listini_updatedAt: date

    model_config = ConfigDict(from_attributes=True)