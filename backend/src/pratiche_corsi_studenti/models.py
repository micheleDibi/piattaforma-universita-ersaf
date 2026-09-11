from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base 


# SQLALCHEMY MODEL
class PraticaCorsoStudente(Base):
    __tablename__ = "pratiche_corsi_studenti"

    pratica_corso_studente_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    pratica_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    corso_studente_id: Mapped[int] = mapped_column(Integer, nullable=False)

    pratica_corso_studente_created_by: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_corso_studente_created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    pratica_corso_studente_updated_by: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_corso_studente_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )


# PYDANTIC SCHEMAS
class PraticaCorsoStudenteBase(BaseModel):
    pratica_id: int
    corso_studente_id: int


class PraticaCorsoStudenteCreate(PraticaCorsoStudenteBase):
    pratica_corso_studente_created_by: int


class PraticaCorsoStudenteUpdate(BaseModel):
    pratica_id: Optional[int] = None
    corso_studente_id: Optional[int] = None
    pratica_corso_studente_updated_by: int


class PraticaCorsoStudenteResponse(PraticaCorsoStudenteBase):
    pratica_corso_studente_id: int
    pratica_corso_studente_created_by: int
    pratica_corso_studente_created_at: Optional[datetime] = None
    pratica_corso_studente_updated_by: int
    pratica_corso_studente_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)