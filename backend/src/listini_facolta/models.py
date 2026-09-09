from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from src.database import Base 


# Modello SQLAlchemy 
class ListinoFacoltaDB(Base):
    __tablename__ = "listini_facolta"

    listino_facolta_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listino_facolta_codice: Mapped[str] = mapped_column(String(45), nullable=False)
    listino_facolta_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relazione inversa con listini_testa
    listini_testa: Mapped[List["ListinoTestaDB"]] = relationship("ListinoTestaDB", back_populates="facolta")


# Schemi Pydantic 
class ListinoFacoltaBase(BaseModel):
    listino_facolta_codice: str
    listino_facolta_descrizione: str

class ListinoFacoltaCreate(ListinoFacoltaBase):
    pass

class ListinoFacoltaUpdate(BaseModel):
    listino_facolta_codice: Optional[str] = None
    listino_facolta_descrizione: Optional[str] = None

class ListinoFacolta(ListinoFacoltaBase):
    listino_facolta_id: int

    model_config = ConfigDict(from_attributes=True)