from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  # Adatta l'import al tuo progetto



# SQLALCHEMY MODEL
class PraticaAllegato(Base):
    __tablename__ = "pratiche_allegati"

    pratica_allegato_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    pratica_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    pratica_allegato_pathfile: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pratica_allegato_nomefile: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    pratica_allegato_checkfile: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    pratica_allegato_descrizione: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    
    pratica_allegato_created_by: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_allegato_created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    pratica_allegato_updated_by: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    pratica_allegato_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )



# PYDANTIC SCHEMAS
class PraticaAllegatoBase(BaseModel):
    pratica_id: int
    pratica_allegato_pathfile: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_nomefile: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_checkfile: int = 0
    pratica_allegato_descrizione: str = Field(..., max_length=255)


class PraticaAllegatoCreate(PraticaAllegatoBase):
    pratica_allegato_created_by: int


class PraticaAllegatoUpdate(BaseModel):
    pratica_id: Optional[int] = None
    pratica_allegato_pathfile: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_nomefile: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_checkfile: Optional[int] = None
    pratica_allegato_descrizione: Optional[str] = Field(default=None, max_length=255)
    pratica_allegato_updated_by: int


class PraticaAllegatoResponse(PraticaAllegatoBase):
    pratica_allegato_id: int
    pratica_allegato_created_by: int
    pratica_allegato_created_at: Optional[datetime] = None
    pratica_allegato_updated_by: int
    pratica_allegato_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)