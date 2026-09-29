"""Adatta il comando cookie Universita al dominio realtime condiviso."""

from fastapi import HTTPException

from src.chat_pratiche.partecipanti import autorizza
from src.realtime.identita import carica
from src.realtime.scrittura import salva as salva_messaggio


def salva(db, contesto, comando):
    corrente, _ = autorizza(db, contesto.utente_id, contesto.pratica_id)
    if corrente != contesto:
        raise HTTPException(403, "I riferimenti della pratica sono cambiati.")
    payload = dict(
        type="CHAT",
        destinationType="PRACTICE",
        to=str(contesto.pratica_id),
        destinationId=str(contesto.pratica_id),
        codice=contesto.numero,
        clientMessageId=comando["clientMessageId"],
        content=comando["cifrato"],
    )
    evento = salva_messaggio(db, carica(db, contesto.utente_id), payload, limite=20)
    return int(evento["messaggioId"])
