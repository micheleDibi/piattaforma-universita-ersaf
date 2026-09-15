from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional

from src.auth.dipendenze import get_current_utente
from src.database import get_db
from src.aziende.models import Azienda, AderenteDettaglio
from src.aziende.schemas import AziendaCreate, AziendaResponse, AziendaUpdate, AderenteDettaglioBase, AderenteDettaglioResponse, AderenteDettaglioUpdate


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


def _azienda_o_404(db: Session, azienda_id: int) -> Azienda:
    azienda = db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first()
    if not azienda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Azienda non trovata.",
        )
    return azienda


#POST
@router.post("/", response_model=AziendaResponse, status_code=status.HTTP_201_CREATED)
def crea_azienda(azienda_in: AziendaCreate, db: Session = Depends(get_db)):
    _verifica_unicita(db, azienda_in.model_dump())

    nuova_azienda = Azienda(**azienda_in.model_dump())
    db.add(nuova_azienda)
    db.commit()
    db.refresh(nuova_azienda)
    return nuova_azienda


#GET ALL
@router.get("/", response_model=List[AziendaResponse])
def lista_aziende(
    skip: int = Query(0, ge=0),
    # Un tetto esplicito: prima ?limit=10000000 scaricava l'intera tabella.
    limit: int = Query(40, ge=1, le=200),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Azienda)
    if search:
        query = query.filter(Azienda.azienda_ragione_sociale.ilike(f"{search}%"))

    # Senza ORDER BY, MySQL non garantisce l'ordine fra una pagina e la
    # successiva: lo scroll infinito di ElencoAziende poteva ripetere o saltare
    # righe.
    return (
        query.order_by(Azienda.azienda_id.asc()).offset(skip).limit(limit).all()
    )

#Get P IVA
@router.get("/cerca-per-piva", response_model=AziendaResponse)
def cerca_azienda_per_piva(
    partita_iva: str = Query(..., min_length=11, max_length=11),
    db: Session = Depends(get_db),
):
    """Match esatto, non ilike: usata dal flusso di associazione azienda-
    attuatore, dove un risultato ambiguo rischierebbe di agganciare l'azienda
    sbagliata. 404 (non una lista vuota) cosi' il frontend distingue
    "nessun risultato, proponi la creazione" da un errore generico.
    """
    azienda = (
        db.query(Azienda)
        .filter(Azienda.azienda_partitaIVA == partita_iva)
        .first()
    )
    if not azienda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessuna azienda trovata con questa Partita IVA.",
        )
    return azienda


#GET BY ID
@router.get("/{azienda_id}", response_model=AziendaResponse)
def dettaglio_azienda(azienda_id: int, db: Session = Depends(get_db)):
    return _azienda_o_404(db, azienda_id)


#PUT
@router.put("/{azienda_id}", response_model=AziendaResponse)
def aggiorna_azienda(
    azienda_id: int, azienda_in: AziendaUpdate, db: Session = Depends(get_db)
):
    azienda = _azienda_o_404(db, azienda_id)

    # exclude_unset=True: senza, ogni campo non inviato veniva riscritto con il
    # default dello schema, e su CAP, provincia, via, citta' e partita IVA -
    # NOT NULL nel database - il risultato era un 500.
    modifiche = azienda_in.model_dump(exclude_unset=True)
    _verifica_unicita(db, modifiche, escludi_id=azienda_id)

    for chiave, valore in modifiche.items():
        setattr(azienda, chiave, valore)

    db.commit()
    db.refresh(azienda)
    return azienda



def _dettaglio_o_nuovo(db: Session, azienda_id: int) -> AderenteDettaglio:
    """azienda_id non ha una UNIQUE, quindi in teoria potrebbero esserci piu'
    righe: qui si prende la prima, trattando la relazione come 1:1 (intento
    applicativo confermato via chat), o si costruisce un'istanza non ancora
    aggiunta alla sessione se non esiste."""
    dettaglio = (
        db.query(AderenteDettaglio)
        .filter(AderenteDettaglio.azienda_id == azienda_id)
        .first()
    )
    if dettaglio is None:
        # Un'istanza transiente non ha ancora i default lato server: quelli
        # (default=0) si applicano solo al flush, non alla costruzione
        # Python. Senza valorizzarli qui esplicitamente ogni percentuale
        # resterebbe None, e AderenteDettaglioResponse (campi int, non
        # Optional) rifiuterebbe la risposta con un 500 alla prima GET su
        # un'azienda senza dettaglio ancora salvato.
        dettaglio = AderenteDettaglio(
            azienda_id=azienda_id,
            **{campo: 0 for campo in AderenteDettaglioBase.model_fields},
        )
    return dettaglio

@router.get("/{azienda_id}/dettagli", response_model=AderenteDettaglioResponse)
def dettaglio_azienda_percentuali(azienda_id: int, db: Session = Depends(get_db)):
    _azienda_o_404(db, azienda_id)
    return _dettaglio_o_nuovo(db, azienda_id)


@router.put("/{azienda_id}/dettagli", response_model=AderenteDettaglioResponse)
def aggiorna_dettaglio_azienda(
    azienda_id: int,
    dettaglio_in: AderenteDettaglioUpdate,
    db: Session = Depends(get_db),
):
    _azienda_o_404(db, azienda_id)
    dettaglio = _dettaglio_o_nuovo(db, azienda_id)

    for chiave, valore in dettaglio_in.model_dump().items():
        setattr(dettaglio, chiave, valore)

    db.add(dettaglio)
    db.commit()
    db.refresh(dettaglio)
    return dettaglio