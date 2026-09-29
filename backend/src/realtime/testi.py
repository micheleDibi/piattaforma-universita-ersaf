"""Vincoli testuali del protocollo e dei record legacy (lunghezze UTF-16)."""

from src.realtime.errori import richiedi

TRIM = "".join(chr(n) for n in range(33))


def testo(valore, massimo=255, multilinea=False):
    richiedi(isinstance(valore, str), "invalid_text")
    try:
        lunghezza = len(valore.encode("utf-16-le")) // 2
    except UnicodeError:
        richiedi(False, "invalid_text")
    ammessi = "\n\r\t" if multilinea else ""
    richiedi(
        lunghezza <= massimo
        and not any((ord(c) < 32 or 127 <= ord(c) <= 159) and c not in ammessi for c in valore),
        "invalid_text",
    )
    return valore


def produttore(valore, multilinea=False):
    richiedi(isinstance(valore, str), "invalid_text")
    valore = testo(valore.strip(TRIM), multilinea=multilinea)
    richiedi(bool(valore), "invalid_text")
    return valore


def strutturato(valore, massimo):
    valore = testo(valore, massimo)
    richiedi(bool(valore.strip()), "invalid_text")
    return valore.strip(TRIM)
