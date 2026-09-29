"""Budget persistenti per utente, condivisi tra connessioni e processi."""

import hashlib
import time
from datetime import timedelta

from src.realtime.dati import esegui, ora
from src.realtime.errori import richiedi


def consuma(db, soggetto, quantita=120):
    chiave = hashlib.sha256(soggetto.encode()).digest()
    finestra = int(time.time()) // 60
    esegui(
        db,
        """INSERT INTO realtime_limite VALUES (:k,:f,0,:exp)
        ON DUPLICATE KEY UPDATE chiave=VALUES(chiave)""",
        dict(k=chiave, f=finestra, exp=ora() + timedelta(minutes=2)),
    )
    r = esegui(
        db, "SELECT finestra,conteggio FROM realtime_limite WHERE chiave=:k FOR UPDATE", dict(k=chiave)
    ).one()
    n = r.conteggio if r.finestra == finestra else 0
    richiedi(n < quantita, "rate_limited", 429)
    esegui(
        db,
        "UPDATE realtime_limite SET finestra=:f,conteggio=:n,scadenza=:exp WHERE chiave=:k",
        dict(k=chiave, f=finestra, n=n + 1, exp=ora() + timedelta(minutes=2)),
    )


def budget_messaggi(db, utente):
    esegui(
        db,
        """INSERT INTO chat_pratica_limite VALUES (:u,0,0)
        ON DUPLICATE KEY UPDATE utente_id=VALUES(utente_id)""",
        dict(u=utente),
    )
    r = esegui(
        db, "SELECT finestra,tentativi FROM chat_pratica_limite WHERE utente_id=:u FOR UPDATE", dict(u=utente)
    ).one()
    adesso = int(time.time())
    return (adesso, 0) if adesso - r.finestra >= 60 else tuple(r)
