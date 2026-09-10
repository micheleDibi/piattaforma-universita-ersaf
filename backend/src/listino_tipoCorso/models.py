from pydantic import BaseModel, ConfigDict
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from src.database import Base

if TYPE_CHECKING:
    from src.listini_testa.models import ListinoTestaDB

# Modello SQLAlchemy (Database)
class ListinoTipoCorsoDB(Base):
    __tablename__ = "listini_tipicorsi"  

    listino_tipoCorso_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listino_tipoCorso_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)

    listini_testa: Mapped[List["ListinoTestaDB"]] = relationship("ListinoTestaDB", back_populates="tipo_corso")

# Schemi Pydantic (FastAPI Validazione / Serializzazione)
class ListinoTipoCorsoBase(BaseModel):
    listino_tipoCorso_descrizione: str

class ListinoTipoCorsoCreate(ListinoTipoCorsoBase):
    pass

class ListinoTipoCorso(ListinoTipoCorsoBase):
    listino_tipoCorso_id: int

    model_config = ConfigDict(from_attributes=True)