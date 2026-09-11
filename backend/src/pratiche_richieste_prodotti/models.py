from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  # Adatta l'import al tuo progetto


# ==============================================================================
# SQLALCHEMY MODEL
# ==============================================================================
class PraticaRichiestaProdotto(Base):
    __tablename__ = "pratiche_richieste_prodotti"

    praRicProd_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    praRicProd_createBy: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    praRicProd_createDate: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    praRicProd_updateBy: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    praRicProd_updateDate: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    listTesta_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    praRicCons_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, index=True
    )


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================
class PraticaRichiestaProdottoBase(BaseModel):
    listTesta_id: int
    praRicCons_id: int
    pratica_id: Optional[int] = None


class PraticaRichiestaProdottoCreate(PraticaRichiestaProdottoBase):
    praRicProd_createBy: int
    praRicProd_createDate: datetime
    praRicProd_updateBy: int
    praRicProd_updateDate: datetime


class PraticaRichiestaProdottoUpdate(BaseModel):
    listTesta_id: Optional[int] = None
    praRicCons_id: Optional[int] = None
    pratica_id: Optional[int] = None
    praRicProd_updateBy: int
    praRicProd_updateDate: datetime


class PraticaRichiestaProdottoResponse(PraticaRichiestaProdottoBase):
    praRicProd_id: int
    praRicProd_createBy: int
    praRicProd_createDate: datetime
    praRicProd_updateBy: int
    praRicProd_updateDate: datetime

    model_config = ConfigDict(from_attributes=True)