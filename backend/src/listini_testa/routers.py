from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from src.listini_testa.models import ListinoTestaDB, ListinoTesta, ListinoTestaCreate, ListinoTestaUpdate
from src.database import get_db 
from src.listino_tipoCorso.models import ListinoTipoCorsoDB  
from src.nome_universita.models import NomeUniversitaDB   

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

#GET ALL
@router.get("/", response_model=List[ListinoTesta])
def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = (
        db.query(ListinoTestaDB)
        .options(
            joinedload(ListinoTestaDB.universita),
            joinedload(ListinoTestaDB.tipo_corso)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
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