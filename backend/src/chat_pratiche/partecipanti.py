"""Stessa partecipazione delle chat Universo, indipendente dal ruolo globale."""
from fastapi import HTTPException
from sqlalchemy import select, or_, func

from src.clienti.models import Cliente
from src.utenti.models import Utente
from src.pratiche.models import Pratica
from src.chat_pratiche.contesto import ContestoChat


def partecipanti(db, pratica, blocca=False):
    ids = (pratica.utente_id, pratica.utente_consulente_id)
    clienti = (pratica.cliente_id, pratica.cliente_emittente_aderente_id, pratica.cliente_consulente_id)
    univoci = select(Cliente.utente_id).group_by(Cliente.utente_id).having(func.count() == 1)
    query = select(Cliente).join(Utente, Utente.utente_id == Cliente.utente_id)
    query = query.where(Utente.utente_attivoSN == -1, Cliente.utente_id.in_(univoci),
               or_(Cliente.utente_id.in_(ids), Cliente.cliente_id.in_(clienti)))
    query = query.order_by(Cliente.utente_id).limit(257).execution_options(populate_existing=True)
    if blocca:
        query = query.with_for_update(read=True)
    return list(db.scalars(query))


def autorizza(db, utente_id, pratica_id, *, blocca=False):
    query = select(Pratica).where(Pratica.pratica_id == pratica_id)
    if blocca:
        query = query.with_for_update()
    pratica = db.scalar(query.execution_options(populate_existing=True))
    if pratica is None:
        raise HTTPException(404, "Pratica non trovata.")
    persone = partecipanti(db, pratica, blocca)
    me = next((p for p in persone if p.utente_id == utente_id), None)
    if not me or not 2 <= len(persone) <= 256 or not pratica.pratica_numero:
        raise HTTPException(403, "Non sei tra i partecipanti autorizzati alla chat della pratica.")
    utente = db.get(Utente, utente_id)
    contesto = ContestoChat(utente_id, me.cliente_id, utente.utente_username,
                           pratica_id, pratica.pratica_numero, pratica.cliente_id)
    return contesto, persone
