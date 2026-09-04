"""Rotte di autenticazione."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.dipendenze import (  # noqa: F401  (get_current_utente e' riesportata)
    SessioneCorrente,
    get_current_utente,
    get_sessione_corrente,
    schema_bearer,
)
from src.auth.models import MotivoRevoca
from src.auth.schemas import MESSAGGIO_CREDENZIALI, LoginRequest
from src.auth.servizio_login import (
    cliente_principale,
    codice_ruolo,
    trova_utente_per_username,
    verifica_credenziali,
)
from src.database import get_db
from src.security.rete import ip_client, user_agent
from src.security.sessioni import crea_sessione, revoca_sessione

logger = logging.getLogger("ersaf.auth")

router = APIRouter(prefix="/auth", tags=["Login"])


def _credenziali_errate() -> HTTPException:
    """Un solo messaggio per tutti i motivi di rifiuto.

    Password sbagliata, utente inesistente, account disattivato, utente senza
    riga `clienti`, username ambiguo: dall'esterno devono essere
    indistinguibili, altrimenti il login diventa un oracolo di enumerazione.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=MESSAGGIO_CREDENZIALI
    )


@router.post("/login")
def login(creds: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = ip_client(request)
    ua = user_agent(request)

    utente, ambiguo = trova_utente_per_username(db, creds.utente_username)
    if ambiguo:
        # Il database non ha la UNIQUE su utente_username e contiene sei gruppi
        # di duplicati. Prima si prendeva una riga arbitraria: se la password
        # digitata era quella dell'altro omonimo l'accesso falliva senza motivo
        # apparente, e se coincideva si entrava nell'account sbagliato.
        # La bonifica e' descritta nella migrazione 005.
        logger.warning(
            "accesso negato: lo username corrisponde a piu' di un utente"
        )
        verifica_credenziali(db, None, creds.utente_password)
        raise _credenziali_errate()

    if not verifica_credenziali(db, utente, creds.utente_password):
        raise _credenziali_errate()

    # Gli 869 utenti senza riga `clienti` producevano un 500 qui
    # (user.clienti.ruolo.ruolo_codice su clienti = None), e un 500 distingueva
    # "password sbagliata" da "utente esistente ma orfano".
    cliente = cliente_principale(db, utente.utente_id)
    if cliente is None:
        logger.warning(
            "accesso negato: utente senza riga clienti, utente_id=%s",
            utente.utente_id,
        )
        raise _credenziali_errate()

    ruolo = codice_ruolo(db, cliente.cliente_ruolo)

    if ruolo and ruolo.lower() == "nazionale":
        # Il flusso 2FA vero e' fuori perimetro. Non si emette sessione e non
        # si restituisce utente_id: il frontend deve fermarsi qui.
        db.commit()  # l'eventuale rehash pigro resta valido
        logger.info(
            "verifica a due fattori richiesta per utente_id=%s", utente.utente_id
        )
        return {
            "requires_2fa": True,
            "message": "Verifica a due fattori richiesta (2FA)",
            "utente_username": utente.utente_username,
        }

    token, scadenza = crea_sessione(db, utente.utente_id, ip, ua)
    db.commit()
    logger.info("login riuscito per utente_id=%s", utente.utente_id)

    return {
        "message": "Login effettuato con successo",
        # utente_id resta nella risposta: il frontend lo salva e lo inserisce
        # nel corpo di POST /clienti/. Toglierlo romperebbe la creazione dei
        # sottoscrittori.
        "utente_id": utente.utente_id,
        "utente_username": utente.utente_username,
        "ruolo_codice": ruolo,
        "token": token,
        "token_type": "bearer",
        "scadenza": scadenza.isoformat() if scadenza else None,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credenziali: HTTPAuthorizationCredentials | None = Depends(schema_bearer),
    db: Session = Depends(get_db),
) -> Response:
    """Sempre 204, anche con un token gia' revocato o inesistente.

    Un codice diverso direbbe al chiamante se quel token e' mai esistito.
    """
    if credenziali is not None and credenziali.scheme.lower() == "bearer":
        revoca_sessione(db, credenziali.credentials, MotivoRevoca.LOGOUT)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
