from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict, Field

from src.database import Base
from src.listini_testa.models import ListinoTestaDB

if TYPE_CHECKING:
    from src.pratiche.models import Pratica


class PraticaCorsoSingolo(Base):
    """Fino a 6 corsi singoli associati alla stessa pratica."""

    __tablename__ = "pratiche_corsisingoli"

    praCorSin_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    praCorSin_costoCorso1: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0.00000000")
    )
    praCorSin_costoCorso2: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0.00000000")
    )
    praCorSin_costoCorso3: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0.00000000")
    )
    praCorSin_costoCorso4: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0.00000000")
    )
    praCorSin_costoCorso5: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0.00000000")
    )
    praCorSin_costoCorso6: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0.00000000")
    )

    listTesta_corso1_id: Mapped[int] = mapped_column(ForeignKey("listini_testa.listTesta_id"), nullable=False)
    listTesta_corso2_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("listini_testa.listTesta_id"), nullable=True
    )
    listTesta_corso3_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("listini_testa.listTesta_id"), nullable=True
    )
    listTesta_corso4_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("listini_testa.listTesta_id"), nullable=True
    )
    listTesta_corso5_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("listini_testa.listTesta_id"), nullable=True
    )
    listTesta_corso6_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("listini_testa.listTesta_id"), nullable=True
    )

    pratica_id: Mapped[int] = mapped_column(ForeignKey("pratiche.pratica_id"), nullable=False)

    pratica: Mapped["Pratica"] = relationship(
        "Pratica", foreign_keys=[pratica_id], back_populates="corsi_singoli"
    )
    corso1: Mapped["ListinoTestaDB"] = relationship("ListinoTestaDB", foreign_keys=[listTesta_corso1_id])
    corso2: Mapped[Optional["ListinoTestaDB"]] = relationship(
        "ListinoTestaDB", foreign_keys=[listTesta_corso2_id]
    )
    corso3: Mapped[Optional["ListinoTestaDB"]] = relationship(
        "ListinoTestaDB", foreign_keys=[listTesta_corso3_id]
    )
    corso4: Mapped[Optional["ListinoTestaDB"]] = relationship(
        "ListinoTestaDB", foreign_keys=[listTesta_corso4_id]
    )
    corso5: Mapped[Optional["ListinoTestaDB"]] = relationship(
        "ListinoTestaDB", foreign_keys=[listTesta_corso5_id]
    )
    corso6: Mapped[Optional["ListinoTestaDB"]] = relationship(
        "ListinoTestaDB", foreign_keys=[listTesta_corso6_id]
    )


# ---------------------------------------------------------------------------
# Schemi Pydantic
# ---------------------------------------------------------------------------

# pratiche_corsisingoli

class PraticaCorsoSingoloBase(BaseModel):
    praCorSin_costoCorso1: Optional[Decimal] = None
    praCorSin_costoCorso2: Optional[Decimal] = None
    praCorSin_costoCorso3: Optional[Decimal] = None
    praCorSin_costoCorso4: Optional[Decimal] = None
    praCorSin_costoCorso5: Optional[Decimal] = None
    praCorSin_costoCorso6: Optional[Decimal] = None
    listTesta_corso2_id: Optional[int] = None
    listTesta_corso3_id: Optional[int] = None
    listTesta_corso4_id: Optional[int] = None
    listTesta_corso5_id: Optional[int] = None
    listTesta_corso6_id: Optional[int] = None


class PraticaCorsoSingoloCreate(PraticaCorsoSingoloBase):
    pratica_id: int
    listTesta_corso1_id: int  # NOT NULL senza default


class PraticaCorsoSingoloResponse(PraticaCorsoSingoloBase):
    praCorSin_id: int
    pratica_id: int
    listTesta_corso1_id: int

    model_config = ConfigDict(from_attributes=True)