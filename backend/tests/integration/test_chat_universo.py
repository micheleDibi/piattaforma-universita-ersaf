import base64
import time
import uuid

import jwt
import pytest
from sqlalchemy import text, select, func
from starlette.websockets import WebSocketDisconnect

from src.chat_pratiche.configurazione import configurazione
from src.chat_pratiche.models import Messaggio
from src.chat_pratiche.socket_nativo import avvia, invia
from src.chat_pratiche.cifratura import cifra
from src.chat_pratiche.chiavi import ChiaviConversazione
from src.chat_pratiche.partecipanti import autorizza
from src.chat_pratiche.storico import pagina
from src.security.browser import nome_cookie
from tests.support.chat import chat, pratica  # noqa: F401

pytestmark = pytest.mark.mariadb


from tests.support.realtime import universo, frame_chat  # noqa: F401


def test_stessa_sessione_universo_stesso_storico(client, db, chat, universo):
    p, account, _ = chat
    token, _, _ = universo
    ctx, _ = autorizza(db, account.utente_id, p.pratica_id)
    cifrato = cifra(ChiaviConversazione(db, ctx), "Messaggio da Universo", "universo-1")
    with client.websocket_connect("wss://test.example.org/realtime/ws",
            subprotocols=["universo.realtime.v1", "jwt."+token], headers={"Origin":"https://universo.example.org"}) as ws:
        ws.send_json(dict(channel="chat", payload=dict(type="CHAT",destinationType="PRACTICE",
            destinationId=str(p.pratica_id),to=str(p.pratica_id),codice=p.pratica_numero,
            **{"from":str(account.utente_id)},content=cifrato,clientMessageId="universo-1")))
        evento = frame_chat(ws)
        assert evento["payload"]["content"].startswith("u3.")
        ws.send_json(dict(channel="system",payload=dict(type="DELIVERY_ACK",deliveryId=evento["payload"]["deliveryId"])))
    assert client.get(f"/pratiche/{p.pratica_id}/messaggi").json()["elementi"][0]["testo"] == "Messaggio da Universo"
    response = client.get("/realtime/api/v1/messages",params={"destinationType":"PRACTICE","conversationId":p.pratica_id},headers={"Authorization":"Bearer "+token})
    assert response.status_code == 200, response.text
    assert response.json()["items"][0]["messageId"] == int(evento["payload"]["messaggioId"])
    assert db.scalar(select(func.count()).select_from(Messaggio)) == 1


def test_cookie_non_sostituisce_token_universo_e_token_non_accede_api_app(client, chat, universo):
    p, _, _ = chat
    assert client.get("/realtime/api/v1/messages",params={"destinationType":"PRACTICE","conversationId":p.pratica_id}).status_code == 401
    client.cookies.clear()
    assert client.get(f"/pratiche/{p.pratica_id}/messaggi",headers={"Authorization":"Bearer "+universo[0]}).status_code == 401


@pytest.mark.parametrize("campo,valore",[("aud","altro"),("iss","altro"),("exp",1),("cid",999),("aid",999),("device","estraneo"),("role","Nazionale")])
def test_claims_alterati_rifiutati(client, chat, universo, campo, valore):
    token, payload, key = universo
    errato = jwt.encode({**payload,campo:valore},key,algorithm="HS256")
    risposta = client.get("/realtime/api/v1/messages",params={"destinationType":"PRACTICE","conversationId":chat[0].pratica_id},headers={"Authorization":"Bearer "+errato})
    assert risposta.status_code == 401


def test_revoca_sessione_universo_chiude_socket(client, db, universo):
    with client.websocket_connect("wss://test.example.org/realtime/ws",
            subprotocols=["universo.realtime.v1","jwt."+universo[0]],headers={"Origin":"https://universo.example.org"}) as ws:
        assert ws.receive_json()["payload"]["type"] == "connected"
        db.execute(text("UPDATE realtime_auth_session SET revoked_at=UTC_TIMESTAMP()"))
        db.commit()
        with pytest.raises(WebSocketDisconnect) as exc:
            while True:
                ws.receive_json()
        assert exc.value.code == 1008


def test_accesso_chiavi_richiede_partecipazione_e_contesto(client, chat, universo):
    p, _, _ = chat
    url = "/realtime/crypto/key"
    headers = {"Authorization":"Bearer "+universo[0]}
    body = dict(destinationType="PRACTICE",resourceId=str(p.pratica_id),resourceCode=p.pratica_numero)
    assert client.post(url,json=body,headers=headers).status_code == 200
    assert client.post(url,json={**body,"resourceCode":"errato"},headers=headers).status_code == 403
    assert client.post(url,json={**body,"destinationType":"PERSON"},headers=headers).status_code == 400


def test_due_socket_stesso_archivio_ack_duplicato_e_retry(client, db, chat, universo):
    from tests.integration.test_chat_nativa import collega, preparato
    p, _, _ = chat
    with collega(client, p.pratica_id) as uni, client.websocket_connect("wss://test.example.org/realtime/ws",
            subprotocols=["universo.realtime.v1","jwt."+universo[0]],headers={"Origin":"https://universo.example.org"}) as universo_ws:
        assert uni.receive_json()["tipo"] == "connesso"
        comando = preparato(client, p.pratica_id)
        uni.send_json(comando)
        evento = frame_chat(universo_ws)
        assert evento["payload"]["clientMessageId"] == comando["clientMessageId"]
        ack = dict(channel="system",payload=dict(type="DELIVERY_ACK",deliveryId=evento["payload"]["deliveryId"]))
        universo_ws.send_json(ack)
        universo_ws.send_json(ack)
        altro = preparato(client, p.pratica_id, "secondo")
        uni.send_json(altro)
        assert frame_chat(universo_ws)["payload"]["clientMessageId"] == "secondo"
    assert db.scalar(select(func.count()).select_from(Messaggio)) == 2


def test_cors_universo_isolato_dalle_api_cookie(chat, universo):
    from starlette.testclient import TestClient
    from src.chat_pratiche.cors import CorsApplicazioni
    from src.main import app
    cors = TestClient(CorsApplicazioni(app.router))
    headers = {"Origin":"https://universo.example.org", "Access-Control-Request-Method":"POST",
               "Access-Control-Request-Headers":"Authorization,Content-Type"}
    risposta = cors.options("/realtime/crypto/key",headers=headers)
    assert risposta.status_code == 200
    assert risposta.headers["access-control-allow-origin"] == headers["Origin"]
    assert "access-control-allow-credentials" not in risposta.headers
    assert cors.options("/auth/login",headers=headers).status_code == 400


def test_preflight_verifica_schema_reale_dei_test(chat, universo, db):
    from src.chat_pratiche.avvio import verifica_schema
    verifica_schema(db)


@pytest.mark.parametrize("scarto,esito", [(10,200),(60,401)])
def test_tolleranza_orologio_compatibile_con_java(client, chat, universo, scarto, esito):
    _, payload, key = universo
    token = jwt.encode({**payload,"iat":int(time.time())+scarto},key,algorithm="HS256")
    response = client.get("/realtime/api/v1/messages",
        params={"destinationType":"PRACTICE","conversationId":chat[0].pratica_id},
        headers={"Authorization":"Bearer "+token})
    assert response.status_code == esito
