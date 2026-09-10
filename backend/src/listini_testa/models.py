from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, String, text, ForeignKey
from src.database import Base 
from src.listini_dettagli.models import ListinoDettaglioCreate, ListinoDettaglioResponse

class ListinoTestaDB(Base):
    __tablename__ = "listini_testa"

    listTesta_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    listTesta_codice: Mapped[str] = mapped_column(String(45), nullable=False)
    listTesta_descrizione: Mapped[str] = mapped_column(String(255), nullable=False)
    listTesta_livello: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    listino_tipo_id: Mapped[int] = mapped_column(Integer, ForeignKey("listini_tipi.listino_tipo_id"), nullable=False)
    listino_modalita_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("listini_modalita.listino_modalita_id"), nullable=True)
    listino_tipoCorso_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("listini_tipicorsi.listino_tipoCorso_id"), nullable=True)
    listino_durataLaurea_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("listini_duratalauree.listino_durataLaurea_id"), nullable=True)
    listino_facolta_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("listini_facolta.listino_facolta_id"), nullable=True)
    listino_corsoLaurea_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("listini_corsilauree.listino_corsoLaurea_id"), nullable=True)
    nome_universita_id: Mapped[int] = mapped_column(Integer, ForeignKey("nome_universita.nome_universita_id"), nullable=False, default=1)
    
    listino_attivoSN: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)
    
    listTesta_created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listTesta_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    listTesta_updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listTesta_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    # Relazioni mappate con stringhe
    tipo: Mapped["ListinoTipoDB"] = relationship("ListinoTipoDB")
    modalita: Mapped[Optional["ListinoModalitaDB"]] = relationship("ListinoModalitaDB")
    tipo_corso: Mapped[Optional["ListinoTipoCorsoDB"]] = relationship("ListinoTipoCorsoDB")
    durata_laurea: Mapped[Optional["ListinoDurataLaureaDB"]] = relationship("ListinoDurataLaureaDB")
    facolta: Mapped[Optional["ListinoFacoltaDB"]] = relationship("ListinoFacoltaDB")
    universita: Mapped[Optional["NomeUniversitaDB"]] = relationship("NomeUniversitaDB")
    corso_laurea: Mapped[Optional["ListinoCorsoLaureaDB"]] = relationship("ListinoCorsoLaureaDB", back_populates="listini_testa")
    
    # ── AGGIUNTO: Relazione con i dettagli del listino ──
    dettagli: Mapped[List["ListinoDettaglio"]] = relationship("ListinoDettaglio", back_populates="testa", cascade="all, delete-orphan")

# Schemi Pydantic per Listino Testa
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
    dettagli: Optional[List["ListinoDettaglioCreate"]] = []

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
    dettagli: Optional[List[ListinoDettaglioCreate]] = None

class ListinoTesta(ListinoTestaBase):
    listTesta_id: int
    listTesta_created_by: Optional[int] = None
    listTesta_created_at: Optional[datetime] = None
    listTesta_updated_by: Optional[int] = None
    listTesta_updated_at: Optional[datetime] = None

    nome_universita: Optional[str] = None
    listino_tipoCorso_descrizione: Optional[str] = None

    dettagli: List["ListinoDettaglioResponse"] = []

    @model_validator(mode='before')
    @classmethod
    def extract_relations(cls, data):
        if not isinstance(data, dict):
            item_dict = {}
            for key in data.__table__.columns.keys():
                item_dict[key] = getattr(data, key, None)

            item_dict["dettagli"] = getattr(data, "dettagli", [])
            
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

ListinoTestaCreate.model_rebuild()
ListinoTesta.model_rebuild()

import src.listini_tipi.models
import src.listino_tipoCorso.models
import src.nome_universita.models
import src.listini_corsilaurea.models
import src.listini_modalita.models
import src.listini_duratalauree.models
import src.listini_facolta.models