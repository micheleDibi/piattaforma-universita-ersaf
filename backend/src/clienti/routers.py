import logging
from typing import List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from sqlalchemy.orm import Session, joinedload

from src.auth.dipendenze import get_current_utente
from src.auth.models import ATTIVO
from src.auth.servizio_otp import (
    SCADENZA_MINUTI,
    codice_valido,
    marca_verificato,
    trova_per_cliente,
)
from src.aziende.models import Azienda
from src.clienti.models import Cliente
from src.clienti.schemas import (
    ClienteDettaglioResponse,
    ClienteResponse,
    ClienteConUtenteCreate,
    ClienteUpdate,
    VerificaOtpContattoRequest,
)
from src.clienti.servizio import (
    TipoUtente,
    attiva_utente_con_password,
    crea_cliente_con_utente,
)
from src.clienti.verifica_contatti import email_gia_verificata, genera_otp_email
from src.database import get_db
from src.notifiche.backend_invio import Mailer, get_mailer
from src.notifiche.email import (
    DatiInvioCredenziali,
    DatiInvioOtp,
    invia_mail_credenziali,
    invia_mail_otp,
)
from src.notifiche.models import CODICE_OTP_VERIFICA_EMAIL
from src.ruolo.models import Ruolo
from src.security.rete import ip_client, spacchetta_ip
from src.universita.models import Universita
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.clienti")

router = APIRouter(
    prefix="/clienti",
    tags=["Clienti"],
    dependencies=[Depends(get_current_utente)],
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
    e il curriculum. L'utente si attiva solo alla verifica email."""
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
        "message": "Cliente e utente creati. L'account resta disattivato finché l'email non viene verificata.",
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
        search_term = f"{search}%"
        if solo_attuatori:
            query = query.outerjoin(Cliente.azienda)
            query = query.filter(
                (Cliente.cliente_nome.ilike(search_term))
                | (Cliente.cliente_cognome.ilike(search_term))
                | (Azienda.azienda_ragione_sociale.ilike(search_term))
            )
        else:
            query = query.filter(
                (Cliente.cliente_nome.ilike(search_term))
                | (Cliente.cliente_cognome.ilike(search_term))
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
    campi_curriculum.pop("cliente_id", None)
    campi_cliente.pop("cliente_id", None)

    try:
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


# =============================================================================
# Verifica contatti (email)
# =============================================================================
@router.post("/{cliente_id}/contatti/email/genera-otp")
def genera_otp_email_cliente(
    cliente_id: int,
    request: Request,
    attivita: BackgroundTasks,
    db: Session = Depends(get_db),
    mailer: Mailer = Depends(get_mailer),
    current_utente=Depends(get_current_utente),
):
    cliente = _cliente_o_404(db, cliente_id)
    if not cliente.cliente_email:
        raise HTTPException(status_code=400, detail="Il cliente non ha un indirizzo email.")
    if email_gia_verificata(db, cliente):
        raise HTTPException(status_code=400, detail="L'email di questo cliente è già stata verificata.")

    sfida = genera_otp_email(
        db, cliente, autore_id=current_utente.utente_id, hostname=spacchetta_ip(ip_client(request))
    )
    db.commit()

    attivita.add_task(
        invia_mail_otp,
        mailer,
        DatiInvioOtp(
            log_otp_id=sfida.log_otp_id,
            destinatario=cliente.cliente_email,
            nome=f"{cliente.cliente_nome} {cliente.cliente_cognome}".strip() or cliente.cliente_email,
            codice=sfida.codice,
            scadenza_minuti=SCADENZA_MINUTI,
        ),
        codice_template=CODICE_OTP_VERIFICA_EMAIL,
    )

    return {"log_otp_id": sfida.log_otp_id, "otp_scadenza": sfida.scadenza.isoformat()}


@router.post("/{cliente_id}/contatti/email/verifica-otp")
def verifica_otp_email_cliente(
    cliente_id: int,
    corpo: VerificaOtpContattoRequest,
    attivita: BackgroundTasks,
    db: Session = Depends(get_db),
    mailer: Mailer = Depends(get_mailer),
    current_utente=Depends(get_current_utente),
):
    cliente = _cliente_o_404(db, cliente_id)
    riga = trova_per_cliente(db, cliente_id, corpo.log_otp_id)
    if not codice_valido(riga, corpo.otp_codice):
        raise HTTPException(status_code=401, detail="Codice OTP non valido o scaduto.")

    marca_verificato(riga)

    utente = db.get(Utente, cliente.utente_id)
    credenziali_inviate = False
    if utente is not None and utente.utente_attivoSN != ATTIVO:
        password_in_chiaro = attiva_utente_con_password(
            db, utente, cliente.cliente_nome, cliente.cliente_cognome
        )
        db.commit()
        attivita.add_task(
            invia_mail_credenziali,
            mailer,
            DatiInvioCredenziali(
                destinatario=cliente.cliente_email,
                nome=f"{cliente.cliente_nome} {cliente.cliente_cognome}".strip(),
                username=utente.utente_username,
                password=password_in_chiaro,
            ),
        )
        credenziali_inviate = True
    else:
        db.commit()

    return {"message": "Email verificata con successo.", "credenziali_inviate": credenziali_inviate}