"""Sessioni applicative revocabili (migrazione 004).

Sostituiscono l'header `x-utente-id`, che era un intero non firmato: chiunque
poteva scrivere `x-utente-id: 1` e impersonare qualsiasi utente.

Il token consegnato al client e' opaco, 32 byte da CSPRNG. Nel database c'e'
solo SHA-256(token || SESSION_TOKEN_PEPPER). Nessun JWT: un JWT non e'
revocabile senza una lista di revoca, e la revoca al cambio password e'
esattamente il requisito.

NON si tocca `utente_session`, che appartiene alla piattaforma legacy Instant
Developer ancora in produzione.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from src.auth.models import ATTIVO, AuthSessione, MotivoRevoca
from src.config import get_impostazioni
from src.security.tempo import istante_piu_ore
from src.security.tokens import TipoToken, forma_token_valida, genera_token, impronta
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.sessioni")

# Ogni quanto si aggiorna sess_last_seen_at. Senza una soglia sarebbe una
# scrittura per ogni richiesta autenticata.
SOGLIA_ULTIMO_ACCESSO = timedelta(minutes=5)


def crea_sessione(
    db: Session, utente_id: int, ip: bytes | None, user_agent: str | None
) -> tuple[str, datetime]:
    """Restituisce il token IN CHIARO — che non va mai loggato — e la scadenza.

    Il chiamante e' responsabile del commit: al login la creazione della
    sessione fa parte della stessa transazione dell'eventuale rehash.
    """
    token = genera_token()
    sessione = AuthSessione(
        utente_id=utente_id,
        sess_token_hash=impronta(token, TipoToken.SESSIONE),
        sess_created_at=func.now(),
        sess_expires_at=istante_piu_ore(get_impostazioni().session_ttl_hours),
        sess_ip=ip,
        sess_user_agent=user_agent,
    )
    db.add(sessione)
    db.flush()
    db.refresh(sessione)
    return token, sessione.sess_expires_at


def valida_sessione(db: Session, token: str) -> tuple[int, int] | None:
    """Query [B] della migrazione 004. Restituisce (sess_id, utente_id).

    Oltre a revoca e scadenza, la query scarta le sessioni di utenti
    disattivati e quelle nate PRIMA dell'ultimo cambio password: e' difesa in
    profondita', perche' se la revoca massiva della [A] fallisse quelle
    sessioni resterebbero altrimenti valide.
    """
    if not forma_token_valida(token):
        return None

    riga = db.execute(
        select(AuthSessione.sess_id, AuthSessione.utente_id)
        .join(Utente, Utente.utente_id == AuthSessione.utente_id)
        .where(
            AuthSessione.sess_token_hash == impronta(token, TipoToken.SESSIONE),
            AuthSessione.sess_revoked_at.is_(None),
            AuthSessione.sess_expires_at > func.now(),
            Utente.utente_attivoSN == ATTIVO,
            or_(
                Utente.utente_password_changed_at.is_(None),
                AuthSessione.sess_created_at >= Utente.utente_password_changed_at,
            ),
        )
    ).first()
    return (riga.sess_id, riga.utente_id) if riga else None


def segna_ultimo_accesso(db: Session, sess_id: int) -> None:
    """Aggiorna sess_last_seen_at, non piu' spesso della soglia."""
    db.execute(
        update(AuthSessione)
        .where(
            AuthSessione.sess_id == sess_id,
            or_(
                AuthSessione.sess_last_seen_at.is_(None),
                AuthSessione.sess_last_seen_at < func.now() - SOGLIA_ULTIMO_ACCESSO,
            ),
        )
        .values(sess_last_seen_at=func.now())
        .execution_options(synchronize_session=False)
    )
    db.commit()


def revoca_sessione(db: Session, token: str, motivo: MotivoRevoca) -> int:
    if not forma_token_valida(token):
        return 0
    esito = db.execute(
        update(AuthSessione)
        .where(
            AuthSessione.sess_token_hash == impronta(token, TipoToken.SESSIONE),
            AuthSessione.sess_revoked_at.is_(None),
        )
        .values(sess_revoked_at=func.now(), sess_revoked_reason=motivo.value)
        .execution_options(synchronize_session=False)
    )
    return esito.rowcount


def revoca_sessioni_utente(db: Session, utente_id: int, motivo: MotivoRevoca) -> int:
    """Query [A] della migrazione 004: revoca TUTTE le sessioni di un utente.

    Va eseguita nella stessa transazione dello UPDATE della password. Il
    chiamante non committa qui.
    """
    esito = db.execute(
        update(AuthSessione)
        .where(
            AuthSessione.utente_id == utente_id,
            AuthSessione.sess_revoked_at.is_(None),
        )
        .values(sess_revoked_at=func.now(), sess_revoked_reason=motivo.value)
        .execution_options(synchronize_session=False)
    )
    return esito.rowcount
