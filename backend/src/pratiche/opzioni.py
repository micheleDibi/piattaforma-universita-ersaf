"""Lookup autenticati limitati alle anagrafiche e ai percorsi presenti in pratiche."""
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.auth.visibilita import Visibilita, condizione_azienda, visibilita_corrente
from src.database import get_db
from src.clienti.models import Cliente
from src.listini_testa.models import ListinoTestaDB
from src.pratiche.models import Pratica
from src.pratiche_stati.models import PraticaStato

router = APIRouter()


class RicercaOpzioni(BaseModel):
    search: str = Field("", max_length=100)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=50)


class Opzione(BaseModel):
    id: int
    label: str
    dettaglio: str | None = None


class PaginaOpzioni(BaseModel):
    elementi: list[Opzione]
    altri: bool


@router.get("/filtri/stati", response_model=list[Opzione])
def stati(db: Session = Depends(get_db)):
    return [Opzione(id=r.pratica_stato_id, label=r.pratica_stato_descrizione)
            for r in db.query(PraticaStato).order_by(PraticaStato.pratica_stato_id).all()]


def query_opzioni(db: Session, tipo: str, ricerca: str, vis: Visibilita):
    if tipo == "studenti":
        identita = Cliente.cliente_id
        label = func.trim(func.concat(Cliente.cliente_nome, " ", Cliente.cliente_cognome))
        dettaglio = Cliente.cliente_codice
        relazione = Pratica.cliente_id == identita
        ordine = (Cliente.cliente_cognome, Cliente.cliente_nome, identita)
    else:
        identita = ListinoTestaDB.listTesta_id
        label = ListinoTestaDB.listTesta_descrizione
        dettaglio = ListinoTestaDB.listTesta_codice
        relazione = Pratica.listTesta_id == identita
        ordine = (label, identita)
    query = db.query(identita.label("id"), label.label("label"), dettaglio.label("dettaglio"))
    # Solo le pratiche che il chiamante vede: altrimenti la tendina proporrebbe
    # studenti e percorsi che esistono solo nelle pratiche di altre aziende.
    esistenza = db.query(Pratica.pratica_id).filter(relazione)
    condizione = condizione_azienda(vis, Pratica.azienda_id)
    if condizione is not None:
        esistenza = esistenza.filter(condizione)
    query = query.filter(esistenza.exists())
    for parola in ricerca.split():
        query = query.filter(or_(label.ilike(f"%{parola}%"), dettaglio.ilike(f"%{parola}%")))
    return query.order_by(*ordine)


@router.get("/filtri/{tipo}", response_model=PaginaOpzioni)
def opzioni(tipo: Literal["studenti", "percorsi"],
            ricerca: Annotated[RicercaOpzioni, Query()], db: Session = Depends(get_db),
            vis: Visibilita = Depends(visibilita_corrente)):
    righe = query_opzioni(db, tipo, ricerca.search, vis).offset(ricerca.skip).limit(ricerca.limit + 1).all()
    return PaginaOpzioni(elementi=[Opzione(id=r.id, label=r.label or "Non indicato", dettaglio=r.dettaglio)
                                  for r in righe[:ricerca.limit]], altri=len(righe) > ricerca.limit)
