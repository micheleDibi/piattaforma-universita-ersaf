from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional

from src.auth.dipendenze import get_current_utente
from src.database import get_db
from src.aziende.models import Azienda, AderenteDettaglio
from src.aziende.schemas import AziendaCreate, AziendaResponse, AziendaUpdate, AderenteDettaglioBase, AderenteDettaglioResponse, AderenteDettaglioUpdate
from src.aziende_xcod.models import AziendaXCod
from src.aziende_xcod.servizi import aziende_visibili_ids, padre_id_di
import datetime
from src.auth.servizio_login import cliente_principale


# L'autenticazione e' una dipendenza del router, non del singolo endpoint:
# quando era per endpoint, 4 rotte su 4 se ne sono dimenticate.
# Chi aggiunge una rotta qui la trova protetta senza doverci pensare; se una
# rotta dovra' essere pubblica lo si dichiara esplicitamente con
# dependencies=[] su quel decoratore.
router = APIRouter(
    prefix="/aziende",
    tags=["Aziende"],
    dependencies=[Depends(get_current_utente)],
)

# (attributo, testo del messaggio). Il database non ha alcuna UNIQUE su queste
# colonne - e ne contiene gia' duplicati - quindi il vincolo esiste solo qui:
# e' una regola applicativa, non una garanzia.
_CAMPI_UNICI = (
    ("azienda_codiceFiscale", "questo Codice Fiscale"),
    ("azienda_partitaIVA", "questa Partita IVA"),
    ("azienda_ragione_sociale", "questa Ragione Sociale"),
    ("azienda_email", "questa Email"),
    ("azienda_pec", "questa PEC"),
    ("azienda_telefono", "questo Telefono"),
    ("azienda_iban", "questo IBAN"),
)


def _verifica_unicita(db: Session, valori: dict, escludi_id: Optional[int] = None) -> None:
    """Una sola query al posto di sette SELECT sequenziali.

    Erano sette round-trip su colonne senza indice, uno per campo, e ognuno
    apriva la sua finestra TOCTOU. Qui la finestra resta - senza UNIQUE nel
    database non si puo' chiudere - ma e' una sola e costa una query.

    `valori` contiene solo i campi effettivamente inviati: in un aggiornamento
    parziale non si deve controllare un campo che il chiamante non ha toccato,
    altrimenti le aziende che condividono gia' una PEC con un'altra riga
    diventerebbero immodificabili.
    """
    condizioni = [
        getattr(Azienda, attributo) == valori[attributo]
        for attributo, _ in _CAMPI_UNICI
        if valori.get(attributo)
    ]
    if not condizioni:
        return

    query = db.query(Azienda).filter(or_(*condizioni))
    if escludi_id is not None:
        query = query.filter(Azienda.azienda_id != escludi_id)

    for esistente in query.all():
        for attributo, etichetta in _CAMPI_UNICI:
            atteso = valori.get(attributo)
            if atteso and getattr(esistente, attributo) == atteso:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Esiste già un'azienda con {etichetta}.",
                )


def _azienda_o_404(db: Session, azienda_id: int, visibili: Optional[set[int]] = None) -> Azienda:
    # Se non e' visibile per l'utente corrente si risponde 404 come se non
    # esistesse, non 403: evita di rivelare l'esistenza di aziende fuori dal
    # proprio ramo di gerarchia.
    if visibili is not None and azienda_id not in visibili:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Azienda non trovata.")
    azienda = db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first()
    if not azienda:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Azienda non trovata.")
    return azienda

def _azienda_o_404(db: Session, azienda_id: int, visibili: Optional[set[int]] = None) -> Azienda:
    # Se non e' visibile per l'utente corrente si risponde 404 come se non
    # esistesse, non 403: evita di rivelare l'esistenza di aziende fuori dal
    # proprio ramo di gerarchia.
    if visibili is not None and azienda_id not in visibili:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Azienda non trovata.")
    azienda = db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first()
    if not azienda:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Azienda non trovata.")
    return azienda


def _verifica_percentuali_non_superano_padre(db: Session, azienda_id: int, valori: dict) -> None:
    """Regola 1 della gerarchia: un'azienda non può avere percentuali
    superiori a quelle del proprio padre. Un'azienda radice (senza padre)
    non ha alcun tetto."""
    padre_id = padre_id_di(db, azienda_id)
    if padre_id is None:
        return

    padre_dettaglio = (
        db.query(AderenteDettaglio)
        .filter(AderenteDettaglio.azienda_id == padre_id)
        .first()
    )
    for campo in AderenteDettaglioBase.model_fields:
        limite = getattr(padre_dettaglio, campo, 0) if padre_dettaglio else 0
        if valori.get(campo, 0) > limite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La percentuale '{campo}' supera quella del padre ({limite}).",
            )


#POST
@router.post("/", response_model=AziendaResponse, status_code=status.HTTP_201_CREATED)
def crea_azienda(
    azienda_in: AziendaCreate,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    _verifica_unicita(db, azienda_in.model_dump())

    nuova_azienda = Azienda(**azienda_in.model_dump())
    db.add(nuova_azienda)
    db.commit()
    db.refresh(nuova_azienda)

    cliente_creatore = cliente_principale(db, utente_corrente.utente_id)
    padre_id = getattr(cliente_creatore, "azienda_id", None) if cliente_creatore else None

    ora = datetime.datetime.utcnow()
    db.add(AziendaXCod(
        azienda_padre_id=padre_id,
        azienda_figlia_id=nuova_azienda.azienda_id,
        azienda_xCod_created_by=utente_corrente.utente_id,
        azienda_xCod_created_at=ora,
        azienda_xCod_updated_by=utente_corrente.utente_id,
        azienda_xCod_updated_at=ora,
    ))
    db.commit()

    return nuova_azienda


#GET ALL
@router.get("/", response_model=List[AziendaResponse])
def lista_aziende(
    skip: int = Query(0, ge=0),
    limit: int = Query(40, ge=1, le=200),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    query = db.query(Azienda)
    if search:
        query = query.filter(Azienda.azienda_ragione_sociale.ilike(f"{search}%"))

    visibili = aziende_visibili_ids(db, utente_corrente)
    if visibili is not None:
        query = query.filter(Azienda.azienda_id.in_(visibili))

    return (
        query.order_by(Azienda.azienda_id.asc()).offset(skip).limit(limit).all()
    )


#Get P IVA
@router.get("/cerca-per-piva", response_model=AziendaResponse)
def cerca_azienda_per_piva(
    partita_iva: str = Query(..., min_length=11, max_length=11),
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    query = db.query(Azienda).filter(Azienda.azienda_partitaIVA == partita_iva)

    visibili = aziende_visibili_ids(db, utente_corrente)
    if visibili is not None:
        query = query.filter(Azienda.azienda_id.in_(visibili))

    azienda = query.first()
    if not azienda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessuna azienda trovata con questa Partita IVA.",
        )
    return azienda


#GET BY ID
@router.get("/{azienda_id}", response_model=AziendaResponse)
def dettaglio_azienda(
    azienda_id: int,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    return _azienda_o_404(db, azienda_id, aziende_visibili_ids(db, utente_corrente))


#PUT
@router.put("/{azienda_id}", response_model=AziendaResponse)
def aggiorna_azienda(
    azienda_id: int,
    azienda_in: AziendaUpdate,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    azienda = _azienda_o_404(db, azienda_id, aziende_visibili_ids(db, utente_corrente))

    modifiche = azienda_in.model_dump(exclude_unset=True)
    _verifica_unicita(db, modifiche, escludi_id=azienda_id)

    for chiave, valore in modifiche.items():
        setattr(azienda, chiave, valore)

    db.commit()
    db.refresh(azienda)
    return azienda


@router.get("/{azienda_id}/dettagli", response_model=AderenteDettaglioResponse)
def dettaglio_azienda_percentuali(
    azienda_id: int,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    _azienda_o_404(db, azienda_id, aziende_visibili_ids(db, utente_corrente))
    return _dettaglio_o_nuovo(db, azienda_id)


@router.put("/{azienda_id}/dettagli", response_model=AderenteDettaglioResponse)
def aggiorna_dettaglio_azienda(
    azienda_id: int,
    dettaglio_in: AderenteDettaglioUpdate,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    _azienda_o_404(db, azienda_id, aziende_visibili_ids(db, utente_corrente))

    valori = dettaglio_in.model_dump()
    _verifica_percentuali_non_superano_padre(db, azienda_id, valori)

    dettaglio = _dettaglio_o_nuovo(db, azienda_id)
    for chiave, valore in valori.items():
        setattr(dettaglio, chiave, valore)

    db.add(dettaglio)
    db.commit()
    db.refresh(dettaglio)
    return dettaglio