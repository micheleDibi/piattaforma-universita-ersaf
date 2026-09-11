from pydantic import BaseModel, ConfigDict
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, TYPE_CHECKING
from src.database import Base

if TYPE_CHECKING:
    from src.listini_testa.models import ListinoTestaDB

# --- Modello SQLAlchemy ---
class NomeUniversitaDB(Base):
    __tablename__ = "nome_universita"  

    nome_universita_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nome_universita_codice: Mapped[str] = mapped_column(String(45), nullable=False)
    nome_universita_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)

    listini_testa: Mapped[List["ListinoTestaDB"]] = relationship("ListinoTestaDB", back_populates="universita")
    pratiche: Mapped[List["Pratica"]] = relationship("Pratica", back_populates="universita")

# --- Schemi Pydantic ---
class NomeUniversitaBase(BaseModel):
    nome_universita_codice: str
    nome_universita_descrizione: str

class NomeUniversitaCreate(NomeUniversitaBase):
    pass

class NomeUniversitaUpdate(BaseModel):
    nome_universita_codice: Optional[str] = None
    nome_universita_descrizione: Optional[str] = None

class NomeUniversitaRead(NomeUniversitaBase):
    nome_universita_id: int

    model_config = ConfigDict(from_attributes=True)