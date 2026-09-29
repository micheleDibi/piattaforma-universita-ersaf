"""Appartenenza immutabile degli snapshot, validata anche quando proviene dal DB."""

import json

from src.realtime.errori import ErroreRealtime, richiedi


def decodifica(raw):
    try:
        richiedi(isinstance(raw, str) and len(raw) <= 1100000, "invalid_snapshot", 503)
        ids = json.loads(raw)
        richiedi(
            isinstance(ids, list)
            and len(ids) <= 50000
            and all(type(n) is int and 0 < n <= 9223372036854775807 for n in ids)
            and len(set(ids)) == len(ids),
            "invalid_snapshot",
            503,
        )
        return ids
    except (ValueError, TypeError, RecursionError):
        raise ErroreRealtime("invalid_snapshot", 503) from None
