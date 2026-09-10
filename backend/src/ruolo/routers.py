from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.auth.dipendenze import get_current_utente
from src.database import get_db
from src.ruolo.models import Ruolo
from src.ruolo.schemas import RuoloCreate, RuoloResponse, RuoloUpdate

# L'autenticazione e' una dipendenza del router, non del singolo endpoint:
# quando era per endpoint, 4 rotte su 4 se ne sono dimenticate. Qui pesava piu'
# che altrove: un PUT anonimo su ruolo_codice disattivava il 2FA del ruolo
# Nazionale, perche' il login lo decide confrontando proprio quella stringa.
router = APIRouter(
    prefix="/ruoli",
    tags=["Ruoli"],
    dependencies=[Depends(get_current_utente)],
)


def _ruolo_o_404(db: Session, ruolo_id: int) -> Ruolo:
    db_ruolo = db.query(Ruolo).filter(Ruolo.ruolo_id == ruolo_id).first()
    if not db_ruolo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ruolo non trovato"
        )
    return db_ruolo


def _verifica_codice_libero(db: Session, codice: str, escludi_id: int | None = None) -> None:
    """ruolo_codice deve restare univoco anche senza UNIQUE nel database.

    codice_ruolo() risolve un ruolo_id in una stringa e il login la confronta
    con "nazionale": due righe con lo stesso codice rendono ambiguo chi ha
    diritto al 2FA e chi compare fra gli attuatori.
    """
    query = db.query(Ruolo).filter(Ruolo.ruolo_codice == codice)
    if escludi_id is not None:
        query = query.filter(Ruolo.ruolo_id != escludi_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esiste già un ruolo con questo codice.",
        )


@router.post("/", response_model=RuoloResponse, status_code=status.HTTP_201_CREATED)
def crea_ruolo(ruolo: RuoloCreate, db: Session = Depends(get_db)):
    _verifica_codice_libero(db, ruolo.ruolo_codice)

    db_ruolo = Ruolo(**ruolo.model_dump())
    db.add(db_ruolo)
    db.commit()
    db.refresh(db_ruolo)
    return db_ruolo


#GET ALL
@router.get("/", response_model=List[RuoloResponse])
def leggi_ruoli(db: Session = Depends(get_db)):
    # Nessuna paginazione: i ruoli sono sette e alimentano le tendine del
    # frontend, che devono vederli tutti. Un ORDER BY serve comunque perche'
    # l'ordine delle voci non cambi da una richiesta all'altra.
    return db.query(Ruolo).order_by(Ruolo.ruolo_id.asc()).all()


#GET BY ID
@router.get("/{ruolo_id}", response_model=RuoloResponse)
def leggi_ruolo(ruolo_id: int, db: Session = Depends(get_db)):
    return _ruolo_o_404(db, ruolo_id)


#PUT
@router.put("/{ruolo_id}", response_model=RuoloResponse)
def aggiorna_ruolo(ruolo_id: int, ruolo: RuoloUpdate, db: Session = Depends(get_db)):
    db_ruolo = _ruolo_o_404(db, ruolo_id)

    modifiche = ruolo.model_dump(exclude_unset=True)
    if "ruolo_codice" in modifiche:
        _verifica_codice_libero(db, modifiche["ruolo_codice"], escludi_id=ruolo_id)

    for chiave, valore in modifiche.items():
        setattr(db_ruolo, chiave, valore)

    db.commit()
    db.refresh(db_ruolo)
    return db_ruolo
