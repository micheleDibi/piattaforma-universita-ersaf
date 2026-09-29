"""Un solo contratto HKDF/AES-GCM per persone, pratiche e ticket."""

import hashlib
import hmac
import os
import struct
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from src.chat_pratiche.chiavi import deriva
from src.chat_pratiche.cifratura import codifica, decodifica
from src.chat_pratiche.configurazione import chiavi, configurazione
from src.realtime.conversazioni import autorizza
from src.realtime.dati import esegui
from src.realtime.errori import ErroreRealtime, richiedi
from src.realtime.memoria_crypto import cancella, decifra


def aad(c, mittente, coordinate, identita):
    formato, versione, epoca = coordinate
    campo = "messageIdTag" if formato == "u2" else "messageId"
    return (
        f"universo-realtime/{formato}\ncontext={c.dominio}\nsender={mittente}\n"
        f"{campo}={identita}\nkeyVersion={versione}\nepochHour={epoca}\nflags={c.flags}"
    ).encode()


def chiave(db, utente, c, coordinate):
    versione, epoca = coordinate
    richiedi((versione is None) == (epoca is None), "invalid_key_coordinates")
    corrente = int(time.time()) // 3600
    versione = configurazione().chat_chiave_versione if versione is None else versione
    epoca = corrente if epoca is None else epoca
    richiedi(
        type(versione) is int and 1 <= versione <= 255 and type(epoca) is int and 490896 <= epoca <= corrente,
        "invalid_key_coordinates",
    )
    richiedi(versione in chiavi(), "invalid_key_coordinates")
    if versione != configurazione().chat_chiave_versione or epoca != corrente:
        autorizza_storico(db, utente, c, (versione, epoca))
    chiave = bytearray(deriva(versione, epoca, c.dominio))
    try:
        return dict(
            format="u2", algorithm="AES-256-GCM", key=codifica(chiave), keyVersion=versione, epochHour=epoca
        )
    finally:
        cancella(chiave)


def autorizza_storico(db, utente, c, coordinate):
    # I ticket seguono la composizione corrente anche per gli utenti aggiunti
    # successivamente. PERSON/PRACTICE conservano il requisito del grant.
    if c.tipo == "TICKET":
        autorizza(db, utente, (c.tipo, c.risorsa, c.pubblico))
        return
    versione, epoca = coordinate
    grant = esegui(
        db,
        """SELECT 1 FROM realtime_message_key_grant WHERE utente_id=:u
        AND canonical_context=:c AND key_version=:v AND epoch_hour=:e""",
        dict(u=utente, c=c.dominio, v=versione, e=epoca),
    ).scalar()
    richiedi(grant, "historical_key_access_denied", 403)


def apri(c, mittente, comando):
    chiave, valore = None, None
    try:
        cifrato, cid = comando["content"], comando["clientMessageId"]
        richiedi(cifrato.startswith("u2."), "invalid_ciphertext")
        raw = decodifica(cifrato[3:])
        richiedi(51 <= len(raw) <= 1050 and codifica(raw) == cifrato[3:], "invalid_ciphertext")
        v, e, flag = struct.unpack(">BIB", raw[:6])
        tag = hashlib.sha256(cid.encode()).digest()[:16]
        richiedi(flag == c.flags and hmac.compare_digest(tag, raw[6:22]), "invalid_ciphertext")
        richiedi(
            v == configurazione().chat_chiave_versione and e == int(time.time()) // 3600,
            "key_epoch_stale",
            409,
        )
        chiave = bytearray(deriva(v, e, c.dominio))
        valore = decifra(chiave, raw[22:34], raw[34:], aad(c, mittente, ("u2", v, e), codifica(tag)))
        richiedi(valore.decode("utf-8").strip() and len(valore) <= 1000, "invalid_ciphertext")
        return valore, v, e
    except ErroreRealtime:
        cancella(valore)
        raise
    except Exception:
        cancella(valore)
        raise ErroreRealtime("invalid_ciphertext") from None
    finally:
        cancella(chiave)


def conserva(c, mittente, messaggio_id, materiale):
    valore, v, e = materiale
    nonce = os.urandom(12)
    chiave = None
    try:
        chiave = bytearray(deriva(v, e, c.dominio))
        cifrato = AESGCM(chiave).encrypt(nonce, valore, aad(c, mittente, ("u3", v, e), str(messaggio_id)))
        return "u3." + codifica(struct.pack(">BIB", v, e, c.flags) + nonce + cifrato)
    finally:
        cancella(chiave)
        cancella(valore)
