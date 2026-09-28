"""Adattamento limitato a una pratica; mai inoltrare payload arbitrari."""

import re


def invio_java(dati, contesto):
    if (set(dati) != {"tipo", "clientMessageId", "cifrato"} or dati["tipo"] != "invia"
            or not isinstance(dati["clientMessageId"], str)
            or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", dati["clientMessageId"])
            or not isinstance(dati["cifrato"], str) or len(dati["cifrato"]) > 1403
            or not re.fullmatch(r"u2\.[A-Za-z0-9_-]{68,1400}", dati["cifrato"])):
        raise ValueError("Messaggio non valido")
    return {"channel": "chat", "payload": {
        "type": "CHAT", "destinationType": "PRACTICE", "to": str(contesto.pratica_id),
        "destinationId": str(contesto.pratica_id), "codice": contesto.numero,
        "clientMessageId": dati["clientMessageId"], "content": dati["cifrato"],
    }}


def evento_pratica(envelope, contesto):
    p = envelope.get("payload", {})
    if not isinstance(p, dict):
        return None
    if (envelope.get("channel") != "chat" or p.get("type") != "CHAT"
            or p.get("destinationType") != "PRACTICE"
            or str(p.get("destinationId")) != str(contesto.pratica_id)
            or p.get("codice") != contesto.numero or not p.get("messaggioId")):
        return None
    return {"tipo": "messaggio", "id": str(p["messaggioId"]),
            "clientMessageId": p.get("clientMessageId") if str(p.get("from")) == str(contesto.utente_id) else None,
            "consegna": p.get("deliveryId")}
