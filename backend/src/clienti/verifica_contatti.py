"""Verifica dei contatti (email, e in futuro cellulare) di un cliente.

Riusa src.auth.servizio_otp generalizzato. Una volta verificata l'email si
attiva l'utente e si mandano le credenziali - il cellulare (Skebby) e' fuori
perimetro per ora: quando sara' pronto, l'attivazione va condizionata a
"entrambi verificati", come nel ticket originale.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.auth.servizio_otp import SCADENZA_MINUTI, SfidaOtp, gia_verificato, genera_otp
from src.clienti.models import Cliente

TIPO_RIFERIMENTO_EMAIL = "email"
TIPO_RIFERIMENTO_CELLULARE = "cellulare"  # non ancora usato


def email_gia_verificata(db: Session, cliente: Cliente) -> bool:
    if not cliente.cliente_email:
        return False
    return gia_verificato(db, cliente.cliente_id, TIPO_RIFERIMENTO_EMAIL, cliente.cliente_email)


def genera_otp_email(db: Session, cliente: Cliente, autore_id: int, hostname: str) -> SfidaOtp:
    return genera_otp(
        db,
        cliente_id=cliente.cliente_id,
        utente_id=cliente.utente_id,
        tipo_riferimento=TIPO_RIFERIMENTO_EMAIL,
        riferimento=cliente.cliente_email,
        autore_id=autore_id,
        hostname=hostname,
        scadenza_minuti=SCADENZA_MINUTI,
    )