"""Parsing rigoroso comune ai confini HTTP e WebSocket."""

import json
import math
import re

from fastapi import Request
from src.realtime.errori import ErroreRealtime, richiedi


def oggetto(coppie):
    valori = {}
    for k, v in coppie:
        richiedi(k not in valori, "invalid_json")
        valori[k] = v
    return valori


def json_limitato(raw, massimo=16384):
    try:
        dimensione = len(raw.encode("utf-8")) if isinstance(raw, str) else len(raw)
        richiedi(dimensione <= massimo, "payload_too_large", 413)
        if not isinstance(raw, str):
            raw = raw.decode("utf-8")
        valore = json.loads(
            raw,
            object_pairs_hook=oggetto,
            parse_constant=costante_non_valida,
            parse_float=numero_finito,
        )
        richiedi(type(valore) is dict, "invalid_json")
        verifica_profondita(valore)
        return valore
    except (ValueError, UnicodeError, RecursionError):
        raise ErroreRealtime("invalid_json") from None


def verifica_profondita(valore, profondita=0):
    richiedi(profondita <= 32, "invalid_json")
    if isinstance(valore, str):
        valore.encode("utf-8")
    if isinstance(valore, dict):
        for chiave in valore:
            chiave.encode("utf-8")
    figli = valore.values() if isinstance(valore, dict) else valore if isinstance(valore, list) else ()
    for figlio in figli:
        verifica_profondita(figlio, profondita + 1)


def costante_non_valida(_):
    raise ValueError("Costante JSON non valida")


def numero_finito(valore):
    numero = float(valore)
    if not math.isfinite(numero):
        raise ValueError("Numero JSON non finito")
    return numero


async def corpo_vuoto(request: Request):
    async for parte in request.stream():
        richiedi(not parte, "unexpected_body")


async def corpo(request, massimo=16384):
    richiedi(
        request.headers.get("content-type", "").split(";")[0].lower() == "application/json",
        "invalid_content_type",
        415,
    )
    raw = bytearray()
    async for parte in request.stream():
        raw.extend(parte)
        richiedi(len(raw) <= massimo, "payload_too_large", 413)
    return json_limitato(raw, massimo)


def stringa(dati, campo, massimo=255):
    s = dati.get(campo)
    richiedi(isinstance(s, str) and s.strip() and len(s) <= massimo, "invalid_" + campo)
    return s


def positivo(dati, campo):
    s = stringa(dati, campo, 19)
    richiedi(
        re.fullmatch(r"[1-9][0-9]{0,18}", s) and int(s) <= 9223372036854775807,
        "invalid_" + campo,
    )
    return int(s)


def uuid_canonico(valore):
    richiedi(
        isinstance(valore, str)
        and re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            valore,
        ),
        "invalid_id",
    )
    return valore


def parametri(request, ammessi):
    coppie = list(request.query_params.multi_items())
    richiedi(
        len(coppie) == len(dict(coppie)) and set(dict(coppie)) <= set(ammessi),
        "invalid_query",
    )
    return dict(coppie)
