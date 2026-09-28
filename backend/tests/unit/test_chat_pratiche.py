import hashlib
import struct
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException

from src.chat_pratiche.cifratura import aad, cifra, codifica, decifra, decodifica
from src.chat_pratiche.contesto import ContestoChat
from src.chat_pratiche.protocollo import evento_pratica, invio_java
from src.chat_pratiche.socket import verifica_socket
from src.security.browser import nome_cookie, token_csrf

CONTESTO = ContestoChat(10, 100, "prova", 101, "PR-101", 102)
CHIAVE = bytes(range(32))


def servizio():
    return SimpleNamespace(contesto=CONTESTO, chiave=lambda *args: dict(key=codifica(CHIAVE), keyVersion=1, epochHour=497292))


def test_submission_u2_compatibile_con_aad_java():
    cifrato = cifra(servizio(), "Messaggio con accento: è", "test-messaggio-1")
    raw = decodifica(cifrato[3:])
    assert raw[:6] == struct.pack(">BIB", 1, 497292, 0)
    tag = codifica(hashlib.sha256(b"test-messaggio-1").digest()[:16])
    autenticazione = f"universo-realtime/u2\ncontext=PRACTICE:101:GROUP\nsender=10\nmessageIdTag={tag}\nkeyVersion=1\nepochHour=497292\nflags=0".encode()
    assert AESGCM(CHIAVE).decrypt(raw[22:34], raw[34:], autenticazione).decode() == "Messaggio con accento: è"
    with pytest.raises(ValueError):
        cifra(servizio(), "è" * 501, "id-1")


def test_storico_u3_e_v1_e_testo_precedente():
    nonce = bytes(range(12))
    clear = "Vecchio messaggio".encode()
    ciphertext = AESGCM(CHIAVE).encrypt(nonce, clear, aad("u3", 101, 10, "42", 1, 497292))
    record = dict(messageId=42, senderUserId=10, recipientUserId=20,
                  content="u3." + codifica(struct.pack(">BIB", 1, 497292, 0) + nonce + ciphertext))
    assert decifra(servizio(), record) == clear.decode()
    with pytest.raises(Exception):
        decifra(servizio(), {**record, "messageId": 43})
    import base64
    legacy_key = hashlib.pbkdf2_hmac("sha256", b"universo_conv_pratiche_101_v1", b"universo_2025_v1", 12000, 32)
    legacy = base64.b64encode(nonce + AESGCM(legacy_key).encrypt(nonce, clear, None)).decode()
    assert decifra(servizio(), {**record, "content": legacy}) == clear.decode()
    assert decifra(servizio(), {**record, "content": "Testo storico in chiaro"}) == "Testo storico in chiaro"


def test_gateway_non_consente_cambi_di_pratica_o_canale():
    messaggio = dict(tipo="invia", clientMessageId="uno", cifrato=cifra(servizio(), "Ciao", "uno"))
    result = invio_java(messaggio, CONTESTO)
    assert result["payload"]["destinationType"] == "PRACTICE"
    assert result["payload"]["destinationId"] == "101"
    for extra in ({"destinationId": "102"}, {"from": "20"}, {"channel": "notification"}):
        with pytest.raises(ValueError):
            invio_java({**messaggio, **extra}, CONTESTO)
    evento = {**result, "payload": {**result["payload"], "from": "10", "messaggioId": "42"}}
    assert evento_pratica(evento, CONTESTO)["id"] == "42"
    for campo, valore in (("destinationId", "102"), ("destinationType", "PERSON"), ("codice", "altro")):
        assert evento_pratica({**evento, "payload": {**evento["payload"], campo: valore}}, CONTESTO) is None


def test_handshake_richiede_origin_cookie_e_csrf():
    cookie = "sessione-di-prova"
    headers = {"origin": "https://test.example.org", "sec-websocket-protocol": "ersaf.pratiche.v1, csrf." + token_csrf(cookie)}
    assert verifica_socket(headers, {nome_cookie(): cookie}) == cookie
    for errate, cookies in (({**headers, "origin": "https://estraneo.invalid"}, {nome_cookie(): cookie}),
                           ({**headers, "sec-websocket-protocol": "ersaf.pratiche.v1"}, {nome_cookie(): cookie}), (headers, {})):
        with pytest.raises(HTTPException) as exc:
            verifica_socket(errate, cookies)
        assert exc.value.status_code == 403


def test_vettore_condiviso_validato_anche_da_java(monkeypatch):
    import json
    from pathlib import Path
    from src.chat_pratiche import cifratura
    v = json.loads((Path(__file__).parents[1] / "support/practice_crypto_vector.json").read_text(encoding="utf-8"))
    java = servizio()
    java.chiave = lambda *args: dict(key=v["key"], keyVersion=1, epochHour=v["epochHour"])
    monkeypatch.setattr(cifratura.os, "urandom", lambda n: bytes(range(n)))
    assert cifra(java, v["plaintext"], "bridge-compat-1") == v["u2"]
    assert decifra(java, dict(messageId=42, senderUserId=10, recipientUserId=20, content=v["u3"])) == v["plaintext"]
