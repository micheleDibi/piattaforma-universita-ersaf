from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from src.auth.dipendenze import get_current_utente
from src.database import get_db
from src.pratiche.models import Pratica, PraticaCreate, PraticaResponse, PraticaUpdate

# Stessa scelta di aziende/routers.py: autenticazione a livello di router,
# non di singolo endpoint, cosi' una rotta nuova la trova gia' protetta.
router = APIRouter(
    prefix="/pratiche",
    tags=["Pratiche"],
    dependencies=[Depends(get_current_utente)],
)

# joinedload sulle relazioni che PraticaResponse.estrai_relazioni legge per
# popolare cliente_nome_completo / pratica_stato_descrizione / listTesta_descrizione.
# Senza, quei tre campi restano None in risposta (niente errori, ma la tabella
# del frontend mostrerebbe solo id).
_RELAZIONI_ELENCO = (
    joinedload(Pratica.cliente),
    joinedload(Pratica.stato),
    joinedload(Pratica.listino_testa),
)


def _pratica_o_404(db: Session, pratica_id: int) -> Pratica:
    pratica = (
        db.query(Pratica)
        .options(*_RELAZIONI_ELENCO)
        .filter(Pratica.pratica_id == pratica_id)
        .first()
    )
    if not pratica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pratica non trovata.",
        )
    return pratica


# POST
@router.post("/", response_model=PraticaResponse, status_code=status.HTTP_201_CREATED)
def crea_pratica(pratica_in: PraticaCreate, db: Session = Depends(get_db)):
    # exclude_unset=True e' OBBLIGATORIO qui, a differenza di crea_azienda:
    # molti campi di PraticaCreate (listTesta_id, cliente_id, pratica_stato_id,
    # nome_universita_id, cliente_emittente_aderente_id, pratica_prezzo, tutti
    # i missFlag/rinn...) sono Optional=None nello schema perche' a database
    # hanno un server_default. Un model_dump() completo passerebbe None
    # esplicito per i campi non inviati, e SQLAlchemy scriverebbe NULL invece
    # di lasciar agire il DEFAULT del database - lo stesso bug descritto nei
    # commenti di Cliente/Azienda sui server_default.
    dati = pratica_in.model_dump(exclude_unset=True)

    nuova_pratica = Pratica(**dati)
    db.add(nuova_pratica)
    db.commit()
    db.refresh(nuova_pratica)
    return _pratica_o_404(db, nuova_pratica.pratica_id)


# GET ALL
@router.get("/", response_model=List[PraticaResponse])
def lista_pratiche(
    skip: int = Query(0, ge=0),
    limit: int = Query(40, ge=1, le=200),
    search: Optional[str] = None,
    cliente_id: Optional[int] = None,
    pratica_stato_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Pratica).options(*_RELAZIONI_ELENCO)

    # Ricerca per numero pratica: e' l'unico campo testuale "identificativo"
    # su Pratica stessa. Se serve anche cercare per nome/cognome cliente,
    # va aggiunto un join esplicito su Cliente qui.
    if search:
        query = query.filter(Pratica.pratica_numero.ilike(f"%{search}%"))
    if cliente_id is not None:
        query = query.filter(Pratica.cliente_id == cliente_id)
    if pratica_stato_id is not None:
        query = query.filter(Pratica.pratica_stato_id == pratica_stato_id)

    # Piu' recenti prima: a differenza di ElencoAziende (ordine alfabetico
    # naturale sulla ragione sociale), per un elenco di pratiche ha piu' senso
    # vedere prima quelle create per ultime. Se preferisci l'ordine per id
    # crescente come in aziende, cambia .desc() in .asc().
    return (
        query.order_by(Pratica.pratica_id.desc()).offset(skip).limit(limit).all()
    )


# GET BY ID
@router.get("/{pratica_id}", response_model=PraticaResponse)
def dettaglio_pratica(pratica_id: int, db: Session = Depends(get_db)):
    return _pratica_o_404(db, pratica_id)


# PUT
@router.put("/{pratica_id}", response_model=PraticaResponse)
def aggiorna_pratica(
    pratica_id: int, pratica_in: PraticaUpdate, db: Session = Depends(get_db)
):
    pratica = _pratica_o_404(db, pratica_id)

    # exclude_unset=True: stesso motivo di aggiorna_azienda, un campo non
    # inviato non deve essere riscritto con un default dello schema.
    modifiche = pratica_in.model_dump(exclude_unset=True)

    for chiave, valore in modifiche.items():
        setattr(pratica, chiave, valore)

    db.commit()
    db.refresh(pratica)
    return _pratica_o_404(db, pratica_id)