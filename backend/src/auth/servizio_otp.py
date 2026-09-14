"""Generazione e verifica del codice OTP per l'accesso del ruolo Nazionale.

Nessuna modifica di schema: si riusa `logs_otp` cosi' com'e' (script legacy
InDe genera/verifica OTP). L'identificativo che il frontend deve ripresentare
per verificare o rigenerare e' la coppia (utente_id, log_otp_id):
log_otp_id da solo e' un intero sequenziale indovinabile, quindi non basta a
provare che il chiamante ha gia' superato username+password in QUESTO login.
"""

from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.auth.models import LogOtp
from src.clienti.models import Cliente
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.otp")

TIPO_RIFERIMENTO_LOGIN = "login - uni.ersaf.it"
LUNGHEZZA_CODICE = 6
SCADENZA_MINUTI = 10


@dataclass(frozen=True)
class SfidaOtp:
    log_otp_id: int
    codice: str
    scadenza: datetime


def _genera_codice() -> str:
    """Zero-padded: senza, '42' non corrisponderebbe mai a un input di 6 cifre."""
    return f"{secrets.randbelow(10**LUNGHEZZA_CODICE):0{LUNGHEZZA_CODICE}d}"


def _invalida_precedenti(db: Session, utente_id: int) -> None:
    """"Genera nuovo codice OTP" deve invalidare il precedente: si marcano
    scadute tutte le righe non ancora verificate dello stesso utente."""
    db.execute(
        update(LogOtp)
        .where(LogOtp.utente_id == utente_id, LogOtp.log_otp_check == 0)
        .values(log_otp_expired_at=datetime.now())
        .execution_options(synchronize_session=False)
    )


def genera_otp(db: Session, utente: Utente, cliente: Cliente, hostname: str) -> SfidaOtp:
    _invalida_precedenti(db, utente.utente_id)

    ora = datetime.now()
    scadenza = ora + timedelta(minutes=SCADENZA_MINUTI)
    riga = LogOtp(
        cliente_id=cliente.cliente_id,
        utente_id=utente.utente_id,
        log_otp_tipo_riferimento=TIPO_RIFERIMENTO_LOGIN,
        log_otp_riferimento=cliente.cliente_email or "",
        log_otp_codice=_genera_codice(),
        log_otp_check=0,
        log_otp_hostname=hostname[:45],
        log_otp_created_by=utente.utente_id,
        log_otp_created_at=ora,
        log_otp_updated_by=utente.utente_id,
        log_otp_updated_at=ora,
        log_otp_expired_at=scadenza,
    )
    db.add(riga)
    db.flush()  # serve log_otp_id; il commit resta al chiamante (router)

    logger.info("OTP generato per utente_id=%s, log_otp_id=%s", utente.utente_id, riga.log_otp_id)
    return SfidaOtp(log_otp_id=riga.log_otp_id, codice=riga.log_otp_codice, scadenza=scadenza)


def trova(db: Session, utente_id: int, log_otp_id: int) -> Optional[LogOtp]:
    return db.execute(
        select(LogOtp).where(LogOtp.log_otp_id == log_otp_id, LogOtp.utente_id == utente_id)
    ).scalar_one_or_none()


def codice_valido(riga: Optional[LogOtp], codice: str) -> bool:
    if riga is None or riga.log_otp_check:
        return False
    if riga.log_otp_expired_at and riga.log_otp_expired_at < datetime.now():
        return False
    return secrets.compare_digest(riga.log_otp_codice, codice)


def marca_verificato(riga: LogOtp) -> None:
    ora = datetime.now()
    riga.log_otp_check = 1
    riga.log_otp_datetime_check = ora
    riga.log_otp_updated_by = riga.utente_id
    riga.log_otp_updated_at = ora