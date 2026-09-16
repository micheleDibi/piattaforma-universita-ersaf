import logging
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session, joinedload

from src.auth.dipendenze import get_current_utente

from src.aziende.models import Azienda
from src.clienti.models import Cliente
from src.clienti.schemas import (
    ClienteDettaglioResponse,
    ClienteResponse,
    ClienteConUtenteCreate,
    ClienteUpdate,
    PermessiPraticheResponse,
)
from src.clienti.servizio import (
    TipoUtente,
    crea_cliente_con_utente,
)

from src.database import get_db

from src.ruolo.models import Ruolo
from src.universita.models import Universita
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.clienti")

router = APIRouter(
    prefix="/clienti",
    tags=["Clienti"],
    dependencies=[Depends(get_current_utente)],
)

@router.get("/permessi-pratiche", response_model=PermessiPraticheResponse)
def permessi_pratiche_correnti(current_utente=Depends(get_current_utente)):
    cliente: Cliente = current_utente.clienti
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessun cliente associato a questo utente.",
        )
    return PermessiPraticheResponse(
        abilPraticheUniv=bool(cliente.cliente_abilPraticheUniv),
        ecampus=bool(cliente.cliente_abilitazione_ecampus),
        link_campus=bool(cliente.cliente_abilitazione_link_campus),
        corsi_speciali=bool(cliente.cliente_abilitazione_corsi_speciali),
        a4u=bool(cliente.cliente_abilitazione_a4u),
    )

_CARICAMENTO_ELENCO = (
    joinedload(Cliente.azienda),
    joinedload(Cliente.ruolo),
    joinedload(Cliente.utente).joinedload(Utente.padre).selectinload(Utente.clienti),
    joinedload(Cliente.utente).joinedload(Utente.aggiornato_da).selectinload(Utente.clienti),
)


def _cliente_o_404(db: Session, cliente_id: int, con_curriculum: bool = False) -> Cliente:
    caricamento = list(_CARICAMENTO_ELENCO)
    if con_curriculum:
        caricamento.append(joinedload(Cliente.universita))

    db_cliente = (
        db.query(Cliente)
        .options(*caricamento)
        .filter(Cliente.cliente_id == cliente_id)
        .first()
    )
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente non trovato"
        )
    return db_cliente


#POST
@router.post("/con-utente", status_code=status.HTTP_201_CREATED)
def crea_cliente_e_utente(
    dati: ClienteConUtenteCreate,
    tipo_utente: TipoUtente = TipoUtente.SOTTOSCRITTORE,
    db: Session = Depends(get_db),
    current_utente=Depends(get_current_utente),
):
    """Crea in una transazione la riga utenti (disattivata), la riga clienti
    e il curriculum. L'utente si attiva dopo la verifica di email e cellulare."""
    try:
        esito = crea_cliente_con_utente(
            db, dati.model_dump(), tipo_utente, current_utente.utente_id
        )
        db.commit()
        db.refresh(esito["cliente"])
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception(
            "creazione cliente fallita, richiesta da utente_id=%s",
            current_utente.utente_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Creazione non riuscita. Riprova, e se persiste segnala l'errore.",
        )

    return {
        "message": "Cliente e utente creati. L'account resta disattivato finché email e cellulare non sono verificati.",
        "cliente_id": esito["cliente"].cliente_id,
        "utente_id": esito["utente"].utente_id,
        "username_generato": esito["utente"].utente_username,
    }


# GET ALL (paginazione a 50)
@router.get("/", response_model=List[ClienteResponse])
def leggi_clienti(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    ruolo_codice: Optional[str] = None,
    solo_attuatori: bool = False,
    solo_utenti: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(Cliente).options(*_CARICAMENTO_ELENCO)

    if ruolo_codice or solo_attuatori or solo_utenti:
        query = query.join(Ruolo, Cliente.cliente_ruolo == Ruolo.ruolo_id)

    if ruolo_codice:
        query = query.filter(Ruolo.ruolo_codice == ruolo_codice)
    elif solo_attuatori:
        query = query.filter(
            Ruolo.ruolo_codice.in_(
                ["Nazionale", "Regionale", "Provinciale", "Aderente"]
            )
        )
    elif solo_utenti:
        query = query.filter(Ruolo.ruolo_codice == "Utente")

    if search:
        parole = search.split()
        if solo_attuatori:
            query = query.outerjoin(Cliente.azienda)
            for parola in parole:
                termine = f"%{parola}%"
                query = query.filter(
                    (Cliente.cliente_nome.ilike(termine))
                    | (Cliente.cliente_cognome.ilike(termine))
                    | (Azienda.azienda_ragione_sociale.ilike(termine))
                )
        else:
            for parola in parole:
                termine = f"%{parola}%"
                query = query.filter(
                    (Cliente.cliente_nome.ilike(termine))
                    | (Cliente.cliente_cognome.ilike(termine))
                )

    return query.order_by(Cliente.cliente_id.asc()).offset(skip).limit(limit).all()


#GET BY ID
@router.get("/{cliente_id}", response_model=ClienteDettaglioResponse)
def leggi_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return _cliente_o_404(db, cliente_id, con_curriculum=True)


#PUT
@router.put("/{cliente_id}", response_model=ClienteDettaglioResponse)
def aggiorna_cliente(
    cliente_id: int,
    modifiche: ClienteUpdate,
    db: Session = Depends(get_db),
    current_utente=Depends(get_current_utente),
):
    from src.otp.servizio import blocca_cliente
    blocca_cliente(db, cliente_id)
    db_cliente = _cliente_o_404(db, cliente_id, con_curriculum=True)

    inviati = modifiche.model_dump(exclude_unset=True)
    campi_curriculum = {
        chiave: valore
        for chiave, valore in inviati.items()
        if chiave.startswith("universita_")
    }
    campi_cliente = {
        chiave: valore
        for chiave, valore in inviati.items()
        if not chiave.startswith("universita_")
    }

    CAMPI_STRINGA_NOT_NULL = {
        "cliente_codice", "cliente_nome", "cliente_cognome", "cliente_email",
        "cliente_telefono", "cliente_indirizzo", "cliente_civico", "cliente_citta",
        "cliente_CAP", "cliente_provincia", "cliente_luogoNascita",
        "cliente_provinciaNascita", "cliente_cittadinanza", "cliente_tipoDocumento",
        "cliente_documento", "cliente_comuneRilascio", "cliente_sesso",
    }

    for chiave in CAMPI_STRINGA_NOT_NULL:
        if campi_cliente.get(chiave) is None and chiave in campi_cliente:
            campi_cliente[chiave] = ""


    campi_curriculum.pop("cliente_id", None)
    campi_cliente.pop("cliente_id", None)
    campi_cliente.pop("utente_id", None)

    try:
        from sqlalchemy import delete, update
        from src.otp.models import ContattoVerificato, Sfida
        for tipo in ("email", "cellulare"):
            campo_contatto = "cliente_" + tipo
            if campo_contatto in campi_cliente and campi_cliente[campo_contatto] != getattr(db_cliente, campo_contatto):
                db.execute(delete(ContattoVerificato).where(ContattoVerificato.cliente_id == cliente_id, ContattoVerificato.tipo == tipo))
                tipi = [tipo, "login"] if tipo == "email" else [tipo]
                db.execute(update(Sfida).where(Sfida.cliente_id == cliente_id, Sfida.tipo.in_(tipi)).values(stato="superato"))
        for chiave, valore in campi_cliente.items():
            setattr(db_cliente, chiave, valore)

        if campi_curriculum:
            curriculum = db_cliente.curriculum
            if curriculum is None:
                curriculum = Universita(
                    cliente_id=db_cliente.cliente_id,
                    universita_createBy=current_utente.utente_id,
                )
                db.add(curriculum)
            for chiave, valore in campi_curriculum.items():
                setattr(curriculum, chiave, valore)
            curriculum.universita_updateBy = current_utente.utente_id

        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception(
            "aggiornamento cliente_id=%s fallito, richiesto da utente_id=%s",
            cliente_id,
            current_utente.utente_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Salvataggio non riuscito. Riprova, e se persiste segnala l'errore.",
        )

    db.refresh(db_cliente)
    return db_cliente
