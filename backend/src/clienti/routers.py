from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from src.clienti.models import Cliente
from src.clienti.schemas import ClienteCreate, ClienteResponse, ClienteConUtenteCreate
from src.universita.schemas import UniversitaBase
from src.database import get_db
from typing import Optional
from src.ruolo.models import Ruolo
from src.aziende.models import Azienda
from src.universita.models import Universita
from src.utenti.models import Utente
import uuid
from datetime import date
from src.auth.dipendenze import get_current_utente
from src.security.password import hash_password, messaggi_policy, verifica_policy_password


router = APIRouter(prefix="/clienti", tags=["Clienti"])

#POST
@router.post("/con-utente", status_code=status.HTTP_201_CREATED)
def crea_cliente_e_utente(
    dati: ClienteConUtenteCreate, 
    tipo_utente: str = "sottoscrittore",
    db: Session = Depends(get_db),
    current_utente = Depends(get_current_utente)
):

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
        # Crea prima l'Utente temporaneo per ottenere l'ID
        nuovo_utente = Utente(
            utente_username="temp",
            utente_password="",
            utente_password_hash="",
            utente_attivoSN=1
        )
        db.add(nuovo_utente)
        db.flush() # Genera utente_id

        # Genera Username e Password definitivi (con iniziali maiuscole)
        nome = dati.cliente_nome.strip()
        cognome = dati.cliente_cognome.strip()
        
        username = f"{nome.capitalize()}{cognome.capitalize()}"
        password_inChiaro = f"{nome[:3]}{cognome[:3]}{nuovo_utente.utente_id}"

        violate = verifica_policy_password(password_inChiaro, username=username)
        if violate:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "codice": "policy_password",
                    "regole_violate": violate,
                    "messaggi": messaggi_policy(violate),
                },
            )
        
        id_corrente = current_utente.utente_id

        nuovo_utente.utente_username = username
        nuovo_utente.utente_created_by = id_corrente
        nuovo_utente.utente_updated_by = id_corrente
        nuovo_utente.utente_padre = id_corrente
        nuovo_utente.utente_password_hash = hash_password(password_inChiaro)
        nuovo_utente.utente_password_algo = "bcrypt"
        nuovo_utente.utente_password = ""  # Mai in chiaro
        nuovo_utente.utente_salt = str(uuid.uuid4())

        # Isola i campi del cliente escludendo utente temporaneo e campi università
        campi_universita_keys = set(UniversitaBase.model_fields.keys())
        dati_cliente_dict = dati.model_dump(
            exclude={"utente_username", "utente_password"}.union(campi_universita_keys)
        )
        dati_cliente_dict["utente_id"] = nuovo_utente.utente_id

        # Campi default in base al tipo di utente
        base_abilitazioni = -1 if tipo_utente.lower() == "attuatore" else 0

        campi_abilitazioni = [
            "cliente_abilPraticheUniv",
            "cliente_abilitazione_ecampus",
            "cliente_abilitazione_link_campus",
            "cliente_abilitazione_corsi_speciali",
            "cliente_abilitazione_a4u"
        ]
        
        for campo in campi_abilitazioni:
            if dati_cliente_dict.get(campo) is None:
                if campo == "cliente_abilitazione_corsi_speciali":
                    dati_cliente_dict[campo] = 0
                else:
                    dati_cliente_dict[campo] = base_abilitazioni

        # Crea il Cliente
        nuovo_cliente = Cliente(**dati_cliente_dict)
        db.add(nuovo_cliente)
        db.flush() # Genera cliente_id indispensabile per l'università

        # Estrai e crea il record dell'Università collegata
        dati_universita_dict = dati.model_dump(include=campi_universita_keys)
        dati_universita_dict["cliente_id"] = nuovo_cliente.cliente_id
        dati_universita_dict["universita_createBy"] = current_utente.utente_id

        # Elenco esatto delle sole colonne TINYINT/INT obbligatorie nel DB (Null: "NO")[cite: 1]
        campi_obbligatori_tinyint = [
            "universita_immatricolato",
            "universita_iscrizioneAltraUniversita",
            "universita_attivita_professionalizzanti",
            "universita_corsi_di_formazione",
            "universita_altre_attivita_certificate"
        ]

        # Forziamo il valore a 0 per i tinyint obbligatori
        for chiave in campi_obbligatori_tinyint:
            valore = dati_universita_dict.get(chiave)
            if valore is None or valore == "" or valore is False or valore == "false":
                dati_universita_dict[chiave] = 0
            elif valore is True or valore == "true" or valore == 1 or valore == "1":
                dati_universita_dict[chiave] = 1
            else:
                dati_universita_dict[chiave] = 0

        # Campi numerici interi aggiornati (inclusi i voti e l'anno sessione professione)[cite: 1]
        campi_numerici_interi = {
            "universita_votoRicevuto_diploma", "universita_votoMassimo_diploma",
            "universita_votoRicevuto_ai", "universita_votoMassimo_ai",
            "universita_votoRicevuto_titolo", "universita_votoMassimo_titolo",
            "universita_percentualeInvalidita", "universita_voto_professione",
            "universita_annoSessione_professione"
        }

        # Campi data
        campi_data = {
            k for k in dati_universita_dict.keys() 
            if "data" in k.lower() or k.endswith("_data")
        }

        # Pulizia mirata per tutti gli altri campi opzionali
        for chiave, valore in dati_universita_dict.items():
            if chiave in campi_obbligatori_tinyint:
                continue
            if valore is None or valore == "":
                if chiave in campi_numerici_interi:
                    dati_universita_dict[chiave] = None # Oppure 0 se preferisci default a zero
                elif chiave in campi_data:
                    dati_universita_dict[chiave] = None
                else:
                    dati_universita_dict[chiave] = None # Per le stringhe opzionali nel DB è meglio salvare NULL anziché stringa vuota

        dati_universita_dict["universita_createDate"] = date.today()
        dati_universita_dict["universita_updateDate"] = date.today()

        nuova_universita = Universita(**dati_universita_dict)
        db.add(nuova_universita)
        
        db.commit()
        db.refresh(nuovo_cliente)
        
        return {
            "message": "Cliente, utente e dati università creati con successo!", 
            "cliente_id": nuovo_cliente.cliente_id,
            "utente_id": nuovo_utente.utente_id,
            "username_generato": username,
            "password_generata": password_inChiaro
        }

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")



# GET ALL (paginazione a 50)
@router.get("/", response_model=List[ClienteResponse])
def leggi_clienti(
    skip: int = 0, 
    limit: int = 50, 
    search: Optional[str] = None, 
    ruolo_codice: Optional[str] = None,
    solo_attuatori: bool = False,
    solo_utenti: bool = False, 
    db: Session = Depends(get_db)
):
    query = db.query(Cliente).options(
        joinedload(Cliente.azienda),
        joinedload(Cliente.ruolo))

    
    if ruolo_codice or solo_attuatori or solo_utenti:
        query = query.join(Ruolo, Cliente.cliente_ruolo == Ruolo.ruolo_id)
        
    if ruolo_codice:
        query = query.filter(Ruolo.ruolo_codice == ruolo_codice)
    elif solo_attuatori:
        query = query.filter(Ruolo.ruolo_codice.in_(["Nazionale", "Regionale", "Provinciale", "Aderente"]))
    elif solo_utenti: # <--- 3. Gestiamo il filtro per i soli utenti
        query = query.filter(Ruolo.ruolo_codice == "Utente")
    
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
    db_cliente = (
        db.query(Cliente)
        .options(
            joinedload(Cliente.azienda),
            joinedload(Cliente.ruolo),
            joinedload(Cliente.utente).joinedload(Utente.padre)
        )
        .filter(Cliente.cliente_id == cliente_id)
        .first()
    )
    
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

