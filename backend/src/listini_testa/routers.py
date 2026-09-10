import re
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from src.listini_testa.models import ListinoTestaDB, ListinoTesta, ListinoTestaCreate, ListinoTestaUpdate
from src.database import get_db 
from src.listino_tipoCorso.models import ListinoTipoCorsoDB  
from src.nome_universita.models import NomeUniversitaDB   
from src.listini_dettagli.models import ListinoDettaglio
from sqlalchemy.orm import joinedload, selectinload
from src.auth.dipendenze import get_current_utente

router = APIRouter(
    prefix="/listini-testa", tags=["Listini Testa"],dependencies=[Depends(get_current_utente)],
)

# Funzione centralizzata per il calcolo del prossimo codice canonico
def generate_next_code(db: Session) -> str:
    all_codes = db.query(ListinoTestaDB.listTesta_codice).all()
    max_n = 0
    pattern = re.compile(r"^ERSAF_COD_(\d+)$", re.IGNORECASE)
    
    for (codice,) in all_codes:
        if codice:
            match = pattern.match(codice.strip())
            if match:
                n_val = int(match.group(1)) # Parsing esplicito come intero
                if n_val > max_n:
                    max_n = n_val
                    
    next_n = max_n + 1
    return f"ERSAF_COD_{next_n:04d}"

# Endpoint unificati per la proposta del codice
@router.get("/next-code", response_model=dict)
@router.get("/prossimo-codice", response_model=dict)
def get_next_code(db: Session = Depends(get_db)):
    code = generate_next_code(db)
    return {"codice": code, "next_code": code}


#POST
@router.post("/", response_model=ListinoTesta, status_code=status.HTTP_201_CREATED)
def create_listino_testa(item: ListinoTestaCreate, db: Session = Depends(get_db)):
    codice = item.listTesta_codice
    
    if not codice or codice.strip() == "":
        codice = generate_next_code(db)
    else:
        existing = db.query(ListinoTestaDB).filter(ListinoTestaDB.listTesta_codice == codice).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Il codice '{codice}' è già stato assegnato a un altro prodotto."
            )

    item_data = item.model_dump(exclude={"listTesta_codice", "dettagli"})

    db_item = ListinoTestaDB(
        **item_data,
        listTesta_codice=codice,
        listTesta_created_at=datetime.now()
    )
    
    db.add(db_item)
    db.flush() 

    if item.dettagli:
        for det in item.dettagli:
            db_det = ListinoDettaglio(
                listTesta_id=db_item.listTesta_id,
                **det.model_dump()
            )
            db.add(db_det)

    try:
        db.commit()
        db.refresh(db_item)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        if "listtesta_codice" in error_msg or "unique" in error_msg or "duplicate" in error_msg:
            nuovo_codice = generate_next_code(db)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Il codice è stato assegnato nel frattempo, nuovo codice proposto: {nuovo_codice}"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore di integrità DB: {e.orig}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
    return db_item

@router.get("/opzioni/universita")
def get_opzioni_universita(db: Session = Depends(get_db)):
    universita = db.query(NomeUniversitaDB).all()
    return [{"id": u.nome_universita_id, "codice": u.nome_universita_codice, "descrizione": u.nome_universita_descrizione} for u in universita]

@router.get("/opzioni/tipi-corso")
def get_opzioni_tipi_corso(db: Session = Depends(get_db)):
    tipi = db.query(ListinoTipoCorsoDB).all()
    return [{"id": t.listino_tipoCorso_id, "descrizione": t.listino_tipoCorso_descrizione} for t in tipi]

#GET ALL
@router.get("/", response_model=List[ListinoTesta])
def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(40, ge=1, le=200),
    search: Optional[str] = None,
    universita: Optional[str] = None,
    tipo_corso: Optional[str] = None,
    attivo: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ListinoTestaDB).options(
        joinedload(ListinoTestaDB.universita),
        joinedload(ListinoTestaDB.tipo_corso)
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                ListinoTestaDB.listTesta_descrizione.ilike(search_term),
                ListinoTestaDB.listTesta_codice.ilike(search_term)
            )
        )

    if universita and universita != "Tutte le università":
        query = query.join(ListinoTestaDB.universita).filter(
            NomeUniversitaDB.nome_universita_descrizione == universita
        )

    if tipo_corso and tipo_corso != "Tutti i tipi":
        query = query.join(ListinoTestaDB.tipo_corso).filter(
            ListinoTipoCorsoDB.listino_tipoCorso_descrizione == tipo_corso
        )

    if attivo is not None:
        query = query.filter(ListinoTestaDB.listino_attivoSN == attivo)

    return query.order_by(ListinoTestaDB.listTesta_id.asc()).offset(skip).limit(limit).all()


# GET BY ID
@router.get("/{listTesta_id}", response_model=ListinoTesta)
def get_by_id(listTesta_id: int, db: Session = Depends(get_db)):
    db_item = (
        db.query(ListinoTestaDB)
        .options(
            joinedload(ListinoTestaDB.universita),
            joinedload(ListinoTestaDB.tipo_corso),
            selectinload(ListinoTestaDB.dettagli) # <-- Carica i dettagli associati
        )
        .filter(ListinoTestaDB.listTesta_id == listTesta_id)
        .first()
    )
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listino testa non trovato")
    return db_item


# PUT
@router.put("/{listTesta_id}", response_model=ListinoTesta)
def update(listTesta_id: int, item: ListinoTestaUpdate, db: Session = Depends(get_db)):
    db_item = (
        db.query(ListinoTestaDB)
        .options(
            joinedload(ListinoTestaDB.universita),
            joinedload(ListinoTestaDB.tipo_corso),
            selectinload(ListinoTestaDB.dettagli)
        )
        .filter(ListinoTestaDB.listTesta_id == listTesta_id)
        .first()
    )
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listino testa non trovato")
    
    update_data = item.model_dump(exclude_unset=True, exclude={"dettagli"})
    old_codice = db_item.listTesta_codice
    new_codice = update_data.get("listTesta_codice")

    if new_codice and new_codice != old_codice:
        existing = db.query(ListinoTestaDB).filter(
            ListinoTestaDB.listTesta_codice == new_codice,
            ListinoTestaDB.listTesta_id != listTesta_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Il codice '{new_codice}' è già occupato da un altro prodotto."
            )
        print(f"[AUDIT LOG] Prodotto ID {listTesta_id} - Codice modificato da '{old_codice}' a '{new_codice}' in data {datetime.now()}")

    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    # Gestione e sincronizzazione dei dettagli
    if item.dettagli is not None:
        db.query(ListinoDettaglio).filter(ListinoDettaglio.listTesta_id == listTesta_id).delete()
        for det in item.dettagli:
            db_det = ListinoDettaglio(
                listTesta_id=listTesta_id,
                **det.model_dump()
            )
            db.add(db_det)

    try:
        db.commit()
        db_item = (
            db.query(ListinoTestaDB)
            .options(
                joinedload(ListinoTestaDB.universita),
                joinedload(ListinoTestaDB.tipo_corso),
                selectinload(ListinoTestaDB.dettagli)
            )
            .filter(ListinoTestaDB.listTesta_id == listTesta_id)
            .first()
        )
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore di unicità sul codice: {e.orig}"
        )
        
    return db_item