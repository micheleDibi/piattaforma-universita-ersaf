"""Sottoinsieme delle tabelle legacy: mai ricrearle durante l'avvio."""
from sqlalchemy import Column, DateTime, Integer, String, Text

from src.database import Base


class Messaggio(Base):
    __tablename__ = "messaggi"
    messaggio_id = Column(Integer, primary_key=True, autoincrement=True)
    messaggio_testo = Column(Text, nullable=False)
    messaggio_oggetto = Column(String(255), nullable=False, default="-")
    messaggio_dataInvio = Column(DateTime, nullable=True)
    cliente_mittente_id = Column(Integer, nullable=False)
    cliente_destinatario_id = Column(Integer, nullable=False)
    messaggio_stato_id = Column(Integer, nullable=False)
    messaggio_codice = Column(String(45), nullable=False)
    pratica_id = Column(Integer, nullable=False, index=True)


class StatoMessaggio(Base):
    __tablename__ = "messaggi_stati"
    messaggio_stato_id = Column(Integer, primary_key=True, autoincrement=True)
    messaggio_stato_codice = Column(String(45), nullable=False)
