from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from src.database import Base 
from typing import List

class Azienda(Base):
    __tablename__= "aziende"

    azienda_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    azienda_ragione_sociale: Mapped[str]= mapped_column(String, unique=True)
    azienda_partitaIVA:Mapped[str]= mapped_column(String, unique=True, nullable=True)
    azienda_codiceFiscale:Mapped[str]= mapped_column(String, unique=True, nullable=True)
    azienda_fatturazioneSDI:Mapped[str]= mapped_column(String, nullable=True)
    azienda_via:Mapped[str]= mapped_column(String, nullable=False)
    azienda_civico:Mapped[str]= mapped_column(String, nullable=True)
    azienda_citta:Mapped[str]= mapped_column(String, nullable=False)
    azienda_CAP:Mapped[str]= mapped_column(String, nullable=False)
    azienda_provincia:Mapped[str]= mapped_column(String, nullable=False)
    azienda_sitoWeb:Mapped[str]= mapped_column(String, nullable=True)
    azienda_email:Mapped[str]= mapped_column(String, nullable=True)
    azienda_telefono:Mapped[str]= mapped_column(String, nullable=True)
    azienda_pec:Mapped[str]= mapped_column(String, nullable=True)
    azienda_logo:Mapped[str]= mapped_column(String, nullable=True)
    azienda_codice_nazionale:Mapped[str]= mapped_column(String, nullable=False)
    azienda_iban:Mapped[str]= mapped_column(String, nullable=True)
    azienda_codice_bic:Mapped[str]= mapped_column(String, nullable=True)

    #Relazioni  
    clienti: Mapped[List["Cliente"]] = relationship(back_populates="azienda", cascade="all")