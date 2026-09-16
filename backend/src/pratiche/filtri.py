"""Filtri dell'elenco: gli studenti sono clienti, i percorsi listini_testa."""
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.pratiche.models import Pratica


class FiltriPratiche(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(40, ge=1, le=200)
    search: str = Field("", max_length=255)
    cliente_id: int | None = None  # contratto precedente, conservato
    studenti: list[Annotated[int, Field(gt=0)]] = Field(default_factory=list, max_length=100)
    pratica_stato_id: int | None = Field(None, gt=0)
    percorso_id: int | None = Field(None, gt=0)
    nome_universita_id: int | None = Field(None, gt=0)
    listino_tipo_corso_id: list[Annotated[int, Field(gt=0)]] = Field(default_factory=list, max_length=10)


def query_filtrata(db: Session, filtri: FiltriPratiche):
    query = db.query(Pratica)
    if filtri.search.strip():
        query = query.filter(Pratica.pratica_numero.ilike(f"%{filtri.search.strip()}%"))
    if filtri.cliente_id is not None:
        query = query.filter(Pratica.cliente_id == filtri.cliente_id)
    if filtri.studenti:
        query = query.filter(Pratica.cliente_id.in_(filtri.studenti))
    if filtri.pratica_stato_id is not None:
        query = query.filter(Pratica.pratica_stato_id == filtri.pratica_stato_id)
    if filtri.percorso_id is not None:
        query = query.filter(Pratica.listTesta_id == filtri.percorso_id)
    if filtri.nome_universita_id is not None:
        query = query.filter(Pratica.nome_universita_id == filtri.nome_universita_id)
    if filtri.listino_tipo_corso_id:
        query = query.filter(Pratica.listino_tipo_corso_id.in_(filtri.listino_tipo_corso_id))
    return query
