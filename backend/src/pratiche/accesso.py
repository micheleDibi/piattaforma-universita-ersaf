"""Accesso comune a scheda, firma, PDF e messaggi della pratica."""

from fastapi import HTTPException

from src.auth.visibilita import condizione_azienda
from src.pratiche.models import Pratica


def pratica_visibile(db, pratica_id, vis, *, opzioni=(), blocca=False):
    query = db.query(Pratica).options(*opzioni).filter(Pratica.pratica_id == pratica_id)
    condizione = condizione_azienda(vis, Pratica.azienda_id)
    if condizione is not None:
        query = query.filter(condizione)
    if blocca:
        query = query.with_for_update().populate_existing()
    pratica = query.first()
    if pratica is None:
        raise HTTPException(404, "Pratica non trovata.")
    return pratica
