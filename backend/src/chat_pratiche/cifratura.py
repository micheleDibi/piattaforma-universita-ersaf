"""Protocollo Universo u2/u3 e lettura legacy v1; nessuna scrittura in chiaro."""

import base64
import hashlib
import os
import re
import struct

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAX_TESTO = 1000


def codifica(dati):
    return base64.urlsafe_b64encode(dati).decode().rstrip("=")


def decodifica(testo):
    return base64.urlsafe_b64decode(testo + "=" * (-len(testo) % 4))


def aad(formato, pratica, mittente, identita, versione, ora, peer=None, utente=None):
    dominio = f"PRACTICE:{pratica}:GROUP"
    if peer is not None:
        primo, secondo = sorted((int(peer), int(utente)))
        dominio = f"PRACTICE:{pratica}:{primo}:{secondo}"
    campo = "messageIdTag" if formato == "u2" else "messageId"
    return (f"universo-realtime/{formato}\ncontext={dominio}\nsender={mittente}\n"
            f"{campo}={identita}\nkeyVersion={versione}\nepochHour={ora}\nflags=0").encode()


def cifra(conversazione, testo, client_id):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", client_id) or not testo.strip() or len(testo.encode()) > MAX_TESTO:
        raise ValueError("Messaggio non valido o troppo lungo.")
    materiale = conversazione.chiave()
    versione, ora = materiale["keyVersion"], materiale["epochHour"]
    tag = hashlib.sha256(client_id.encode()).digest()[:16]
    nonce = os.urandom(12)
    c = conversazione.contesto
    dati = AESGCM(decodifica(materiale["key"])).encrypt(nonce, testo.encode(),
        aad("u2", c.pratica_id, c.utente_id, codifica(tag), versione, ora))
    return "u2." + codifica(struct.pack(">BIB", versione, ora, 0) + tag + nonce + dati)


def decifra(conversazione, record):
    testo = record["content"]
    c = conversazione.contesto
    if testo.startswith(("u2.", "u3.")):
        formato = testo[:2]
        raw = decodifica(testo[3:])
        if len(raw) < 35 or len(raw) > 1050:
            raise ValueError("Formato non valido")
        versione, ora, flags = struct.unpack(">BIB", raw[:6])
        if flags or not versione or not ora:
            raise ValueError("Contesto non valido")
        offset = 22 if formato == "u2" else 6
        identita = codifica(raw[6:22]) if formato == "u2" else str(record["messageId"])
        peer = record.get("recipientUserId") if str(record["senderUserId"]) == str(c.utente_id) else record["senderUserId"]
        tentativi = [None] if peer is None else [None, peer]
        for destinazione in tentativi:
            try:
                key = conversazione.chiave(versione, ora, destinazione)
                return AESGCM(decodifica(key["key"])).decrypt(raw[offset:offset+12], raw[offset+12:],
                    aad(formato, c.pratica_id, record["senderUserId"], identita, versione, ora,
                        destinazione, c.utente_id)).decode("utf-8")
            except Exception:
                if destinazione == tentativi[-1]:
                    raise
    # Lo storico Instant contiene anche testi non cifrati. Un valore che sembra
    # v1 ma fallisce l'autenticazione non viene mostrato come testo ordinario.
    if len(testo) >= 32 and len(testo) % 4 == 0 and re.fullmatch(r"[A-Za-z0-9+/]*={0,2}", testo):
        raw = base64.b64decode(testo, validate=True)
        key = hashlib.pbkdf2_hmac("sha256", f"universo_conv_pratiche_{c.pratica_id}_v1".encode(),
                                   b"universo_2025_v1", 12000, 32)
        return AESGCM(key).decrypt(raw[:12], raw[12:], None).decode("utf-8")
    return testo
