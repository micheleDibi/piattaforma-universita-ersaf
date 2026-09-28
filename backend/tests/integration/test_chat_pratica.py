import asyncio
import json

import pytest
from starlette.websockets import WebSocketDisconnect

from src.chat_pratiche import rotte, socket
from src.chat_pratiche.cifratura import cifra, codifica
from src.security.browser import nome_cookie, token_csrf
from tests.integration.test_documento_pratica import pratica  # noqa: F401

pytestmark = pytest.mark.mariadb


class JavaFinto:
    # Il test non apre connessioni verso alcun servizio reale.
    socket_url = "ws://example.invalid/ws"
    origine = "https://example.invalid"
    token = "token-sintetico"
    chiuse = 0
    def __init__(self, contesto): self.contesto = contesto
    def chiudi(self): type(self).chiuse += 1
    def chiave(self, *args): return dict(keyVersion=1, epochHour=497292, key=codifica(bytes(32)))
    def richiesta(self, metodo, path, **options):
        assert path == "/api/v1/messages"
        return dict(items=[dict(messageId=42, senderUserId=self.contesto.utente_id,
            senderName="Operatore di prova", content="Messaggio storico", createdAt="2026-09-28T08:00:00Z")],
            cryptoContext=dict(destinationType="PRACTICE", resourceId=str(self.contesto.pratica_id), resourceCode=self.contesto.numero),
            nextCursor=None, hasMore=False)


def test_storico_preparazione_csrf_e_contesto(client, pratica, monkeypatch):
    monkeypatch.setattr(rotte, "ServizioJava", JavaFinto)
    url = f"/pratiche/{pratica.pratica_id}/messaggi"
    risultato = client.get(url)
    assert risultato.status_code == 200, risultato.text
    assert risultato.json()["elementi"][0]["testo"] == "Messaggio storico"
    assert "token" not in risultato.text and "chiave" not in risultato.text
    assert risultato.headers["cache-control"] == "no-store"
    dati = dict(testo="Nuovo messaggio", clientMessageId="msg-1")
    assert client.post(url + "/prepara", json=dati).status_code == 403
    headers = {"X-CSRF-Token": token_csrf(client.cookies.get(nome_cookie()))}
    risposta = client.post(url + "/prepara", json=dati, headers=headers)
    assert risposta.status_code == 200
    assert risposta.json()["cifrato"].startswith("u2.")
    assert set(risposta.json()) == {"cifrato", "clientMessageId"}
    assert client.get("/pratiche/999999999/messaggi").status_code == 404
    assert JavaFinto.chiuse >= 2


def test_socket_isola_canale_e_revoca_sessione(client, pratica, monkeypatch):
    istanze = []
    class Remoto:
        async def __aenter__(self):
            self.coda = asyncio.Queue(); self.invii = []; istanze.append(self)
            return self
        async def __aexit__(self, *args): pass
        def __aiter__(self): return self
        async def __anext__(self): return await self.coda.get()
        async def send(self, raw):
            dati = json.loads(raw); self.invii.append(dati)
            if dati.get("channel") == "chat":
                p = dati["payload"]
                # Un evento personale non deve attraversare il ponte.
                await self.coda.put(json.dumps({"channel": "chat", "payload": {**p, "destinationType": "PERSON", "messaggioId": "900"}}))
                await self.coda.put(json.dumps({"channel": "chat", "payload": {**p, "from": str(contesto.utente_id), "messaggioId": "42", "deliveryId": "consegna-42"}}))
    monkeypatch.setattr(socket, "ServizioJava", JavaFinto)
    monkeypatch.setattr(socket, "connect", lambda *a, **k: Remoto())
    token = client.cookies.get(nome_cookie())
    contesto = socket.verifica_accesso(token, pratica.pratica_id)
    protocols = [socket.PROTOCOLLO, "csrf." + token_csrf(token)]
    url = f"wss://test.example.org/pratiche/{pratica.pratica_id}/messaggi/socket"
    with client.websocket_connect(url, subprotocols=protocols, headers={"Origin": "https://test.example.org"}) as ws:
        assert ws.receive_json() == {"tipo": "connesso"}
        invio = dict(tipo="invia", clientMessageId="msg-42", cifrato=cifra(JavaFinto(contesto), "Ciao", "msg-42"))
        ws.send_json(invio)
        evento = ws.receive_json()
        assert evento == dict(tipo="messaggio", id="42", clientMessageId="msg-42", consegna="consegna-42")
        assert istanze[0].invii[0]["payload"]["destinationId"] == str(pratica.pratica_id)
        assert client.post("/auth/logout", headers={"X-CSRF-Token": token_csrf(token)}).status_code in {200, 204}
        ws.send_json(invio)
        with pytest.raises(WebSocketDisconnect): ws.receive_json()


def test_socket_non_accetta_origine_estranea(client, pratica):
    token = client.cookies.get(nome_cookie())
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"wss://test.example.org/pratiche/{pratica.pratica_id}/messaggi/socket",
                subprotocols=[socket.PROTOCOLLO, "csrf." + token_csrf(token)], headers={"Origin": "https://attacker.invalid"}):
            pytest.fail("Handshake accettato")


def test_grant_storico_negato_non_blocca_il_resto_della_chat(client, pratica, monkeypatch):
    from fastapi import HTTPException
    monkeypatch.setattr(rotte, "ServizioJava", JavaFinto)
    monkeypatch.setattr(rotte, "decifra", lambda *a: (_ for _ in ()).throw(HTTPException(403)))
    risposta = client.get(f"/pratiche/{pratica.pratica_id}/messaggi")
    assert risposta.status_code == 200
    assert risposta.json()["elementi"][0]["testo"] == "Messaggio non disponibile per questo account"
    monkeypatch.setattr(rotte, "decifra", lambda *a: (_ for _ in ()).throw(HTTPException(503)))
    assert client.get(f"/pratiche/{pratica.pratica_id}/messaggi").status_code == 503


def test_servizio_che_restituisce_un_altra_pratica_viene_rifiutato(client, pratica, monkeypatch):
    class JavaErrato(JavaFinto):
        def richiesta(self, *args, **kwargs):
            pagina = super().richiesta(*args, **kwargs)
            pagina["cryptoContext"]["resourceId"] = "99999999"
            return pagina
    monkeypatch.setattr(rotte, "ServizioJava", JavaErrato)
    risposta = client.get(f"/pratiche/{pratica.pratica_id}/messaggi")
    assert risposta.status_code == 503
    assert "Messaggio storico" not in risposta.text
