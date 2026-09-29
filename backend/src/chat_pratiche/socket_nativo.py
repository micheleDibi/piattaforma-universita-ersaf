"""Accesso e operazioni del socket sul solo database applicativo."""
from fastapi import HTTPException
from sqlalchemy import func, select

from src.database import SessionLocal
from src.security.sessioni import valida_sessione
from src.chat_pratiche.configurazione import chiavi
from src.chat_pratiche.models import Messaggio
from src.chat_pratiche.partecipanti import autorizza
from src.chat_pratiche.protocollo import valida_invio
from src.chat_pratiche.scrittura import salva
from src.chat_pratiche.storico import eventi


def contesto_sessione(db, token, pratica_id):
    valida = valida_sessione(db, token)
    if valida is None:
        raise HTTPException(401, "Sessione scaduta.")
    return autorizza(db, valida[1], pratica_id)[0]


def avvia(token, pratica_id):
    chiavi()
    with SessionLocal() as db:
        contesto = contesto_sessione(db, token, pratica_id)
        ultimo = db.scalar(select(func.max(Messaggio.messaggio_id)).where(Messaggio.pratica_id == pratica_id)) or 0
        return contesto, ultimo


def aggiorna(token, contesto, ultimo):
    with SessionLocal() as db:
        if contesto_sessione(db, token, contesto.pratica_id) != contesto:
            raise HTTPException(403)
        return eventi(db, contesto, ultimo)


def invia(token, contesto, dati):
    valida_invio(dati)
    with SessionLocal.begin() as db:
        if contesto_sessione(db, token, contesto.pratica_id) != contesto:
            raise HTTPException(403)
        identificativo = salva(db, contesto, dati)
    return dict(tipo="messaggio", id=str(identificativo), clientMessageId=dati["clientMessageId"])
