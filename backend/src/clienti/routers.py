from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.clienti.models import Cliente
from src.clienti.schemas import ClienteCreate, ClienteResponse
from src.database import get_db
from typing import Optional

router = APIRouter(prefix="/clienti", tags=["Clienti"])

#POST
@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crea_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

#GET ALL (paginazione a 50)
@router.get("/", response_model=List[ClienteResponse])
def leggi_clienti(
    skip: int = 0, 
    limit: int = 50, 
    search: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Cliente)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Cliente.cliente_nome.ilike(search_term)) | 
            (Cliente.cliente_cognome.ilike(search_term))
        )
        
    clienti = query.order_by(Cliente.cliente_id.asc()).offset(skip).limit(limit).all()
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

