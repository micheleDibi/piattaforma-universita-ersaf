from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from src.listini_testa.models import ListinoTestaDB, ListinoTesta, ListinoTestaCreate, ListinoTestaUpdate
from src.database import get_db 
from src.listino_tipoCorso.models import ListinoTipoCorsoDB  
from src.nome_universita.models import NomeUniversitaDB   
from src.universita.models import Universita
from src.nome_universita.models import NomeUniversitaDB
from src.listino_tipoCorso.models import ListinoTipoCorsoDB
from sqlalchemy import or_

router = APIRouter(
    prefix="/listini-testa",tags=["Listini Testa"])

#POST
@router.post("/", response_model=ListinoTesta, status_code=status.HTTP_201_CREATED)
def post(item: ListinoTestaCreate, db: Session = Depends(get_db)):
    db_item = ListinoTestaDB(
        **item.model_dump(),
        listTesta_created_at=datetime.now()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
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
    skip: int = 0,
    limit: int = 100,
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

    items = query.offset(skip).limit(limit).all()
    return items

#GET BY ID
@router.get("/{listTesta_id}", response_model=ListinoTesta)
def get_by_id(listTesta_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ListinoTestaDB).filter(ListinoTestaDB.listTesta_id == listTesta_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listino testa non trovato")
    return db_item

#PUT
@router.put("/{listTesta_id}", response_model=ListinoTesta)
def update(listTesta_id: int, item: ListinoTestaUpdate, db: Session = Depends(get_db)):
    db_item = db.query(ListinoTestaDB).filter(ListinoTestaDB.listTesta_id == listTesta_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listino testa non trovato")
    
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    db_item.listTesta_updated_at = datetime.now()
    db.commit()
    db.refresh(db_item)
    return db_item