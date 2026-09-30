"""Validazione del comando: identita e pratica provengono dalla sessione."""

import re


def valida_invio(dati):
    if (set(dati) != {"tipo", "clientMessageId", "cifrato"} or dati["tipo"] != "invia"
            or not isinstance(dati["clientMessageId"], str)
            or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", dati["clientMessageId"])
            or not isinstance(dati["cifrato"], str) or len(dati["cifrato"]) > 1403
            or not re.fullmatch(r"u2\.[A-Za-z0-9_-]{68,1400}", dati["cifrato"])):
        raise ValueError("Messaggio non valido")
