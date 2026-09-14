"""Validazione della sessione HttpOnly e del CSRF delle operazioni autenticate."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.security.sessioni import segna_ultimo_accesso, valida_sessione
from src.security.browser import token_richiesta, verifica_csrf
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.auth")

@dataclass(frozen=True)
class SessioneCorrente:
    utente: Utente
    sess_id: int


def _non_autenticato(dettaglio: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=dettaglio,
    )


def get_sessione_corrente(
    request: Request,
    db: Session = Depends(get_db),
) -> SessioneCorrente:
    token = token_richiesta(request)
    if not token:
        raise _non_autenticato("Sessione non valida o scaduta")

    esito = valida_sessione(db, token)
    if esito is None:
        # Un unico messaggio per token inesistente, scaduto, revocato o di
        # utente disattivato: distinguerli direbbe all'attaccante quali token
        # sono esistiti.
        raise _non_autenticato("Sessione non valida o scaduta")

    sess_id, utente_id = esito
    utente = db.get(Utente, utente_id)
    if utente is None:
        raise _non_autenticato("Sessione non valida o scaduta")

    verifica_csrf(request, token)
    segna_ultimo_accesso(db, sess_id)
    return SessioneCorrente(utente=utente, sess_id=sess_id)


def get_current_utente(
    sessione: SessioneCorrente = Depends(get_sessione_corrente),
) -> Utente:
    """Firma invariata: i consumatori esistenti continuano a funzionare."""
    return sessione.utente
