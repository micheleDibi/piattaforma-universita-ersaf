from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db 
from src.aziende.models import Azienda  
from src.aziende.schemas import AziendaCreate, AziendaResponse  
from typing import Optional

router = APIRouter(prefix="/aziende", tags=["Aziende"])

#POST
@router.post("/", response_model=AziendaResponse, status_code=status.HTTP_201_CREATED)
def crea_azienda(azienda_in: AziendaCreate, db: Session = Depends(get_db)):

    if azienda_in.azienda_codiceFiscale and db.query(Azienda).filter(Azienda.azienda_codiceFiscale == azienda_in.azienda_codiceFiscale).first():
        raise HTTPException(status_code=400, detail="Esiste già un'azienda con questo Codice Fiscale.")
        
    if azienda_in.azienda_partitaIVA and db.query(Azienda).filter(Azienda.azienda_partitaIVA == azienda_in.azienda_partitaIVA).first():
        raise HTTPException(status_code=400, detail="Esiste già un'azienda con questa Partita IVA.")
        
    if azienda_in.azienda_ragione_sociale and db.query(Azienda).filter(Azienda.azienda_ragione_sociale == azienda_in.azienda_ragione_sociale).first():
        raise HTTPException(status_code=400, detail="Esiste già un'azienda con questa Ragione Sociale.")
        
    if azienda_in.azienda_email and db.query(Azienda).filter(Azienda.azienda_email == azienda_in.azienda_email).first():
        raise HTTPException(status_code=400, detail="Esiste già un'azienda con questa Email.")
        
    if azienda_in.azienda_pec and db.query(Azienda).filter(Azienda.azienda_pec == azienda_in.azienda_pec).first():
        raise HTTPException(status_code=400, detail="Esiste già un'azienda con questa PEC.")
        
    if azienda_in.azienda_telefono and db.query(Azienda).filter(Azienda.azienda_telefono == azienda_in.azienda_telefono).first():
        raise HTTPException(status_code=400, detail="Esiste già un'azienda con questo Telefono.")
        
    if azienda_in.azienda_iban and db.query(Azienda).filter(Azienda.azienda_iban == azienda_in.azienda_iban).first():
        raise HTTPException(status_code=400, detail="Esiste già un'azienda con questo IBAN.")
    
    nuova_azienda = Azienda(**azienda_in.model_dump())
    db.add(nuova_azienda)
    db.commit()
    db.refresh(nuova_azienda)
    return nuova_azienda

#GET ALL
@router.get("/", response_model=List[AziendaResponse])
def lista_aziende(
    skip: int = 0, 
    limit: int = 40, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)):
    query = db.query(Azienda)
    if search:
        query = query.filter(Azienda.azienda_ragione_sociale.ilike(f"{search}%"))
        
    aziende = query.offset(skip).limit(limit).all()
    return aziende

#GET BY ID
@router.get("/{azienda_id}", response_model=AziendaResponse)
def dettaglio_azienda(azienda_id: int, db: Session = Depends(get_db)):
    azienda = db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first()
    if not azienda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Azienda non trovata."
        )
    return azienda

#PUT
@router.put("/{azienda_id}", response_model=AziendaResponse)
def aggiorna_azienda(azienda_id: int, azienda_in: AziendaCreate, db: Session = Depends(get_db)):
    azienda = db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first()
    if not azienda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Azienda non trovata."
        )
    
    for key, value in azienda_in.model_dump().items():
        setattr(azienda, key, value)
        
    db.commit()
    db.refresh(azienda)
    return azienda

