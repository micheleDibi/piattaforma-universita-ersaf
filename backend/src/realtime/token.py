"""JWT e refresh compatibili con le sessioni gia emesse dal servizio precedente."""

import hashlib
import re
import secrets
import time
import uuid
from datetime import timedelta, timezone

import jwt
from src.chat_pratiche.cifratura import codifica
from src.chat_pratiche.cifratura import decodifica as base64_decodifica
from src.chat_pratiche.configurazione import configurazione, leggi_segreto
from src.realtime.contratti import json_limitato
from src.realtime.dati import iso, ora
from src.realtime.errori import ErroreRealtime, richiedi

CAMPI = [
    "iss",
    "aud",
    "sub",
    "sid",
    "cid",
    "aid",
    "role",
    "device",
    "iat",
    "exp",
    "jti",
]


def segreto():
    return leggi_segreto(configurazione().chat_universo_jwt_file, massimo=128)


def impronta(refresh):
    richiedi(
        isinstance(refresh, str) and re.fullmatch(r"urt_[A-Za-z0-9_-]{43}", refresh),
        "invalid_refresh_token",
        401,
    )
    return hashlib.sha256(refresh.encode()).digest()


def nuovo_refresh():
    return "urt_" + secrets.token_urlsafe(32)


def emetti(sessione, refresh):
    conf, adesso = configurazione(), ora().replace(microsecond=0)
    scadenza = min(
        adesso + timedelta(seconds=conf.realtime_accesso_secondi),
        sessione["refresh_expires_at"].replace(microsecond=0),
    )
    richiedi(scadenza > adesso, "invalid_token", 401)
    claims = dict(
        iss=conf.chat_universo_issuer,
        aud=conf.chat_universo_audience,
        sub=str(sessione["utente_id"]),
        sid=sessione["session_id"],
        cid=sessione["cliente_id"],
        aid=sessione["azienda_id"],
        role=sessione["ruolo_codice"],
        device=sessione["device_id"],
        iat=int(adesso.replace(tzinfo=timezone.utc).timestamp()),
        exp=int(scadenza.replace(tzinfo=timezone.utc).timestamp()),
        jti=str(uuid.uuid4()),
    )
    return dict(
        accessToken=jwt.encode(claims, segreto(), algorithm="HS256"),
        accessTokenExpiresAt=iso(scadenza),
        refreshToken=refresh,
        refreshTokenExpiresAt=iso(sessione["refresh_expires_at"]),
        tokenType="Bearer",
    )


def decodifica(token):
    conf = configurazione()
    try:
        richiedi(isinstance(token, str) and len(token) <= 4096, "invalid_token", 401)
        intestazione, corpo, firma = token.split(".")
        richiedi(codifica(base64_decodifica(firma)) == firma, "invalid_token", 401)
        json_limitato(base64_decodifica(intestazione), 4096)
        json_limitato(base64_decodifica(corpo), 4096)
        d = jwt.decode(
            token,
            segreto(),
            algorithms=["HS256"],
            issuer=conf.chat_universo_issuer,
            audience=conf.chat_universo_audience,
            options={"require": CAMPI, "strict_aud": True, "verify_iat": False},
        )
        richiedi(jwt.get_unverified_header(token).get("typ") == "JWT", "invalid_token", 401)
        valida_claims(d)
        return d
    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        AttributeError,
        ErroreRealtime,
    ):
        raise ErroreRealtime("invalid_token", 401) from None


def valida_claims(d):
    richiedi(
        type(d["iat"]) is int
        and type(d["exp"]) is int
        and d["exp"] > d["iat"]
        and d["iat"] <= time.time() + 15,
        "invalid_token",
        401,
    )
    richiedi(
        re.fullmatch(r"[1-9][0-9]{0,9}", d["sub"])
        and int(d["sub"]) <= 2147483647
        and type(d["cid"]) is int
        and 0 < d["cid"] <= 2147483647
        and type(d["aid"]) is int
        and 0 <= d["aid"] <= 2147483647,
        "invalid_token",
        401,
    )
    richiedi(
        all(
            isinstance(d[k], str) and 0 < len(d[k]) <= limite
            for k, limite in (
                ("role", 45),
                ("device", 128),
                ("sid", 36),
                ("jti", 36),
            )
        ),
        "invalid_token",
        401,
    )
    uuid.UUID(d["sid"])
    uuid.UUID(d["jti"])
