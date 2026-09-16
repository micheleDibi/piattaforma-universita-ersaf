from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey
from src.database import Base
from typing import Optional
import datetime


class AziendaXCod(Base):
    """Gerarchia padre-figlio fra aziende (tabella reale `aziende_xcod`).

    Non e' una colonna su Azienda ma una tabella a parte: ogni riga e' UN
    arco padre->figlia. Un'azienda puo' comparire piu' volte come padre (N
    figli, una riga ciascuno) ma - solo per vincolo applicativo, non di
    database, dato che azienda_figlia_id non ha una UNIQUE - una sola volta
    come figlia. "Ogni azienda ha un padre" e' quindi una regola imposta dal
    backend (vedi servizi.py e aziende/router.py), non garantita dallo schema.

    azienda_xCod_codice non ha un uso noto ad oggi: mappato ma non
    utilizzato dalle regole di visibilita'.
    """

    __tablename__ = "aziende_xcod"

    azienda_xCod_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    azienda_xCod_codice: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    azienda_padre_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("aziende.azienda_id"), nullable=True)
    azienda_figlia_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("aziende.azienda_id"), nullable=True)
    # NOT NULL nel database: ogni arco deve avere un autore, anche quello
    # creato "in automatico" alla creazione di un'azienda.
    azienda_xCod_created_by: Mapped[int] = mapped_column(Integer, ForeignKey("utenti.utente_id"), nullable=False)
    azienda_xCod_created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    azienda_xCod_updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("utenti.utente_id"), nullable=False)
    azienda_xCod_updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)