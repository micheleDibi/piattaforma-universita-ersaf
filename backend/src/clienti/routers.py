from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from src.clienti.models import Cliente
from src.clienti.schemas import ClienteCreate, ClienteResponse, ClienteConUtenteCreate
from src.database import get_db
from typing import Optional
from src.ruolo.models import Ruolo
from src.aziende.models import Azienda
from src.utenti.models import Utente


router = APIRouter(prefix="/clienti", tags=["Clienti"])

#POST
@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crea_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.post("/con-utente", status_code=status.HTTP_201_CREATED)
def crea_cliente_e_utente(dati: ClienteConUtenteCreate, db: Session = Depends(get_db)):

    # Controlli su codice, email, telefono, cellulare, pec, documento
    if dati.cliente_codice and db.query(Cliente).filter(Cliente.cliente_codice == dati.cliente_codice).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Esiste già un cliente con questo codice."
        )
        
    if dati.cliente_email and db.query(Cliente).filter(Cliente.cliente_email == dati.cliente_email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Esiste già un cliente registrato con questa email."
        )
        
    if dati.cliente_telefono and db.query(Cliente).filter(Cliente.cliente_telefono == dati.cliente_telefono).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Esiste già un cliente con questo numero di telefono."
        )
    
    if dati.cliente_cellulare and db.query(Cliente).filter(Cliente.cliente_cellulare == dati.cliente_cellulare).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Esiste già un cliente con questo numero di cellulare."
        )
        
    if dati.cliente_pec and db.query(Cliente).filter(Cliente.cliente_pec == dati.cliente_pec).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Esiste già un cliente con questa PEC."
        )
        
    if dati.cliente_documento and db.query(Cliente).filter(Cliente.cliente_documento == dati.cliente_documento).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Esiste già un cliente con questo numero di documento."
        )

    try:
        #Crea prima l'Utente temporaneo per ottenere l'ID
        nuovo_utente = Utente(
            utente_username="temp",
            utente_password="temp", 
            utente_attivoSN=1
        )
        db.add(nuovo_utente)
        db.flush() # Genera utente_id

        # Genera Username e Password definitivi
        nome = dati.cliente_nome.strip()
        cognome = dati.cliente_cognome.strip()
        
        username = f"{nome}{cognome}"
        password = f"{nome[:3]}{cognome[:3]}{nuovo_utente.utente_id}"

        nuovo_utente.utente_username = username
        nuovo_utente.utente_password = password

        # Prepara i dati del cliente ESCLUDENDO i campi utente temporanei dello schema
        dati_dict = dati.model_dump(exclude={"utente_username", "utente_password"})
        dati_dict["utente_id"] = nuovo_utente.utente_id

        # Crea il Cliente
        nuovo_cliente = Cliente(**dati_dict)
        db.add(nuovo_cliente)
        
        db.commit()
        db.refresh(nuovo_cliente)
        
        return {
            "message": "Cliente e utente creati con successo!", 
            "cliente_id": nuovo_cliente.cliente_id,
            "utente_id": nuovo_utente.utente_id,
            "username_generato": username,
            "password_generata": password
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

#GET ALL (paginazione a 50)
@router.get("/", response_model=List[ClienteResponse])
def leggi_clienti(
    skip: int = 0, 
    limit: int = 50, 
    search: Optional[str] = None, 
    ruolo_codice: Optional[str] = None,
    solo_attuatori: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Cliente).options(
        joinedload(Cliente.azienda),
        joinedload(Cliente.ruolo))

    if ruolo_codice or solo_attuatori:
        query = query.join(Ruolo, Cliente.cliente_ruolo == Ruolo.ruolo_id)
        
    if ruolo_codice:
        query = query.filter(Ruolo.ruolo_codice == ruolo_codice)
    elif solo_attuatori:
        query = query.filter(Ruolo.ruolo_codice.in_(["Nazionale", "Regionale", "Provinciale", "Aderente"]))
    
    if search:
        search_term = f"{search}%"
        if solo_attuatori:
            query = query.outerjoin(Cliente.azienda)
            query = query.filter(
                (Cliente.cliente_nome.ilike(search_term)) | 
                (Cliente.cliente_cognome.ilike(search_term)) |
                (Azienda.azienda_ragione_sociale.ilike(search_term))
            )
        else:
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

