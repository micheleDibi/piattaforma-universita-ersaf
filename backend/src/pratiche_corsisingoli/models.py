from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DECIMAL, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  


# SQLALCHEMY MODEL

class PraticaCorsoSingolo(Base):
    __tablename__ = "pratiche_corsisingoli"

    praCorSin_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    praCorSin_costoCorso1: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8), nullable=False, server_default=text("'0.00000000'")
    )
    praCorSin_costoCorso2: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8), nullable=False, server_default=text("'0.00000000'")
    )
    praCorSin_costoCorso3: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8), nullable=False, server_default=text("'0.00000000'")
    )
    praCorSin_costoCorso4: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8), nullable=False, server_default=text("'0.00000000'")
    )

    listTesta_corso1_id: Mapped[int] = mapped_column(Integer, nullable=False)
    listTesta_corso2_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    listTesta_corso3_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    listTesta_corso4_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    pratica_id: Mapped[int] = mapped_column(Integer, nullable=False)

    praCorSin_costoCorso5: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8), nullable=False, server_default=text("'0.00000000'")
    )
    listTesta_corso5_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    listTesta_corso6_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    praCorSin_costoCorso6: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8), nullable=False, server_default=text("'0.00000000'")
    )


# PYDANTIC SCHEMAS
class PraticaCorsoSingoloBase(BaseModel):
    praCorSin_costoCorso1: Decimal = Field(default=Decimal("0.00000000"))
    praCorSin_costoCorso2: Decimal = Field(default=Decimal("0.00000000"))
    praCorSin_costoCorso3: Decimal = Field(default=Decimal("0.00000000"))
    praCorSin_costoCorso4: Decimal = Field(default=Decimal("0.00000000"))

    listTesta_corso1_id: int
    listTesta_corso2_id: Optional[int] = None
    listTesta_corso3_id: Optional[int] = None
    listTesta_corso4_id: Optional[int] = None

    pratica_id: int

    praCorSin_costoCorso5: Decimal = Field(default=Decimal("0.00000000"))
    listTesta_corso5_id: Optional[int] = None
    listTesta_corso6_id: Optional[int] = None
    praCorSin_costoCorso6: Decimal = Field(default=Decimal("0.00000000"))


class PraticaCorsoSingoloCreate(PraticaCorsoSingoloBase):
    pass


class PraticaCorsoSingoloUpdate(BaseModel):
    praCorSin_costoCorso1: Optional[Decimal] = None
    praCorSin_costoCorso2: Optional[Decimal] = None
    praCorSin_costoCorso3: Optional[Decimal] = None
    praCorSin_costoCorso4: Optional[Decimal] = None

    listTesta_corso1_id: Optional[int] = None
    listTesta_corso2_id: Optional[int] = None
    listTesta_corso3_id: Optional[int] = None
    listTesta_corso4_id: Optional[int] = None

    pratica_id: Optional[int] = None

    praCorSin_costoCorso5: Optional[Decimal] = None
    listTesta_corso5_id: Optional[int] = None
    listTesta_corso6_id: Optional[int] = None
    praCorSin_costoCorso6: Optional[Decimal] = None


class PraticaCorsoSingoloResponse(PraticaCorsoSingoloBase):
    praCorSin_id: int

    model_config = ConfigDict(from_attributes=True)