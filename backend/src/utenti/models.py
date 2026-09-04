from sqlalchemy import Integer, String, Date, text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from src.database import Base 
from src.clienti.models import Cliente
from typing import Optional
import uuid

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
    utente_created_at: Mapped[date] = mapped_column(Date, default=date.today)
    utente_updated_by: Mapped[int] = mapped_column(Integer, nullable=False)
    utente_updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=text("CURRENT_TIMESTAMP"), default=datetime.now)
    utente_salt: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))

    # --- Migrazione 001: hashing delle password ------------------------------
    # Finche' utente_password_hash e' NULL, la verifica passa dalla colonna
    # legacy in chiaro. Il login converte la singola riga dell'utente che si
    # autentica (rehash pigro): nessuna operazione massiva, mai.
    #
    # ATTENZIONE: utente_password e' varchar(255) NOT NULL nel database, quindi
    # "svuotare il chiaro" significa scrivere '' e mai NULL.
    utente_password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # server_default e non default: cosi' l'INSERT non manda la colonna e il
    # DEFAULT del database — che le righe esistenti hanno gia' — resta l'unica
    # sorgente di verita'.
    utente_password_algo: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'legacy_plaintext'")
    )
    # Usato dalla query [B] della migrazione 004 come cut-off delle sessioni:
    # ogni sessione nata prima di questo istante e' da considerare revocata.
    # Per questo il rehash pigro NON lo tocca — un rehash non e' un cambio
    # password, e valorizzarlo invaliderebbe la sessione appena creata.
    utente_password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    utente_password_changed_via: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    # Relazione
    clienti: Mapped["Cliente"] = relationship(back_populates="utente", uselist=False, cascade="all, delete-orphan")