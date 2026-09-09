from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from src.database import Base 

class ListinoCorsoLaureaDB(Base):
    __tablename__ = "listini_corsilauree"

    listino_corsoLaurea_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listino_corsoLaurea_codice: Mapped[str] = mapped_column(String(45), nullable=False)
    listino_corsoLaurea_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)

    listini_testa: Mapped[List["ListinoTestaDB"]] = relationship("ListinoTestaDB", back_populates="corso_laurea")

class ListinoCorsoLaureaBase(BaseModel):
    listino_corsoLaurea_codice: str
    listino_corsoLaurea_descrizione: str

class ListinoCorsoLaureaCreate(ListinoCorsoLaureaBase):
    pass

class ListinoCorsoLaureaUpdate(BaseModel):
    listino_corsoLaurea_codice: Optional[str] = None
    listino_corsoLaurea_descrizione: Optional[str] = None

class ListinoCorsoLaurea(ListinoCorsoLaureaBase):
    listino_corsoLaurea_id: int

    model_config = ConfigDict(from_attributes=True)