"""Lettura delle rate eCampus dal piano legacy, senza calcolare nuovi importi."""

from sqlalchemy import Column, Date, Integer, Numeric, func, select
from sqlalchemy.orm import Session

from src.database import Base


class DilazioneEcampus(Base):
    """Tabella preesistente: tassa usa la convenzione legacy vero=-1, falso=0."""

    __tablename__ = "dilazioni_pagamenti_ecampus"

    dilazione_id = Column(Integer, primary_key=True, autoincrement=True)
    dilazione_data = Column(Date, nullable=False)
    dilazione_importo = Column(Numeric(20, 8))
    pratica_id = Column(Integer, nullable=False)
    dilazione_tassa = Column(Integer, default=0)


def rate_ecampus(db: Session, pratica_id: int) -> list[DilazioneEcampus]:
    """Le sole rate della retta, in ordine di scadenza e poi di ID; tasse escluse."""
    return list(db.scalars(select(DilazioneEcampus).where(
        DilazioneEcampus.pratica_id == pratica_id,
        func.coalesce(DilazioneEcampus.dilazione_tassa, 0) == 0,
    ).order_by(DilazioneEcampus.dilazione_data, DilazioneEcampus.dilazione_id)))
