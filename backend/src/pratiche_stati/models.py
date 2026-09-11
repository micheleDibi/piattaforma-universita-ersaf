from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from src.database import Base  



# SQLALCHEMY MODEL
class PraticaStato(Base):
    __tablename__ = "pratiche_stati"

    pratica_stato_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    # NOT NULL nel database reale: dichiararle facoltative farebbe fallire una
    # scrittura con un vincolo violato invece che con un errore di validazione.
    pratica_stato_codice: Mapped[str] = mapped_column(String(45), nullable=False)
    pratica_stato_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)

    pratiche: Mapped[List["Pratica"]] = relationship("Pratica", back_populates="stato")



# PYDANTIC SCHEMAS
class PraticaStatoBase(BaseModel):
    pratica_stato_codice: Optional[str] = Field(default=None, max_length=45)
    pratica_stato_descrizione: Optional[str] = Field(default=None, max_length=255)


class PraticaStatoCreate(PraticaStatoBase):
    pass


class PraticaStatoUpdate(BaseModel):
    pratica_stato_codice: Optional[str] = Field(default=None, max_length=45)
    pratica_stato_descrizione: Optional[str] = Field(default=None, max_length=255)


class PraticaStatoResponse(PraticaStatoBase):
    pratica_stato_id: int

    model_config = ConfigDict(from_attributes=True)