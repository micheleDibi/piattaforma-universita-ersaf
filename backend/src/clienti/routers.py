from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.clienti.models import Cliente
from src.clienti.schemas import ClienteCreate, ClienteResponse
from src.database import get_db

router = APIRouter(prefix="/clienti", tags=["Clienti"])

#POST
@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crea_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

#GET ALL (paginazione a 40)
@router.get("/", response_model=List[ClienteResponse])
def leggi_clienti(skip: int = 0, limit: int = 40, db: Session = Depends(get_db)):
    clienti = db.query(Cliente).offset(skip).limit(limit).all()
    return clienti

#GET BY ID
@router.get("/{cliente_id}", response_model=ClienteResponse)
def leggi_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    return db_cliente

#PUT
@router.put("/{cliente_id}", response_model=ClienteResponse)
def aggiorna_cliente(cliente_id: int, cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    
    for key, value in cliente.model_dump().items():
        setattr(db_cliente, key, value)
        
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

