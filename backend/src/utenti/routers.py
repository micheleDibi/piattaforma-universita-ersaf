import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from src.utenti.models import Utente
from sqlalchemy.orm import Session
from src.utenti.schemas import UtenteResponse, UtenteCreate, UtenteUpdate
from src.database import get_db
from typing import List
from src.auth.dipendenze import get_current_utente
from src.security.password import hash_password, messaggi_policy, verifica_policy_password


router = APIRouter(
    prefix="/utenti", tags=["Utenti"]
)

#POST
@router.post("/", response_model=UtenteResponse, status_code=status.HTTP_201_CREATED)
def crea_utente(utente: UtenteCreate,
                db: Session = Depends(get_db),
                current_utente = Depends(get_current_utente)):
    # Prima la password finiva in chiaro nella colonna, esattamente come nel
    # PUT. Il criterio "nessuna password in chiaro scritta da nessun percorso
    # di codice" non e' soddisfatto se si sistema solo il PUT.
    violate = verifica_policy_password(
        utente.utente_password, username=utente.utente_username
    )
    if violate:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "codice": "policy_password",
                "regole_violate": violate,
                "messaggi": messaggi_policy(violate),
            },
        )

    dati_utente = utente.model_dump(exclude={"utente_password"})
    id_corrente = current_utente.utente_id
    dati_utente["utente_created_by"] = id_corrente
    dati_utente["utente_updated_by"] = id_corrente
    dati_utente["utente_padre"] = id_corrente
    dati_utente["utente_password_hash"] = hash_password(utente.utente_password)
    dati_utente["utente_password_algo"] = "bcrypt"
    # NOT NULL nel database: stringa vuota, mai NULL.
    dati_utente["utente_password"] = ""
    # Generato dal server: bcrypt non lo usa, ma la colonna resta per
    # compatibilita' con la piattaforma legacy.
    dati_utente["utente_salt"] = str(uuid.uuid4())

    db_utente = Utente(**dati_utente)
    db.add(db_utente)
    db.commit()
    db.refresh(db_utente)
    return db_utente

#GET ALL
@router.get("/", response_model=List[UtenteResponse])
def leggi_utenti(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    utenti = db.query(Utente).offset(skip).limit(limit).all()
    return utenti

#GET BY ID
@router.get("/{utente_id}", response_model=UtenteResponse)
def leggi_utente(utente_id: int, db: Session = Depends(get_db)):
    db_utente = db.query(Utente).filter(Utente.utente_id == utente_id).first()
    if not db_utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return db_utente

#PUT
@router.put("/{utente_id}", response_model=UtenteResponse)
def aggiorna_utente(utente_id: int,
                    utente: UtenteUpdate,
                    db: Session = Depends(get_db),
                    current_utente = Depends(get_current_utente)):
    db_utente = db.query(Utente).filter(Utente.utente_id == utente_id).first()
    if not db_utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    # exclude_unset=True: prima i campi non inviati venivano sovrascritti con i
    # loro default, azzerando utente_created_by e utente_updated_by.
    # Lo schema non ha piu' utente_password: la password non si cambia da qui.
    for key, value in utente.model_dump(exclude_unset=True).items():
        setattr(db_utente, key, value)

    db_utente.utente_updated_by = current_utente.utente_id
    db.commit()
    db.refresh(db_utente)
    return db_utente

