"""Presenza dei soli partecipanti della pratica, condivisa con il realtime."""

from fastapi import HTTPException

from src.database import SessionLocal
from src.chat_pratiche.partecipanti import autorizza
from src.security.sessioni import valida_sessione
from src.realtime import eventi, presenza, presenza_cookie
from src.realtime.transazioni import ritenta


def verifica(db, token, contesto):
    valida = valida_sessione(db, token)
    if valida is None:
        raise HTTPException(401, "Sessione scaduta.")
    attuale, persone = autorizza(db, valida[1], contesto.pratica_id)
    if attuale != contesto:
        raise HTTPException(403)
    return presenza_cookie.session_id(valida[0]), {p.utente_id for p in persone}


@ritenta
def apri(token, contesto, connessione):
    with SessionLocal.begin() as db:
        sid, _ = verifica(db, token, contesto)
        presenza.apri(db, contesto, connessione, sid)


@ritenta
def aggiorna(token, contesto, connessione):
    with SessionLocal.begin() as db:
        sid, persone = verifica(db, token, contesto)
        eventi.blocca(db, contesto.utente_id)
        presenza.rinnova(db, contesto, connessione, sid)
        return presenza.online_utenti(db) & persone
