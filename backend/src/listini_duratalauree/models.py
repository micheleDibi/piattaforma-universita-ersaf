from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from src.database import Base 

# Modello SQLAlchemy 
class ListinoDurataLaureaDB(Base):
    __tablename__ = "listini_duratalauree"

    listino_durataLaurea_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listino_durataLaurea_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relazione inversa con listini_testa (opzionale)
    listini_testa: Mapped[List["ListinoTestaDB"]] = relationship("ListinoTestaDB", back_populates="durata_laurea")


# Schemi Pydantic 
class ListinoDurataLaureaBase(BaseModel):
    listino_durataLaurea_descrizione: str

class ListinoDurataLaureaCreate(ListinoDurataLaureaBase):
    pass

class ListinoDurataLaureaUpdate(BaseModel):
    listino_durataLaurea_descrizione: Optional[str] = None

class ListinoDurataLaurea(ListinoDurataLaureaBase):
    listino_durataLaurea_id: int

    model_config = ConfigDict(from_attributes=True)