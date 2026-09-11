import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from src.auth.dipendenze import get_current_utente
from src.aziende.models import Azienda
from src.clienti.models import Cliente
from src.clienti.schemas import (
    ClienteDettaglioResponse,
    ClienteResponse,
    ClienteConUtenteCreate,
    ClienteUpdate,
)
from src.clienti.servizio import TipoUtente, crea_cliente_con_utente
from src.database import get_db
from src.ruolo.models import Ruolo
from src.universita.models import Universita
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.clienti")

# L'autenticazione e' una dipendenza del router, non del singolo endpoint:
# quando era per endpoint, 3 rotte su 4 se ne sono dimenticate - fra cui il PUT,
# che modifica cliente_ruolo e le abilitazioni.
router = APIRouter(
    prefix="/clienti",
    tags=["Clienti"],
    dependencies=[Depends(get_current_utente)],
)

# ClienteResponse annida UtenteResponse, che a sua volta annida padre e
# aggiornato_da: senza questi joinedload una pagina da 40 costava 121 query.
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
    # Era `str` libero: ?tipo_utente=Attuatorre cadeva in silenzio nel ramo
    # sottoscrittore. Come Enum, FastAPI risponde 422 con i valori ammessi.
    tipo_utente: TipoUtente = TipoUtente.SOTTOSCRITTORE,
    db: Session = Depends(get_db),
    current_utente=Depends(get_current_utente),
):
    """Crea in una transazione la riga utenti, la riga clienti e il curriculum.

    Il corpo di questa funzione era di 188 righe con otto responsabilita'; ora
    sta in src/clienti/servizio.py, diviso in funzioni con un nome e due delle
    quali pure. Qui restano solo l'orchestrazione e la traduzione degli errori.
    """
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
        # Prima era detail=f"Errore: {str(e)}": il client riceveva nomi di
        # tabella, di colonna e il testo SQL, e l'eccezione originale veniva
        # distrutta, rendendo impossibile diagnosticare un guasto reale.
        logger.exception(
            "creazione cliente fallita, richiesta da utente_id=%s",
            current_utente.utente_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Creazione non riuscita. Riprova, e se persiste segnala l'errore.",
        )

    return {
        "message": "Cliente, utente e dati università creati con successo!",
        "cliente_id": esito["cliente"].cliente_id,
        "utente_id": esito["utente"].utente_id,
        "username_generato": esito["utente"].utente_username,
        # Unica occasione in cui questa password esiste in chiaro: nel database
        # c'e' solo l'hash. Se il chiamante non la mostra all'operatore,
        # l'account resta inutilizzabile. Il frontend la presenta in un
        # riquadro da annotare prima di proseguire.
        "password_generata": esito["password_in_chiaro"],
        "avviso": "Annota queste credenziali: la password non sarà più recuperabile.",
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
    """Aggiornamento parziale di anagrafica e curriculum.

    Due difetti chiusi qui. Il primo: model_dump() senza exclude_unset
    riscriveva ogni campo omesso col default dello schema, quindi un
    salvataggio dalla scheda declassava un attuatore a ruolo 0 e gli faceva
    perdere azienda e associazioni. Il secondo: lo schema era ClienteCreate,
    che non ha i campi universita_*, quindi il curriculum inviato dal form
    veniva scartato in silenzio e la risposta era comunque 200.
    """
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
    # cliente_id compare in UniversitaBase: qui identifica la riga, non un
    # campo da riscrivere.
    campi_curriculum.pop("cliente_id", None)
    campi_cliente.pop("cliente_id", None)

    try:
        for chiave, valore in campi_cliente.items():
            setattr(db_cliente, chiave, valore)

        if campi_curriculum:
            curriculum = db_cliente.curriculum
            if curriculum is None:
                # Un cliente creato prima che il curriculum esistesse: si crea
                # ora, invece di perdere quanto l'operatore ha appena scritto.
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
