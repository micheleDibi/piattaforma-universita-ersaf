from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Date
from datetime import  date
from src.database import Base 
from typing import Optional
import enum

class SessoEnum(str, enum.Enum):
    UOMO = "uomo"
    DONNA = "donna"

    @classmethod
    def _missing_(cls, value):
        if value is None or str(value).strip() == "":
            return None
        val_str = str(value).strip().lower()
        if val_str in ["m", "uomo", "male"]:
            return cls.UOMO
        if val_str in ["f", "donna", "female"]:
            return cls.DONNA
        return None

class TipoDocumentoEnum(str, enum.Enum):
    CARTA_IDENTITA = "Carta d'identità"
    CARTA_IDENTITA_ALT = "Carta d'Identità"
    PASSAPORTO = "Passaporto"
    PATENTE = "Patente"

    @classmethod
    def _missing_(cls, value):
        if value is None or str(value).strip() == "":
            return None
        # Gestione case-insensitive per allineare eventuali varianti nel DB
        for member in cls:
            if member.value.lower() == str(value).strip().lower():
                return member
        return None

class Cliente(Base):
    __tablename__= "clienti"

    cliente_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente_codice:Mapped[str] = mapped_column(String, unique=True)
    cliente_nome:Mapped[str] = mapped_column(String, nullable=False)
    cliente_cognome:Mapped[str] = mapped_column(String, nullable=False)
    cliente_email:Mapped[str] = mapped_column(String, nullable=False)
    cliente_telefono:Mapped[str] = mapped_column(String, nullable=False)
    cliente_pec:Mapped[str] = mapped_column(String, nullable=True)
    cliente_indirizzo:Mapped[str] = mapped_column(String, nullable=False)
    cliente_civico:Mapped[str] = mapped_column(String, nullable=False)
    cliente_citta:Mapped[str] = mapped_column(String, nullable=False)
    cliente_CAP:Mapped[str] = mapped_column(String, nullable=False)
    cliente_provincia:Mapped[str] = mapped_column(String, nullable=False)
    cliente_cellulare:Mapped[str] = mapped_column(String, nullable=False)

    #Relazione
    utente_id:Mapped[int] = mapped_column(Integer, ForeignKey("utenti.utente_id"))
    cliente_luogoNascita:Mapped[str] = mapped_column(String, nullable=False)
    cliente_provinciaNascita:Mapped[str] = mapped_column(String, nullable=False)
    cliente_dataNascita:Mapped[date] = mapped_column(Date, nullable=False)
    cliente_cittadinanza:Mapped[str] = mapped_column(String, nullable=False)

    #Enum
    cliente_tipoDocumento: Mapped[TipoDocumentoEnum] = mapped_column(String, nullable=False)

    cliente_documento:Mapped[str] = mapped_column(String, nullable=False)
    cliente_comuneRilascio:Mapped[str] = mapped_column(String, nullable=False)
    cliente_dataRilascio:Mapped[date] = mapped_column(Date, nullable=False)
    cliente_dataScadenzaDocumento:Mapped[date] = mapped_column(Date, nullable=False)

    #Enum   
    cliente_sesso: Mapped[SessoEnum] = mapped_column(String, nullable=False)

    cliente_indirizzoDomicilio:Mapped[str] = mapped_column(String, nullable=True)
    cliente_civicoDomicilio:Mapped[str] = mapped_column(String, nullable=True)
    cliente_cittaDomicilio:Mapped[str] = mapped_column(String, nullable=True)
    cliente_CAPDomicilio:Mapped[str] = mapped_column(String, nullable=True)
    cliente_provinciaDomicilio:Mapped[str] = mapped_column(String, nullable=True)

    #Relazione
    cliente_ruolo:Mapped[int] = mapped_column(ForeignKey("ruoli.ruolo_id"), default=0)
    cliente_gg: Mapped[int]= mapped_column(Integer, nullable=True)
    attuatore_id: Mapped[int]= mapped_column(Integer, nullable=True)

    #Relazione
    azienda_id: Mapped[int]= mapped_column(ForeignKey("aziende.azienda_id"), nullable=True)
    tessera_id: Mapped[int]= mapped_column(Integer, nullable=True)
    cliente_abilPraticheUniv: Mapped[int]= mapped_column(Integer, nullable=False, default=0)
    cliente_pathCertificato: Mapped[str]= mapped_column(String, nullable=True)
    cliente_abilitazione_ecampus: Mapped[int]= mapped_column(Integer, nullable=False, default=0)
    cliente_abilitazione_link_campus: Mapped[int]= mapped_column(Integer, nullable=False, default=0)
    cliente_abilitazione_corsi_speciali: Mapped[int]= mapped_column(Integer, nullable=False, default=0)
    cliente_abilitazione_a4u: Mapped[int]= mapped_column(Integer, nullable=False, default=0)

    utente: Mapped["Utente"] = relationship(back_populates="clienti")
    ruolo: Mapped["Ruolo"] = relationship(back_populates="clienti")
    azienda: Mapped[Optional["Azienda"]]= relationship(back_populates="clienti")