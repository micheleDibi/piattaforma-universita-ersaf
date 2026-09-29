"""Dataset sintetico per tutti i domini del servizio condiviso."""

import base64
import hashlib
import os
import struct

import jwt
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import text
from src.chat_pratiche.configurazione import configurazione
from src.realtime.accesso import nuova_sessione
from src.realtime.identita import carica
from src.realtime.token import emetti
from tests.support.archivi_realtime import TICKET
from tests.support.chat import chat, pratica  # noqa: F401


@pytest.fixture
def universo(chat, db, tmp_path, monkeypatch):
    key = bytes(range(32, 64))
    file = tmp_path / "jwt-test.txt"
    file.write_text(base64.b64encode(key).decode(), encoding="ascii")
    for nome, valore in dict(
        CHAT_UNIVERSO_JWT_FILE=str(file),
        CHAT_UNIVERSO_ORIGINI="https://universo.example.org",
        REALTIME_SCHEMA_TICKET="ersaf_test",
    ).items():
        monkeypatch.setenv(nome, valore)
    configurazione.cache_clear()
    for sql in TICKET:
        db.execute(text(sql))
    for tabella in (
        "realtime_auth_refresh_history",
        "realtime_auth_session",
        "realtime_person_conversation",
        "realtime_person_contact_acl",
        "realtime_message_seen_snapshot",
        "realtime_notification_seen_snapshot",
        "realtime_notification_bridge_state",
        "ticket_messaggio",
        "ticket_uditore",
        "ticket",
        "messaggio",
    ):
        db.execute(text("DELETE FROM " + tabella))
    i = carica(db, chat[1].utente_id)
    sessione, refresh = nuova_sessione(db, i, "test-browser")
    db.commit()
    token = emetti(sessione, refresh)["accessToken"]
    yield token, jwt.decode(token, key, algorithms=["HS256"], audience="universo-realtime-ws"), key
    configurazione.cache_clear()


def header(token):
    return {"Authorization": "Bearer " + token}


def cifra(materiale, dominio, uid, cid, testo="Messaggio sintetico", privato=False):
    decode = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
    encode = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")
    v, e = materiale["keyVersion"], materiale["epochHour"]
    tag = hashlib.sha256(cid.encode()).digest()[:16]
    nonce = os.urandom(12)
    flags = int(privato)
    aad = f"universo-realtime/u2\ncontext={dominio}\nsender={uid}\nmessageIdTag={encode(tag)}\nkeyVersion={v}\nepochHour={e}\nflags={flags}".encode()
    raw = AESGCM(decode(materiale["key"])).encrypt(nonce, testo.encode(), aad)
    return "u2." + encode(struct.pack(">BIB", v, e, flags) + tag + nonce + raw)


def frame_chat(ws):
    for _ in range(20):
        frame = ws.receive_json()
        if frame["channel"] == "chat" and frame["payload"].get("type") == "CHAT":
            return frame
        if frame["channel"] == "system" and frame["payload"].get("type") == "error":
            raise AssertionError(frame)
    raise AssertionError("Messaggio non ricevuto")
