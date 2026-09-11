from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict, Field

from src.database import Base
from src.clienti.models import Cliente
from src.pratiche_stati.models import PraticaStato

if TYPE_CHECKING:
    from src.pratiche.models import Pratica


class PraticaRegistroMise(Base):
    """Estensione 1:1 di pratiche (registro MISE).

    pratica_id e' sia PK che FK verso pratiche.pratica_id. Nel database reale
    la colonna ha anche l'extra auto_increment, cosa che tecnicamente non ha
    senso per una FK: e' quasi certamente un residuo storico e l'applicazione
    scrive comunque un valore esplicito uguale a pratica_id. A livello ORM la
    modelliamo come chiave primaria + FK, senza autoincrement.
    """

    __tablename__ = "pratiche_registri_mise"

    pratica_id: Mapped[int] = mapped_column(ForeignKey("pratiche.pratica_id"), primary_key=True)
    pratica_data_inserimento: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    pratica_data_approvazione: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    pratica_data_scadenza: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )
    pratica_titolo_di_studio: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)
    pratica_cv: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)
    pratica_corsi_di_formazione: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, nullable=True)
    profilo_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    # DEFAULT 0 nel database (non un cliente reale): rispecchiato cosi' com'e'.
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clienti.cliente_id"), nullable=False, server_default=text("0")
    )
    pratica_aggiornamento: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    pratica_attestato: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pratica_stato_id: Mapped[int] = mapped_column(
        ForeignKey("pratiche_stati.pratica_stato_id"), nullable=False
    )
    pratica_nota: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pratica_codice: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    pratica: Mapped["Pratica"] = relationship(
        "Pratica", foreign_keys=[pratica_id], back_populates="registro_mise"
    )
    cliente: Mapped["Cliente"] = relationship("Cliente", foreign_keys=[cliente_id])
    stato: Mapped["PraticaStato"] = relationship("PraticaStato", foreign_keys=[pratica_stato_id])


# ---------------------------------------------------------------------------
# Schemi Pydantic
# ---------------------------------------------------------------------------

# pratiche_registri_mise (1:1 con pratiche)

class PraticaRegistroMiseBase(BaseModel):
    pratica_data_inserimento: Optional[date] = None
    pratica_data_approvazione: Optional[date] = None
    pratica_data_scadenza: Optional[date] = None
    profilo_id: Optional[int] = None
    pratica_aggiornamento: Optional[int] = None
    pratica_attestato: Optional[str] = Field(default=None, max_length=255)
    pratica_nota: Optional[str] = None
    pratica_codice: Optional[str] = Field(default=None, max_length=255)


class PraticaRegistroMiseCreate(PraticaRegistroMiseBase):
    pratica_id: int
    cliente_id: int
    pratica_stato_id: int


class PraticaRegistroMiseResponse(PraticaRegistroMiseBase):
    pratica_id: int
    cliente_id: int
    pratica_stato_id: int

    model_config = ConfigDict(from_attributes=True)