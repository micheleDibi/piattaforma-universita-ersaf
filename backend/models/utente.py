from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Utente(Base):
    __tablename__ = "utenti" 

    utente_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    utente_username = Column(String, unique=True, index=True, nullable=False)
    utente_password = Column(String, index=True, nullable=False)
    utente_ultimo_login = Column(DateTime, nullable=False)
    utente_ultimo_logout = Column(DateTime, nullable=False)
    utente_padre = Column(Integer, nullable=False)
    utente_attivoSN = Column(Integer, nullable=False)
    utente_created_by = Column(Integer, nullable=False)
    utente_created_at = Column(DateTime, nullable=False)
    utente_updated_by = Column(Integer, nullable=False)
    utente_updated_at = Column(DateTime, nullable=False)
    utente_salt = Column(String(36), nullable=False)
    