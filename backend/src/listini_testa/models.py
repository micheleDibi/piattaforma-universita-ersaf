from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, String, text, ForeignKey
from src.database import Base 
from src.listino_tipoCorso.models import ListinoTipoCorsoDB  
from src.nome_universita.models import NomeUniversitaDB   

# Modello SQLAlchemy 
class ListinoTestaDB(Base):
    __tablename__ = "listini_testa"

    listTesta_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listTesta_codice: Mapped[str] = mapped_column(String(45), nullable=False)
    listTesta_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)
    listTesta_livello: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listino_tipo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    listino_modalita_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relazioni
    listino_tipoCorso_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("listini_tipicorsi.listino_tipoCorso_id"), nullable=True)
    listino_durataLaurea_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listino_facolta_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listino_corsoLaurea_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    nome_universita_id: Mapped[int] = mapped_column(Integer, ForeignKey("nome_universita.nome_universita_id"), nullable=False, default=1)
    listino_attivoSN: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)
    
    listTesta_created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listTesta_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    listTesta_updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listTesta_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    tipo_corso: Mapped[Optional["ListinoTipoCorsoDB"]] = relationship("ListinoTipoCorsoDB", back_populates="listini_testa")
    universita: Mapped[Optional["NomeUniversitaDB"]] = relationship("NomeUniversitaDB", back_populates="listini_testa")

# Schemi Pydantic 
class ListinoTestaBase(BaseModel):
    listTesta_codice: str
    listTesta_descrizione: str
    listTesta_livello: Optional[int] = None
    listino_tipo_id: int
    listino_modalita_id: Optional[int] = None
    listino_tipoCorso_id: Optional[int] = None
    listino_durataLaurea_id: Optional[int] = None
    listino_facolta_id: Optional[int] = None
    listino_corsoLaurea_id: Optional[int] = None
    nome_universita_id: int = 1
    listino_attivoSN: int = -1

class ListinoTestaCreate(ListinoTestaBase):
    listTesta_created_by: Optional[int] = None

class ListinoTestaUpdate(BaseModel):
    listTesta_codice: Optional[str] = None
    listTesta_descrizione: Optional[str] = None
    listTesta_livello: Optional[int] = None
    listino_tipo_id: Optional[int] = None
    listino_modalita_id: Optional[int] = None
    listino_tipoCorso_id: Optional[int] = None
    listino_durataLaurea_id: Optional[int] = None
    listino_facolta_id: Optional[int] = None
    listino_corsoLaurea_id: Optional[int] = None
    nome_universita_id: Optional[int] = None
    listino_attivoSN: Optional[int] = None
    listTesta_updated_by: Optional[int] = None

class ListinoTesta(ListinoTestaBase):
    listTesta_id: int
    listTesta_created_by: Optional[int] = None
    listTesta_created_at: Optional[datetime] = None
    listTesta_updated_by: Optional[int] = None
    listTesta_updated_at: Optional[datetime] = None

    # Campi testuali per il frontend (corretto il typo in tipoCorso)
    nome_universita: Optional[str] = None
    listino_tipoCorso_descrizione: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def extract_relations(cls, data):
        # Se stiamo ricevendo un'istanza SQLAlchemy, convertiamola in dict estraendo anche le relazioni
        if not isinstance(data, dict):
            item_dict = {}
            for key in data.__table__.columns.keys():
                item_dict[key] = getattr(data, key, None)
            
            universita_obj = getattr(data, "universita", None)
            if universita_obj:
                item_dict["nome_universita"] = getattr(universita_obj, "nome_universita_descrizione", None)
            else:
                item_dict["nome_universita"] = None

            tipo_corso_obj = getattr(data, "tipo_corso", None)
            if tipo_corso_obj:
                item_dict["listino_tipoCorso_descrizione"] = getattr(tipo_corso_obj, "listino_tipoCorso_descrizione", None)
            else:
                item_dict["listino_tipoCorso_descrizione"] = None

            return item_dict
        return data

    model_config = ConfigDict(from_attributes=True)