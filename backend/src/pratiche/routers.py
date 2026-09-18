from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import Annotated, List

from src.auth.dipendenze import get_current_utente
from src.auth.visibilita import Visibilita, condizione_azienda, visibilita_corrente
from src.database import get_db
from src.pratiche.filtri import FiltriPratiche, query_filtrata
from src.pratiche.opzioni import router as opzioni_router
from src.documenti.rotte import router as documento_router
from src.pratiche.models import Pratica, PraticaCreate, PraticaResponse, PraticaUpdate

# Stessa scelta di aziende/routers.py: autenticazione a livello di router,
# non di singolo endpoint, cosi' una rotta nuova la trova gia' protetta.
router = APIRouter(
    prefix="/pratiche",
    tags=["Pratiche"],
    dependencies=[Depends(get_current_utente)],
)

router.include_router(opzioni_router)
# PDF della pratica: stesso prefisso e stessa autenticazione del dettaglio.
router.include_router(documento_router)

# joinedload sulle relazioni che PraticaResponse.estrai_relazioni legge per
# popolare cliente_nome_completo / pratica_stato_descrizione / listTesta_descrizione.
# Senza, quei tre campi restano None in risposta (niente errori, ma la tabella
# del frontend mostrerebbe solo id).
_RELAZIONI_ELENCO = (
    joinedload(Pratica.cliente),
    joinedload(Pratica.stato),
    joinedload(Pratica.listino_testa),
    joinedload(Pratica.universita),
    joinedload(Pratica.tipo_corso),
    # L'emittente si mostra anche se non e' fra i clienti visibili: la scheda
    # non deve piu' chiederlo a GET /clienti/{id}. Outer join (il default):
    # l'emittente non e' garantito.
    joinedload(Pratica.cliente_emittente_aderente),
)


AZIENDA_MANCANTE = "Per creare pratiche l'utente deve avere un'azienda associata."


def _pratica_o_404(db: Session, pratica_id: int, vis: Visibilita) -> Pratica:
    """Una pratica non visibile risponde come una inesistente."""
    query = (
        db.query(Pratica)
        .options(*_RELAZIONI_ELENCO)
        .filter(Pratica.pratica_id == pratica_id)
    )
    condizione = condizione_azienda(vis, Pratica.azienda_id)
    if condizione is not None:
        query = query.filter(condizione)
    pratica = query.first()
    if not pratica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pratica non trovata.",
        )
    return pratica


# POST
@router.post("/", response_model=PraticaResponse, status_code=status.HTTP_201_CREATED)
def crea_pratica(
    pratica_in: PraticaCreate,
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
):
    # exclude_unset=True e' OBBLIGATORIO qui, a differenza di crea_azienda:
    # molti campi di PraticaCreate (listTesta_id, cliente_id, pratica_stato_id,
    # nome_universita_id, cliente_emittente_aderente_id, pratica_prezzo, tutti
    # i missFlag/rinn...) sono Optional=None nello schema perche' a database
    # hanno un server_default. Un model_dump() completo passerebbe None
    # esplicito per i campi non inviati, e SQLAlchemy scriverebbe NULL invece
    # di lasciar agire il DEFAULT del database - lo stesso bug descritto nei
    # commenti di Cliente/Azienda sui server_default.
    dati = pratica_in.model_dump(exclude_unset=True)

    # Chi non e' Nazionale crea pratiche solo per la propria azienda: il valore
    # inviato non conta. 403 e non 422: il corpo e' valido, e' l'utente a non
    # poter fare l'operazione finche' non ha un'azienda.
    if not vis.nazionale:
        if vis.azienda_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=AZIENDA_MANCANTE
            )
        dati["azienda_id"] = vis.azienda_id

    nuova_pratica = Pratica(**dati)
    db.add(nuova_pratica)
    db.commit()
    db.refresh(nuova_pratica)
    return _pratica_o_404(db, nuova_pratica.pratica_id, vis)


# GET ALL
@router.get("/", response_model=List[PraticaResponse])
def lista_pratiche(
    filtri: Annotated[FiltriPratiche, Query()],
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
):
    return (query_filtrata(db, filtri, vis).options(*_RELAZIONI_ELENCO)
            .order_by(Pratica.pratica_dataCreazione.desc(), Pratica.pratica_id.desc())
            .offset(filtri.skip).limit(filtri.limit).all())


# GET BY ID
@router.get("/{pratica_id}", response_model=PraticaResponse)
def dettaglio_pratica(
    pratica_id: int,
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
):
    return _pratica_o_404(db, pratica_id, vis)


# PUT
@router.put("/{pratica_id}", response_model=PraticaResponse)
def aggiorna_pratica(
    pratica_id: int,
    pratica_in: PraticaUpdate,
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
):
    pratica = _pratica_o_404(db, pratica_id, vis)

    # exclude_unset=True: stesso motivo di aggiorna_azienda, un campo non
    # inviato non deve essere riscritto con un default dello schema.
    modifiche = pratica_in.model_dump(exclude_unset=True)
    # L'azienda di una pratica la cambia solo il Nazionale: per gli altri
    # spostarla significherebbe perderla di vista, o darla a un'altra azienda.
    if not vis.nazionale:
        modifiche.pop("azienda_id", None)

    for chiave, valore in modifiche.items():
        setattr(pratica, chiave, valore)

    db.commit()
    db.refresh(pratica)
    return _pratica_o_404(db, pratica_id, vis)