import re

from src.realtime.contratti import positivo, stringa
from src.realtime.errori import richiedi

CAMPI = {
    "type",
    "destinationType",
    "to",
    "destinationId",
    "codice",
    "isPublic",
    "content",
    "clientMessageId",
    "from",
    "timestamp",
}


def valida(payload, utente):
    richiedi(type(payload) is dict and set(payload) <= CAMPI, "invalid_message")
    tipo = payload.get("type")
    richiedi(
        isinstance(tipo, str) and tipo in {"CHAT", "TYPING", "LIST_USERS"}, "message_type_forbidden", 403
    )
    richiedi(payload.get("from", str(utente)) == str(utente), "sender_mismatch", 403)
    if "clientMessageId" in payload:
        richiedi(tipo in ("CHAT", "TYPING"), "client_message_id_forbidden", 403)
        richiedi(
            re.fullmatch(r"[A-Za-z0-9_-]{1,64}", stringa(payload, "clientMessageId", 64)),
            "invalid_clientMessageId",
        )
    if tipo == "LIST_USERS":
        return dict(type=tipo)
    d = contesto(payload, utente)
    if tipo == "CHAT":
        d["clientMessageId"] = payload.get("clientMessageId")
        richiedi(
            re.fullmatch(r"[A-Za-z0-9_-]{1,64}", stringa(d, "clientMessageId", 64)), "invalid_clientMessageId"
        )
        stringa(d, "content", 1403)
    else:
        richiedi(type(d.get("content")) is bool, "invalid_typing")
        if "clientMessageId" in payload:
            d["clientMessageId"] = payload["clientMessageId"]
    return d


def contesto(payload, utente):
    d = {k: payload[k] for k in ("type", "destinationType", "to", "content") if k in payload}
    d["from"] = str(utente)
    destinazione = stringa(d, "destinationType", 16)
    richiedi(destinazione in {"PERSON", "PRACTICE", "TICKET"}, "invalid_destinationType")
    positivo(d, "to")
    if destinazione != "PERSON":
        d["destinationId"] = payload.get("destinationId")
        positivo(d, "destinationId")
        richiedi(d["to"] == d["destinationId"], "reference_mismatch", 403)
    if destinazione == "PRACTICE":
        d["codice"] = payload.get("codice")
        stringa(d, "codice", 45)
    if destinazione == "TICKET":
        d["isPublic"] = payload.get("isPublic")
        richiedi(type(d.get("isPublic")) is bool, "invalid_isPublic")
    return d


def destinazione(d):
    return d["destinationType"], d["to"], d.get("isPublic")
