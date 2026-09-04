"""Autenticazione delle richieste.

Prima era l'header `x-utente-id`: un intero non firmato che chiunque poteva
cambiare per impersonare qualsiasi utente. Ora e' `Authorization: Bearer
<token>` con validazione della sessione contro il database.

L'header si legge a mano invece di usare il solo HTTPBearer con auto_error,
che risponderebbe 403 quando manca: qui la risposta giusta e' sempre 401 con
WWW-Authenticate, sia che l'header manchi sia che il token non valga piu'.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database import get_db
from src.security.sessioni import segna_ultimo_accesso, valida_sessione
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.auth")

schema_bearer = HTTPBearer(auto_error=False, scheme_name="SessioneERSAF")


@dataclass(frozen=True)
class SessioneCorrente:
    utente: Utente
    sess_id: int


def _non_autenticato(dettaglio: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=dettaglio,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_sessione_corrente(
    credenziali: HTTPAuthorizationCredentials | None = Depends(schema_bearer),
    db: Session = Depends(get_db),
) -> SessioneCorrente:
    if credenziali is None or credenziali.scheme.lower() != "bearer":
        raise _non_autenticato(
            "Manca l'header di autenticazione (Authorization: Bearer <token>)"
        )

    esito = valida_sessione(db, credenziali.credentials)
    if esito is None:
        # Un unico messaggio per token inesistente, scaduto, revocato o di
        # utente disattivato: distinguerli direbbe all'attaccante quali token
        # sono esistiti.
        raise _non_autenticato("Sessione non valida o scaduta")

    sess_id, utente_id = esito
    utente = db.get(Utente, utente_id)
    if utente is None:
        raise _non_autenticato("Sessione non valida o scaduta")

    segna_ultimo_accesso(db, sess_id)
    return SessioneCorrente(utente=utente, sess_id=sess_id)


def get_current_utente(
    sessione: SessioneCorrente = Depends(get_sessione_corrente),
) -> Utente:
    """Firma invariata: i consumatori esistenti continuano a funzionare."""
    return sessione.utente
