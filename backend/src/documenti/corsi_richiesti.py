"""Insegnamenti della domanda, distinti dagli esami gia' sostenuti."""

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.pratiche_corsisingoli.models import PraticaCorsoSingolo


def corsi_richiesti(db, pratica) -> list:
    relazione = PraticaCorsoSingolo
    scheda = db.scalar(select(relazione).where(relazione.pratica_id == pratica.pratica_id)
                       .options(*(joinedload(getattr(relazione, f"corso{i}")) for i in range(1, 7)))
                       .order_by(relazione.praCorSin_id.desc()).limit(1))
    corsi = [getattr(scheda, f"corso{i}") for i in range(1, 7)] if scheda else [
        pratica.listino_testa, pratica.corso2, pratica.corso3,
    ]
    return [c for c in corsi if c is not None]
