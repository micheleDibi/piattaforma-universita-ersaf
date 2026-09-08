import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.utenti.models import Utente
from sqlalchemy.orm import Session, joinedload
from src.utenti.schemas import UtenteResponse, UtenteCreate, UtenteUpdate
from src.database import get_db
from typing import List
from src.auth.autorizzazioni import e_amministrativo
from src.auth.dipendenze import get_current_utente
from src.security.password import hash_password, messaggi_policy, verifica_policy_password


# L'autenticazione e' una dipendenza del router, non del singolo endpoint:
# quando era per endpoint, 2 rotte su 4 se ne sono dimenticate.
# Chi aggiunge una rotta qui la trova protetta senza doverci pensare; se una
# rotta dovra' essere pubblica lo si dichiara esplicitamente con
# dependencies=[] su quel decoratore.
router = APIRouter(
    prefix="/utenti",
    tags=["Utenti"],
    dependencies=[Depends(get_current_utente)],
)

def _verifica_padre(db: Session, utente_padre: int | None, utente_id: int | None = None) -> None:
    """utente_padre deve esistere, e non puo' essere se stessi.

    Il database ha la FOREIGN KEY su utente_created_by e utente_updated_by ma
    NON su utente_padre: si poteva scrivere un id qualsiasi e la riga restava
    li', con la scheda che mostrava "ID: 999999" e nessuno in grado di capire
    a chi si riferisse. La finestra "Cambia Padre" scrive proprio questo campo.
    """
    if utente_padre is None:
        return
    if utente_padre == utente_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Un utente non può essere padre di se stesso.",
        )
    esiste = (
        db.query(Utente.utente_id).filter(Utente.utente_id == utente_padre).first()
    )
    if not esiste:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'utente padre con id {utente_padre} non esiste.",
        )


#POST
@router.post("/", response_model=UtenteResponse, status_code=status.HTTP_201_CREATED)
def crea_utente(utente: UtenteCreate,
                db: Session = Depends(get_db),
                current_utente = Depends(get_current_utente)):

    esistente = db.query(Utente).filter(Utente.utente_username == utente.utente_username).first()
    if esistente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "codice": "username_preso",
                "messaggio": "Esiste già un utente registrato con questo username."
            },
        )
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

    _verifica_padre(db, utente.utente_padre)

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

# UtenteResponse annida padre e aggiornato_da, due relazioni lazy: senza
# joinedload una pagina da 50 costava 101 query. Il .clienti annidato serve a
# UtentePadreSchema.cliente, che espone nome e cognome della persona.
_CARICAMENTO_UTENTE = (
    joinedload(Utente.padre).joinedload(Utente.clienti),
    joinedload(Utente.aggiornato_da).joinedload(Utente.clienti),
)


#GET ALL
@router.get("/", response_model=List[UtenteResponse])
def leggi_utenti(
    skip: int = Query(0, ge=0),
    # Un tetto esplicito: prima ?limit=10000000 scaricava l'intera tabella.
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return (
        db.query(Utente)
        .options(*_CARICAMENTO_UTENTE)
        # Senza ORDER BY, MySQL non garantisce l'ordine fra una pagina e la
        # successiva: lo scroll poteva ripetere o saltare righe.
        .order_by(Utente.utente_id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

#GET BY ID
@router.get("/{utente_id}", response_model=UtenteResponse)
def leggi_utente(utente_id: int, db: Session = Depends(get_db)):
    db_utente = (
        db.query(Utente)
        .options(*_CARICAMENTO_UTENTE)
        .filter(Utente.utente_id == utente_id)
        .first()
    )
    if not db_utente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato"
        )
    return db_utente

#PUT
@router.put("/{utente_id}", response_model=UtenteResponse)
def aggiorna_utente(utente_id: int,
                    utente: UtenteUpdate,
                    db: Session = Depends(get_db),
                    current_utente = Depends(get_current_utente)):
    # Autenticato non basta: senza questo controllo qualunque utente loggato
    # poteva disattivare o rinominare qualunque altro dei 4.771, amministratore
    # compreso. Si modifica se' stessi, oppure si ha un ruolo amministrativo.
    if utente_id != current_utente.utente_id and not e_amministrativo(
        db, current_utente.utente_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai i permessi per modificare un altro utente.",
        )

    db_utente = db.query(Utente).filter(Utente.utente_id == utente_id).first()
    if not db_utente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato"
        )

    # exclude_unset=True: prima i campi non inviati venivano sovrascritti con i
    # loro default, azzerando utente_created_by e utente_updated_by.
    # Lo schema non ha piu' utente_password: la password non si cambia da qui.
    modifiche = utente.model_dump(exclude_unset=True)
    if "utente_padre" in modifiche:
        _verifica_padre(db, modifiche["utente_padre"], utente_id=utente_id)

    for key, value in modifiche.items():
        setattr(db_utente, key, value)

    db_utente.utente_updated_by = current_utente.utente_id
    db.commit()
    db.refresh(db_utente)
    return db_utente

