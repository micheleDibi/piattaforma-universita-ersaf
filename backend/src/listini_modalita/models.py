from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from src.database import Base 


# Modello SQLAlchemy 
class ListinoModalitaDB(Base):
    __tablename__ = "listini_modalita"

    listino_modalita_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listino_modalita_codice: Mapped[str] = mapped_column(String(45), nullable=False)
    listino_modalita_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relazione inversa con listini_testa (opzionale se ti serve navigarla)
    listini_testa: Mapped[List["ListinoTestaDB"]] = relationship("ListinoTestaDB", back_populates="modalita")


# Schemi Pydantic 
class ListinoModalitaBase(BaseModel):
    listino_modalita_codice: str
    listino_modalita_descrizione: str

class ListinoModalitaCreate(ListinoModalitaBase):
    pass

class ListinoModalitaUpdate(BaseModel):
    listino_modalita_codice: Optional[str] = None
    listino_modalita_descrizione: Optional[str] = None

class ListinoModalita(ListinoModalitaBase):
    listino_modalita_id: int

    model_config = ConfigDict(from_attributes=True)