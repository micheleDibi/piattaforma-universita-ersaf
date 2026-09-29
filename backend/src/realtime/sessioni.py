"""Sessioni persistenti, revoca immediata e rotazione atomica anti-replay."""

import hmac
from contextlib import contextmanager
from datetime import timedelta

from fastapi import Request
from src.chat_pratiche.configurazione import configurazione
from src.database import SessionLocal
from src.realtime import token
from src.realtime.dati import esegui, ora
from src.realtime.errori import ErroreRealtime, richiedi
from src.realtime.identita import carica
from src.realtime.transazioni import ritenta


def revoca(db, sid, motivo):
    esegui(
        db,
        """UPDATE realtime_auth_session SET revoked_at=:now,revocation_reason=:reason
        WHERE session_id=:sid AND ((revoked_at IS NULL AND revocation_reason IS NULL)
            OR (revocation_reason='IDLE' AND :reason<>'IDLE'))""",
        dict(now=ora(), reason=motivo, sid=sid),
    )


def identita_corrente(db, s):
    try:
        i = carica(db, s["utente_id"])
    except ErroreRealtime:
        return None
    if (i.cliente_id, i.azienda_id, i.ruolo) != (
        s["cliente_id"],
        s["azienda_id"],
        s["ruolo_codice"],
    ):
        return None
    cambiata = esegui(
        db,
        "SELECT utente_password_changed_at FROM utenti WHERE utente_id=:u",
        {"u": i.utente_id},
    ).scalar()
    # La colonna legacy e DATETIME UTC nel contratto password/sessioni.
    return None if cambiata and cambiata > s["created_at"] else i


def valida(db, accesso, attivita=False):
    d = token.decodifica(accesso)
    s = (
        esegui(
            db,
            "SELECT * FROM realtime_auth_session WHERE session_id=:sid FOR UPDATE",
            d,
        )
        .mappings()
        .first()
    )
    richiedi(
        s is not None and s["revoked_at"] is None and s["revocation_reason"] is None,
        "invalid_token",
        401,
    )
    coppie = (
        ("sub", "utente_id"),
        ("cid", "cliente_id"),
        ("aid", "azienda_id"),
        ("role", "ruolo_codice"),
        ("device", "device_id"),
    )
    richiedi(all(str(d[a]) == str(s[b]) for a, b in coppie), "invalid_token", 401)
    adesso = ora()
    motivo = motivo_scadenza(s, adesso)
    if motivo:
        revoca(db, s["session_id"], motivo)
        raise ErroreRealtime("invalid_token", 401)
    identita = identita_corrente(db, s)
    if identita is None:
        revoca(db, s["session_id"], "IDENTITY")
        raise ErroreRealtime("invalid_token", 401)
    if attivita:
        esegui(
            db,
            "UPDATE realtime_auth_session SET last_used_at=:now WHERE session_id=:sid",
            dict(now=adesso, sid=d["sid"]),
        )
    return identita


def motivo_scadenza(sessione, adesso):
    if sessione["refresh_expires_at"] <= adesso:
        return "EXPIRED"
    limite = adesso - timedelta(seconds=configurazione().chat_universo_inattivita_secondi)
    return "IDLE" if sessione["last_used_at"] <= limite else None


@contextmanager
def transazione(accesso, attivita=False):
    errore = None
    with SessionLocal.begin() as db:
        try:
            identita = valida(db, accesso, attivita)
        except ErroreRealtime as e:
            errore = e
        # La revoca deve sopravvivere al 401; gli errori dell'operazione fanno rollback.
        if errore is None:
            yield db, identita
    if errore is not None:
        raise errore


def bearer(request: Request):
    valori = request.headers.getlist("authorization")
    richiedi(
        len(valori) == 1 and valori[0].lower().startswith("bearer "),
        "invalid_token",
        401,
    )
    return valori[0][7:].strip()


def identita_http(request: Request):
    with transazione(bearer(request), attivita=True) as (_, identita):
        return identita


@ritenta
def ruota(refresh, dispositivo=None):
    vecchio, nuovo = token.impronta(refresh), token.nuovo_refresh()
    # Gli esiti di sicurezza vanno COMMESSI prima di restituire un errore HTTP.
    with SessionLocal.begin() as db:
        esito = rotazione(db, (vecchio, token.impronta(nuovo), dispositivo))
    richiedi(
        isinstance(esito, dict),
        esito if isinstance(esito, str) else "invalid_refresh_token",
        401,
    )
    return token.emetti(esito, nuovo)


def rotazione(db, richiesta):
    vecchio, nuovo, dispositivo = richiesta
    s = (
        esegui(
            db,
            "SELECT * FROM realtime_auth_session WHERE refresh_token_hash=:h FOR UPDATE",
            {"h": vecchio},
        )
        .mappings()
        .first()
    )
    if s is None:
        sid = esegui(
            db,
            "SELECT session_id FROM realtime_auth_refresh_history WHERE token_hash=:h FOR UPDATE",
            {"h": vecchio},
        ).scalar()
        if sid:
            revoca(db, sid, "TOKEN_REUSE")
        return "invalid_refresh_token"
    if not recuperabile(s, dispositivo):
        return "invalid_refresh_token"
    if identita_corrente(db, s) is None:
        revoca(db, s["session_id"], "IDENTITY")
        return "invalid_refresh_token"
    if s["refresh_generation"] >= 10000:
        revoca(db, s["session_id"], "ROTATION_LIMIT")
        return "invalid_refresh_token"
    if s["refresh_expires_at"].replace(microsecond=0) <= ora().replace(microsecond=0):
        return "invalid_refresh_token"
    esegui(
        db,
        """INSERT INTO realtime_auth_refresh_history VALUES (:h,:sid,:now,:exp)""",
        dict(h=vecchio, sid=s["session_id"], now=ora(), exp=s["refresh_expires_at"]),
    )
    esegui(
        db,
        """UPDATE realtime_auth_session SET refresh_token_hash=:h,refresh_generation=refresh_generation+1,
        last_used_at=:now,revoked_at=NULL,revocation_reason=NULL WHERE session_id=:sid""",
        dict(h=nuovo, now=ora(), sid=s["session_id"]),
    )
    return dict(s)


def recuperabile(s, dispositivo):
    if s["refresh_expires_at"] <= ora():
        return False
    inattiva = s["last_used_at"] <= ora() - timedelta(
        seconds=configurazione().chat_universo_inattivita_secondi
    )
    integra = s["revoked_at"] is None and s["revocation_reason"] is None
    if dispositivo is None:
        return integra and not inattiva
    return hmac.compare_digest(s["device_id"].encode(), dispositivo.encode()) and (
        (integra and inattiva) or s["revocation_reason"] == "IDLE"
    )
