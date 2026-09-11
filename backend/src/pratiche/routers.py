from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.auth.dipendenze import get_current_utente

# Importa la dipendenza della sessione DB (modifica il percorso se necessario)
from src.database import get_db

# Importa i modelli e gli schemi forniti
# assumendo che siano nello stesso file o in moduli specifici
from src.pratiche.models import Pratica, PraticaCreate, PraticaResponse, PraticaUpdate

# Le pratiche contengono dati personali dei sottoscrittori: il router e' chiuso
# come gli altri moduli, con la verifica della sessione su ogni operazione.
router = APIRouter(
    prefix="/pratiche",
    tags=["Pratiche"],
    dependencies=[Depends(get_current_utente)],
)


@router.post(
    "/",
    response_model=PraticaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una nuova pratica",
    description="Crea un nuovo record della pratica nel database."
)
def create_pratica(
    pratica_in: PraticaCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nuova pratica.
    Imposta automaticamente 'pratica_created_at' all'ora corrente UTC.
    """
    # Convertiamo lo schema Pydantic in un dizionario per istanziare il modello ORM
    pratica_data = pratica_in.model_dump(exclude_unset=True)
    
    # Crea l'istanza SQLAlchemy
    db_pratica = Pratica(**pratica_data)
    
    # func.now() e non l'orologio di Python: le righe esistenti sono scritte
    # con l'ora del database, e mescolare i due orologi sposterebbe ogni
    # pratica nuova di due ore rispetto a tutte le altre.
    db_pratica.pratica_created_at = func.now()

    db.add(db_pratica)
    db.commit()
    db.refresh(db_pratica)
    
    return db_pratica


@router.get(
    "/",
    response_model=List[PraticaResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista pratiche con paginazione e filtri opzionali"
)
def read_pratiche(
    skip: int = Query(0, ge=0, description="Numero di elementi da saltare"),
    limit: int = Query(100, ge=1, le=500, description="Numero massimo di elementi da restituire"),
    cliente_id: Optional[int] = Query(None, description="Filtra per ID cliente"),
    pratica_stato_id: Optional[int] = Query(None, description="Filtra per ID stato pratica"),
    db: Session = Depends(get_db)
):
    """
    Recupera una lista di pratiche applicando paginazione ed eventuali filtri per cliente o stato.
    """
    query = db.query(Pratica)

    # Filtri opzionali
    if cliente_id is not None:
        query = query.filter(Pratica.cliente_id == cliente_id)
    if pratica_stato_id is not None:
        query = query.filter(Pratica.pratica_stato_id == pratica_stato_id)

    pratiche = query.offset(skip).limit(limit).all()
    return pratiche


@router.get(
    "/{pratica_id}",
    response_model=PraticaResponse,
    status_code=status.HTTP_200_OK,
    summary="Recupera una singola pratica tramite ID"
)
def read_pratica_by_id(
    pratica_id: int,
    db: Session = Depends(get_db)
):
    """
    Restituisce i dettagli di una pratica specifica cercando per ID.
    """
    db_pratica = db.query(Pratica).filter(Pratica.pratica_id == pratica_id).first()
    if not db_pratica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pratica con ID {pratica_id} non trovata."
        )
    return db_pratica


@router.patch(
    "/{pratica_id}",
    response_model=PraticaResponse,
    status_code=status.HTTP_200_OK,
    summary="Aggiorna una pratica (modifica parziale)"
)
def update_pratica(
    pratica_id: int,
    pratica_in: PraticaUpdate,
    db: Session = Depends(get_db)
):
    """
    Aggiorna parzialmente i dati di una pratica. 
    Imposta automaticamente 'pratica_updated_at' con il timestamp di modifica.
    """
    db_pratica = db.query(Pratica).filter(Pratica.pratica_id == pratica_id).first()
    if not db_pratica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pratica con ID {pratica_id} non trovata."
        )

    # Estrae soltanto i campi inviati nel payload della richiesta
    update_data = pratica_in.model_dump(exclude_unset=True)

    # Applica le modifiche all'oggetto ORM
    for field, value in update_data.items():
        setattr(db_pratica, field, value)

    # Stesso orologio della creazione: quello del database.
    db_pratica.pratica_updated_at = func.now()

    db.add(db_pratica)
    db.commit()
    db.refresh(db_pratica)

    return db_pratica