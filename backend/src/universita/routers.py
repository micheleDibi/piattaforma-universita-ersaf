from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from src.auth.dipendenze import get_current_utente
from src.clienti.models import Cliente
from src.database import get_db
from src.universita.models import Universita as UniversitaModel
from src.universita.schemas import Universita, UniversitaCreate, UniversitaUpdate

# L'autenticazione e' una dipendenza del router, non del singolo endpoint:
# quando era per endpoint, 4 rotte su 4 se ne sono dimenticate.
# Chi aggiunge una rotta qui la trova protetta senza doverci pensare; se una
# rotta dovra' essere pubblica lo si dichiara esplicitamente con
# dependencies=[] su quel decoratore.
router = APIRouter(
    prefix="/universita",
    tags=["Universita"],
    dependencies=[Depends(get_current_utente)],
)

def _curriculum_o_404(db: Session, universita_id: int) -> UniversitaModel:
    curriculum = (
        db.query(UniversitaModel)
        .filter(UniversitaModel.universita_id == universita_id)
        .first()
    )
    if not curriculum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Università con id {universita_id} non trovata",
        )
    return curriculum


def _verifica_cliente(db: Session, cliente_id: int | None) -> int:
    """cliente_id e' NOT NULL e non ha alcuna FOREIGN KEY nel database.

    Senza questo controllo si creavano curriculum orfani senza alcun errore, e
    ometterlo del tutto usciva come IntegrityError 1048, cioe' 500.
    """
    if cliente_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="cliente_id è obbligatorio.",
        )
    if not db.query(Cliente.cliente_id).filter(Cliente.cliente_id == cliente_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con id {cliente_id} non trovato",
        )
    return cliente_id


# GET ALL
@router.get("/", response_model=List[Universita])
def get_universita_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    cliente_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(UniversitaModel)
    if cliente_id is not None:
        query = query.filter(UniversitaModel.cliente_id == cliente_id)
    # Senza ORDER BY la paginazione poteva ripetere o saltare righe.
    return (
        query.order_by(UniversitaModel.universita_id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# GET BY ID
@router.get("/{universita_id}", response_model=Universita)
def get_universita_by_id(universita_id: int, db: Session = Depends(get_db)):
    return _curriculum_o_404(db, universita_id)


# POST
@router.post("/", response_model=Universita, status_code=status.HTTP_201_CREATED)
def create_universita(
    universita_data: UniversitaCreate,
    db: Session = Depends(get_db),
    current_utente=Depends(get_current_utente),
):
    dati = universita_data.model_dump(exclude_unset=True)
    _verifica_cliente(db, dati.get("cliente_id"))

    # L'attribuzione la decide il server: universita_createBy era nello schema,
    # quindi il chiamante poteva dichiarare di essere chiunque.
    dati["universita_createBy"] = current_utente.utente_id
    dati["universita_updateBy"] = current_utente.utente_id
    dati["universita_createDate"] = date.today()
    dati["universita_updateDate"] = date.today()

    db_universita = UniversitaModel(**dati)
    db.add(db_universita)
    db.commit()
    db.refresh(db_universita)
    return db_universita


# PUT
@router.put("/{universita_id}", response_model=Universita)
def update_universita(
    universita_id: int,
    universita_data: UniversitaUpdate,
    db: Session = Depends(get_db),
    current_utente=Depends(get_current_utente),
):
    db_universita = _curriculum_o_404(db, universita_id)

    modifiche = universita_data.model_dump(exclude_unset=True)
    # Spostare un curriculum su un'altra persona non e' un aggiornamento: era
    # possibile perche' cliente_id sta in UniversitaUpdate.
    modifiche.pop("cliente_id", None)
    # Idem per l'attribuzione: la decide il server.
    modifiche.pop("universita_createBy", None)
    modifiche.pop("universita_updateBy", None)

    for chiave, valore in modifiche.items():
        setattr(db_universita, chiave, valore)

    db_universita.universita_updateBy = current_utente.utente_id
    db_universita.universita_updateDate = date.today()

    db.commit()
    db.refresh(db_universita)
    return db_universita