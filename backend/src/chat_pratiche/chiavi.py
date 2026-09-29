"""Derivazione locale compatibile HKDF-SHA256 Universo, con grant storici."""
import hashlib
import time

from fastapi import HTTPException
from sqlalchemy import text
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from src.chat_pratiche.configurazione import chiavi, configurazione
from src.chat_pratiche.cifratura import codifica


def deriva(versione, ora, dominio):
    chiave = chiavi().get(versione)
    if chiave is None:
        raise HTTPException(503, "Chiave storica della chat non disponibile.")
    return HKDF(algorithm=hashes.SHA256(), length=32,
        salt=hashlib.sha256(b"universo-realtime-message-key/u2").digest(),
        info=f"version={versione}\nepochHour={ora}\ncontext={dominio}".encode()).derive(chiave)


class ChiaviConversazione:
    def __init__(self, db, contesto):
        self.db, self.contesto = db, contesto

    def chiave(self, versione=None, ora=None, peer=None):
        corrente = int(time.time()) // 3600
        config = configurazione()
        if (versione is None) != (ora is None):
            raise HTTPException(422, "Coordinate della chiave non valide.")
        versione = config.chat_chiave_versione if versione is None else versione
        ora = corrente if ora is None else ora
        if not isinstance(ora, int) or not 490896 <= ora <= corrente:
            raise HTTPException(422, "Coordinate della chiave non valide.")
        c = self.contesto
        dominio = f"PRACTICE:{c.pratica_id}:GROUP"
        if peer is not None:
            a, b = sorted((int(peer), c.utente_id))
            dominio = f"PRACTICE:{c.pratica_id}:{a}:{b}"
        if peer is not None or versione != config.chat_chiave_versione or ora != corrente:
            self._storico(dominio, versione, ora)
        return dict(key=codifica(deriva(versione, ora, dominio)), keyVersion=versione, epochHour=ora)

    def _storico(self, dominio, versione, ora):
        esiste = self.db.scalar(text("""SELECT 1 FROM realtime_message_key_grant
            WHERE utente_id=:utente AND canonical_context=:dominio
            AND key_version=:versione AND epoch_hour=:ora"""),
            dict(utente=self.contesto.utente_id, dominio=dominio, versione=versione, ora=ora))
        if not esiste:
            raise HTTPException(403, "Messaggio non disponibile per questo account.")
