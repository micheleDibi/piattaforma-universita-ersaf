"""Download del documento di una pratica.

Il router si include in quello delle pratiche: prende prefisso `/pratiche` e la
stessa autenticazione del dettaglio, senza doverla ripetere.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload

from src.database import get_db
from src.documenti import modelli as registro
from src.documenti.dati import dati_pratica
from src.documenti.motore import ComposizioneFallita, ModelloAssente, componi_pdf
from src.listini_testa.models import ListinoTestaDB
from src.pratiche.models import Pratica

logger = logging.getLogger("ersaf.documenti")
router = APIRouter()

NON_DISPONIBILE = "Per questo tipo di pratica il documento non è ancora disponibile."
COMPOSIZIONE_FALLITA = "Non è stato possibile comporre il documento. Riprova tra poco o avvisa l'assistenza."


def _pratica(db: Session, pratica_id: int) -> Pratica:
    listino = joinedload(Pratica.listino_testa)
    pratica = (
        db.query(Pratica)
        .options(
            joinedload(Pratica.cliente),
            listino.joinedload(ListinoTestaDB.universita),
            listino.joinedload(ListinoTestaDB.tipo_corso),
            listino.joinedload(ListinoTestaDB.durata_laurea),
            listino.joinedload(ListinoTestaDB.facolta),
            listino.joinedload(ListinoTestaDB.corso_laurea),
        )
        .filter(Pratica.pratica_id == pratica_id)
        .first()
    )
    if pratica is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pratica non trovata.")
    return pratica


@router.get("/{pratica_id}/documento/disponibile")
def documento_disponibile(pratica_id: int, db: Session = Depends(get_db)) -> dict:
    """Se la pratica ha un modulo stampabile: il frontend mostra il pulsante solo in quel caso."""
    pratica = _pratica(db, pratica_id)
    disponibile = registro.modello_per(pratica) is not None
    return {"disponibile": disponibile, "nome_file": registro.nome_file(pratica) if disponibile else None}


@router.get(
    "/{pratica_id}/documento",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}, "description": "Il documento della pratica in PDF/A."}},
)
def scarica_documento(pratica_id: int, db: Session = Depends(get_db)) -> Response:
    pratica = _pratica(db, pratica_id)
    modello = registro.modello_per(pratica)
    if modello is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NON_DISPONIBILE)
    dati, allegati = dati_pratica(db, pratica)
    try:
        pdf = componi_pdf(modello.nome, modello.arricchisci(dati), allegati)
    except (ModelloAssente, ComposizioneFallita):
        # Nessun dato personale nel log: solo pratica e modello.
        logger.exception("composizione del documento fallita: pratica %s, modello %s", pratica_id, modello.nome)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, COMPOSIZIONE_FALLITA) from None
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{registro.nome_file(pratica)}"',
            "Cache-Control": "no-store",
        },
    )
