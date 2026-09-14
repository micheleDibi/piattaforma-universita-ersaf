"""Generazione e verifica di codici OTP: login del ruolo Nazionale e verifica
dei contatti (email, in futuro cellulare) dei clienti.

Riusa `logs_otp` cosi' com'e'. tipo_riferimento/riferimento distinguono gli
usi: "login - uni.ersaf.it"/username per il login, "email"/l'indirizzo per la
verifica contatti. Invalidazione dei precedenti e controllo "gia' verificato"
sono sempre scoperti per (cliente_id, tipo_riferimento, riferimento): generare
un OTP di verifica email non deve mai toccare un OTP di login dello stesso
cliente, e viceversa.
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


def _invalida_precedenti(
    db: Session, cliente_id: int, tipo_riferimento: str, riferimento: str
) -> None:
    """"Genera nuovo codice OTP" deve invalidare il precedente: si marcano
    scadute tutte le righe non ancora verificate con lo stesso riferimento."""
    db.execute(
        update(LogOtp)
        .where(
            LogOtp.cliente_id == cliente_id,
            LogOtp.log_otp_tipo_riferimento == tipo_riferimento,
            LogOtp.log_otp_riferimento == riferimento,
            LogOtp.log_otp_check == 0,
        )
        .values(log_otp_expired_at=datetime.now())
        .execution_options(synchronize_session=False)
    )


def genera_otp(
    db: Session,
    *,
    cliente_id: int,
    utente_id: int,
    tipo_riferimento: str,
    riferimento: str,
    autore_id: int,
    hostname: str,
    scadenza_minuti: int = SCADENZA_MINUTI,
) -> SfidaOtp:
    _invalida_precedenti(db, cliente_id, tipo_riferimento, riferimento)

    ora = datetime.now()
    scadenza = ora + timedelta(minutes=scadenza_minuti)
    riga = LogOtp(
        cliente_id=cliente_id,
        utente_id=utente_id,
        log_otp_tipo_riferimento=tipo_riferimento,
        log_otp_riferimento=riferimento,
        log_otp_codice=_genera_codice(),
        log_otp_check=0,
        log_otp_hostname=hostname[:45],
        log_otp_created_by=autore_id,
        log_otp_created_at=ora,
        log_otp_updated_by=autore_id,
        log_otp_updated_at=ora,
        log_otp_expired_at=scadenza,
    )
    db.add(riga)
    db.flush()  # serve log_otp_id; il commit resta al chiamante

    logger.info(
        "OTP generato: cliente_id=%s tipo=%s log_otp_id=%s",
        cliente_id, tipo_riferimento, riga.log_otp_id,
    )
    return SfidaOtp(log_otp_id=riga.log_otp_id, codice=riga.log_otp_codice, scadenza=scadenza)


def gia_verificato(
    db: Session, cliente_id: int, tipo_riferimento: str, riferimento: str
) -> bool:
    """Replica checkMailOTP/checkCellulareOTP dello script legacy: una volta
    verificato un contatto, non deve essere possibile riverificarlo."""
    return (
        db.execute(
            select(LogOtp.log_otp_id).where(
                LogOtp.cliente_id == cliente_id,
                LogOtp.log_otp_tipo_riferimento == tipo_riferimento,
                LogOtp.log_otp_riferimento == riferimento,
                LogOtp.log_otp_check == 1,
            ).limit(1)
        ).scalar_one_or_none()
        is not None
    )


def trova_per_utente(db: Session, utente_id: int, log_otp_id: int) -> Optional[LogOtp]:
    """Per il login: utente_id+log_otp_id provano che il chiamante ha gia'
    superato username+password, visto che l'endpoint non e' altrimenti
    autenticato."""
    return db.execute(
        select(LogOtp).where(LogOtp.log_otp_id == log_otp_id, LogOtp.utente_id == utente_id)
    ).scalar_one_or_none()


def trova_per_cliente(db: Session, cliente_id: int, log_otp_id: int) -> Optional[LogOtp]:
    """Per la verifica contatti: qui il chiamante e' gia' un operatore
    autenticato (dipendenza del router /clienti); basta legare log_otp_id al
    cliente della scheda che sta guardando."""
    return db.execute(
        select(LogOtp).where(LogOtp.log_otp_id == log_otp_id, LogOtp.cliente_id == cliente_id)
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