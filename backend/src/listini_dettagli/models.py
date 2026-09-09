from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import Date, DECIMAL, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field
from src.database import Base

# SQLALCHEMY MODEL
class ListinoDettaglio(Base):
    __tablename__ = "listini_dettagli"

    listDettaglio_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listTesta_id: Mapped[int] = mapped_column(Integer, ForeignKey("listini_testa.listTesta_id"), nullable=False)
    
    listDettaglio_dataInizioValidazione: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    listDettaglio_dataFineValidazionoe: Mapped[date] = mapped_column(Date, nullable=False, default=date(9999, 12, 31))
    listDettaglio_prezzo: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False, default=Decimal("0.00000000"))
    listDettaglio_durata: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listDettaglio_CFU: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listDettaglio_tasse: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)

    # ── AGGIUNTO: Relazione inversa verso la testa ──
    testa: Mapped["ListinoTestaDB"] = relationship("ListinoTestaDB", back_populates="dettagli")


# PYDANTIC SCHEMAS
class ListinoDettaglioBase(BaseModel):
    listDettaglio_dataInizioValidazione: Optional[date] = None
    listDettaglio_dataFineValidazionoe: date = Field(default=date(9999, 12, 31))
    listDettaglio_prezzo: Decimal = Field(..., ge=0)
    listDettaglio_durata: Optional[int] = None
    listDettaglio_CFU: Optional[int] = None
    listDettaglio_tasse: Optional[Decimal] = None

# Schema per creare dettagli inclusi nella richiesta della testa (non serve listTesta_id perché lo assegna SQLAlchemy in automatico)
class ListinoDettaglioCreateWithoutTestaId(ListinoDettaglioBase):
    pass

class ListinoDettaglioCreate(BaseModel):
    listDettaglio_dataInizioValidazione: Optional[date] = None
    listDettaglio_dataFineValidazionoe: Optional[str] = "9999-12-31"
    listDettaglio_prezzo: Optional[float] = 0.0
    listDettaglio_durata: Optional[int] = None
    listDettaglio_CFU: Optional[int] = None
    listDettaglio_tasse: Optional[float] = None
    
class ListinoDettaglioUpdate(BaseModel):
    listDettaglio_dataInizioValidazione: Optional[date] = None
    listDettaglio_dataFineValidazionoe: Optional[date] = None
    listDettaglio_prezzo: Optional[Decimal] = Field(None, ge=0)
    listDettaglio_durata: Optional[int] = None
    listDettaglio_CFU: Optional[int] = None
    listDettaglio_tasse: Optional[Decimal] = None

class ListinoDettaglioResponse(ListinoDettaglioBase):
    listDettaglio_id: int
    listTesta_id: int

    class Config:
        from_attributes = True