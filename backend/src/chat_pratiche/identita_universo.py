"""Consuma una sessione Universo esistente; non emette token o credenziali."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Request
from sqlalchemy import text

from src.chat_pratiche.configurazione import configurazione, leggi_segreto
from src.database import SessionLocal

CAMPI = ["iss", "aud", "sub", "sid", "cid", "aid", "role", "device", "iat", "exp", "jti"]
SESSIONE = """SELECT s.session_id FROM realtime_auth_session s
    JOIN utenti u ON u.utente_id=s.utente_id AND u.utente_attivoSN=-1
    JOIN clienti c ON c.cliente_id=s.cliente_id AND c.utente_id=s.utente_id
    JOIN ruoli r ON r.ruolo_id=c.cliente_ruolo
    WHERE s.session_id=:sid AND s.utente_id=:sub AND s.cliente_id=:cid
    AND s.azienda_id=:aid AND BINARY s.ruolo_codice=BINARY :role AND s.device_id=:device
    AND s.revoked_at IS NULL AND s.revocation_reason IS NULL
    AND s.refresh_expires_at>:now AND s.last_used_at>:idle
    AND COALESCE(c.azienda_id,0)=s.azienda_id AND BINARY r.ruolo_codice=BINARY s.ruolo_codice
    AND (SELECT COUNT(*) FROM clienti cc WHERE cc.utente_id=s.utente_id)=1
"""


@dataclass(frozen=True)
class IdentitaUniverso:
    token: str
    utente_id: int


def valida(db, token, *, attivita=False):
    conf = configurazione()
    if not conf.chat_universo_jwt_file:
        raise HTTPException(401, "Sessione Universo non valida.")
    secret = leggi_segreto(conf.chat_universo_jwt_file, massimo=128)
    try:
        if not isinstance(token, str) or len(token) > 4096:
            raise ValueError()
        dati = jwt.decode(token, secret, algorithms=["HS256"],
            issuer=conf.chat_universo_issuer, audience=conf.chat_universo_audience,
            options={"require": CAMPI, "strict_aud": True, "verify_iat": False})
        # Come Java: 15 secondi di tolleranza sull'emissione, nessuno sulla scadenza.
        if (jwt.get_unverified_header(token).get("typ") != "JWT"
                or type(dati["iat"]) is not int or type(dati["exp"]) is not int
                or dati["iat"] > datetime.now(timezone.utc).timestamp()+15 or dati["exp"] <= dati["iat"]):
            raise ValueError()
        if int(dati["sub"]) <= 0 or type(dati["cid"]) is not int or type(dati["aid"]) is not int:
            raise ValueError()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        dati.update(now=now, idle=now-timedelta(seconds=conf.chat_universo_inattivita_secondi))
        if not db.scalar(text(SESSIONE), dati):
            raise ValueError()
        if attivita:
            db.execute(text("""UPDATE realtime_auth_session SET last_used_at=:now
                WHERE session_id=:sid AND revoked_at IS NULL"""), dati)
        return IdentitaUniverso(token, int(dati["sub"]))
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(401, "Sessione Universo scaduta o non valida.") from None


def identita_http(request: Request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(401, "Sessione richiesta.")
    with SessionLocal.begin() as db:
        return valida(db, header[7:], attivita=True)
