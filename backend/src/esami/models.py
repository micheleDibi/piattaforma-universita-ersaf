from datetime import date
from typing import Optional

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Esame(Base):
    """Un esame gia' sostenuto dichiarato dal cliente: serve al debito didattico residuo."""

    __tablename__ = "esami"

    esame_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    esame_ssd: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    esame_insegnamento: Mapped[str] = mapped_column(String(255), nullable=False)
    esame_cfu: Mapped[int] = mapped_column(Integer, nullable=False)
    esame_voto: Mapped[int] = mapped_column(Integer, nullable=False)
    esame_data: Mapped[date] = mapped_column(Date, nullable=False)
    esame_corsoDiLaurea: Mapped[str] = mapped_column(String(255), nullable=False)
    esame_ordinamento: Mapped[str] = mapped_column(String(255), nullable=False)
    esame_durata: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    esame_universita: Mapped[str] = mapped_column(String(255), nullable=False)
    # Come in universita: nel database non c'e' FOREIGN KEY verso clienti.
    cliente_id: Mapped[int] = mapped_column(Integer, nullable=False)
