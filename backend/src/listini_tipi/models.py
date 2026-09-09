from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from src.database import Base 

# Modello SQLAlchemy 
class ListinoTipoDB(Base):
    __tablename__ = "listini_tipi"

    listino_tipo_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listino_tipo_codice: Mapped[str] = mapped_column(String(45), nullable=False)
    listino_tipo_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relazione inversa con listini_testa (opzionale)
    listini_testa: Mapped[List["ListinoTestaDB"]] = relationship("ListinoTestaDB", back_populates="tipo")


# Schemi Pydantic 
class ListinoTipoBase(BaseModel):
    listino_tipo_codice: str
    listino_tipo_descrizione: str

class ListinoTipoCreate(ListinoTipoBase):
    pass

class ListinoTipoUpdate(BaseModel):
    listino_tipo_codice: Optional[str] = None
    listino_tipo_descrizione: Optional[str] = None

class ListinoTipo(ListinoTipoBase):
    listino_tipo_id: int

    model_config = ConfigDict(from_attributes=True)