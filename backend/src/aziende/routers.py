from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from src.auth.dipendenze import get_current_utente
from src.auth.servizio_login import cliente_principale
from src.database import get_db
from src.aziende.models import Azienda, AderenteDettaglio
from src.aziende.schemas import (
    AziendaCreate,
    AziendaResponse,
    AziendaUpdate,
    AderenteDettaglioBase,
    AderenteDettaglioResponse,
    AderenteDettaglioUpdate,
    _valida_partita_iva,
    _valida_codice_fiscale,
)
from src.aziende_xcod.models import AziendaXCod
from src.aziende_xcod.servizi import (
    aziende_visibili_ids,
    calcola_cascata_percentuali,
    applica_cascata_percentuali,
    descrivi_cascata,
)


router = APIRouter(
    prefix="/aziende",
    tags=["Aziende"],
    dependencies=[Depends(get_current_utente)],
)

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
    if visibili is not None and azienda_id not in visibili:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Azienda non trovata.")
    azienda = db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first()
    if not azienda:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Azienda non trovata.")
    return azienda


def _dettaglio_o_nuovo(db: Session, azienda_id: int) -> AderenteDettaglio:
    dettaglio = (
        db.query(AderenteDettaglio)
        .filter(AderenteDettaglio.azienda_id == azienda_id)
        .first()
    )
    if dettaglio is None:
        dettaglio = AderenteDettaglio(
            azienda_id=azienda_id,
            **{campo: 0 for campo in AderenteDettaglioBase.model_fields},
        )
    return dettaglio


def _annota_anomalie(db: Session, aziende: list[Azienda]) -> None:
    """Calcola e attacca l'attributo `anomalie` (non persistito, letto da
    AziendaResponse via from_attributes) a ogni azienda passata:
    - Codice Fiscale mancante, o duplicato con un'altra azienda (nominata);
    - Partita IVA mancante o non conforme (diversa da 11 cifre numeriche).

    Il confronto duplicati e' fatto su tutta la tabella, non solo sulle righe
    passate qui, perche' due duplicati potrebbero finire su pagine diverse
    dell'elenco.
    """
    tutte = db.query(Azienda.azienda_id, Azienda.azienda_codiceFiscale, Azienda.azienda_ragione_sociale).all()

    # Mappa CF -> lista di (id, ragione sociale) di ogni azienda con quel CF,
    # per poter nominare "con chi" e' in conflitto, non solo "che esiste un
    # duplicato".
    per_cf = {}
    for azienda_id, cf, ragione_sociale in tutte:
        cf_pulito = (cf or "").strip()
        if not cf_pulito:
            continue
        per_cf.setdefault(cf_pulito, []).append((azienda_id, ragione_sociale))

    for azienda in aziende:
        anomalie = []
        cf = (azienda.azienda_codiceFiscale or "").strip()
        piva = (azienda.azienda_partitaIVA or "").strip()

        if not cf:
            anomalie.append("Codice Fiscale mancante")
        else:
            omonime = [nome for aid, nome in per_cf.get(cf, []) if aid != azienda.azienda_id]
            if omonime:
                elenco = ", ".join(omonime)
                anomalie.append(f"Codice Fiscale duplicato con: {elenco}")

        if not piva:
            anomalie.append("Partita IVA mancante")
        elif not (piva.isdigit() and len(piva) == 11):
            anomalie.append("Partita IVA non conforme (deve essere di 11 cifre numeriche)")

        azienda.anomalie = anomalie


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

    _annota_anomalie(db, [nuova_azienda])
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

    risultati = (
        query.order_by(Azienda.azienda_id.asc()).offset(skip).limit(limit).all()
    )
    _annota_anomalie(db, risultati)
    return risultati


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
    _annota_anomalie(db, [azienda])
    return azienda


#GET BY ID
@router.get("/{azienda_id}", response_model=AziendaResponse)
def dettaglio_azienda(
    azienda_id: int,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    azienda = _azienda_o_404(db, azienda_id, aziende_visibili_ids(db, utente_corrente))
    _annota_anomalie(db, [azienda])
    return azienda


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

    # Ora che l'elenco segnala le anomalie col triangolo, un salvataggio deve
    # rispettare le stesse regole di una creazione: lo stato FINALE
    # dell'azienda dopo le modifiche deve avere Partita IVA conforme (11
    # cifre) e Codice Fiscale non vuoto - anche se questo PUT non toccava
    # quei campi (cioe' erano gia' sporchi da prima del salvataggio).
    try:
        azienda.azienda_partitaIVA = _valida_partita_iva(azienda.azienda_partitaIVA)
        azienda.azienda_codiceFiscale = _valida_codice_fiscale(azienda.azienda_codiceFiscale)
    except ValueError as errore:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(errore))

    db.commit()
    db.refresh(azienda)
    _annota_anomalie(db, [azienda])
    return azienda


@router.get("/{azienda_id}/dettagli", response_model=AderenteDettaglioResponse)
def dettaglio_azienda_percentuali(
    azienda_id: int,
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    _azienda_o_404(db, azienda_id, aziende_visibili_ids(db, utente_corrente))
    return _dettaglio_o_nuovo(db, azienda_id)


@router.put("/{azienda_id}/dettagli")
def aggiorna_dettaglio_azienda(
    azienda_id: int,
    dettaglio_in: AderenteDettaglioUpdate,
    conferma_reset: bool = Query(False),
    db: Session = Depends(get_db),
    utente_corrente=Depends(get_current_utente),
):
    _azienda_o_404(db, azienda_id, aziende_visibili_ids(db, utente_corrente))

    valori = dettaglio_in.model_dump()
    cascata = calcola_cascata_percentuali(db, azienda_id, valori)

    if cascata and not conferma_reset:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"richiede_conferma": True, "reset": descrivi_cascata(db, cascata)},
        )

    applica_cascata_percentuali(db, azienda_id, valori, cascata)
    db.commit()

    dettaglio = _dettaglio_o_nuovo(db, azienda_id)
    return AderenteDettaglioResponse.model_validate(dettaglio).model_dump()