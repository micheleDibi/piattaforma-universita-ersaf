from sqlalchemy import Integer, String, Date, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from src.database import Base 
from src.clienti.models import Cliente
from typing import Optional

class Utente(Base):
    __tablename__ = "utenti"

    utente_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    utente_username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    utente_password: Mapped[str] = mapped_column(String, index=True, nullable=False)
    utente_ultimo_login: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_TIMESTAMP"))
    utente_ultimo_logout: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_TIMESTAMP"))
    utente_padre: Mapped[int] = mapped_column(Integer, nullable=False)
    utente_attivoSN: Mapped[int] = mapped_column(Integer, default= -1)
    utente_created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    utente_created_at: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_TIMESTAMP"))
    utente_updated_by: Mapped[int] = mapped_column(Integer, nullable=False)
    utente_updated_at: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_TIMESTAMP"))
    utente_salt: Mapped[String] = mapped_column(String(36), nullable=False)

    # Relazione
    clienti: Mapped["Cliente"] = relationship(back_populates="utente", uselist=False, cascade="all, delete-orphan")