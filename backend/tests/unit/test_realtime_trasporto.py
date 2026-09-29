"""Trasporto Uvicorn reale su loopback; DB/auth sono coperti dalle suite MariaDB.

I timeout abbreviati verificano regole di chiusura, non prestazioni o RTT.
"""

import asyncio
import json
import socket
import threading
import time
from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest
import uvicorn
from fastapi import FastAPI
from src.realtime import socket as endpoint
from src.realtime.risorse import Risorse
from websockets.exceptions import ConnectionClosed

pytestmark = pytest.mark.filterwarnings(
    "ignore::DeprecationWarning:websockets.*",
    "ignore::DeprecationWarning:uvicorn.*",
    "ignore:The .websockets. implementation is deprecated:UserWarning",
)


@pytest.fixture
def trasporto(monkeypatch):
    scadenze = {"valido": time.time() + 60}
    chiuse = []
    monkeypatch.setattr(endpoint.token, "decodifica", lambda t: {"exp": scadenze[t]})
    monkeypatch.setattr(
        endpoint.operazioni, "avvia", lambda t, c: (SimpleNamespace(utente_id=1), c, "sid", 0)
    )
    monkeypatch.setattr(endpoint.operazioni, "aggiorna", lambda *args: ([], 0, set()))
    monkeypatch.setattr(endpoint.operazioni, "chiudi", chiuse.append)
    monkeypatch.setattr(endpoint.operazioni, "elabora", lambda t, d: d)

    @asynccontextmanager
    async def vita(app):
        app.state.realtime_risorse = risorse = Risorse()
        try:
            yield
        finally:
            await risorse.chiudi()

    app = FastAPI(lifespan=vita)
    app.include_router(endpoint.router)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=0,
        ws="uvicorn.protocols.websockets.websockets_impl:WebSocketProtocol",
        ws_max_size=16384,
        ws_max_queue=16,
        ws_ping_interval=0.05,
        ws_ping_timeout=0.1,
        ws_per_message_deflate=False,
        log_level="critical",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    thread.start()
    termine = time.monotonic() + 5
    while not server.started and thread.is_alive() and time.monotonic() < termine:
        time.sleep(0.01)
    try:
        assert server.started
        yield f"ws://127.0.0.1:{listener.getsockname()[1]}/ws", scadenze, chiuse
    finally:
        server.should_exit = True
        thread.join(5)
        listener.close()
        assert not thread.is_alive()


def collegamento(url, token="valido", **kw):
    from websockets.legacy.client import connect

    return connect(url, subprotocols=["universo.realtime.v1", "jwt." + token], **kw)


def test_frame_invalidi_non_chiudono_e_frame_enorme_chiude(trasporto):
    async def scenario():
        async with collegamento(trasporto[0]) as ws:
            assert json.loads(await ws.recv())["payload"]["type"] == "connected"
            await ws.send('{"channel":"chat","channel":"system"}')
            assert json.loads(await ws.recv())["payload"]["code"] == "invalid_message"
            d = dict(channel="chat", payload=dict(type="LIST_USERS"))
            await ws.send(json.dumps(d))
            assert json.loads(await ws.recv()) == d
            await ws.send("x" * 16385)
            with pytest.raises(ConnectionClosed) as errore:
                await asyncio.wait_for(ws.recv(), 2)
            assert errore.value.rcvd.code == 1009

    asyncio.run(scenario())


def test_scadenza_token_chiude_anche_senza_messaggi(trasporto):
    async def scenario():
        trasporto[1]["breve"] = time.time() + 0.2
        async with collegamento(trasporto[0], "breve") as ws:
            await ws.recv()
            with pytest.raises(ConnectionClosed) as errore:
                await asyncio.wait_for(ws.recv(), 2)
            assert errore.value.rcvd.code == 1008

    asyncio.run(scenario())


def test_ping_pong_e_chiusura_trasporto_senza_pong(trasporto):
    from websockets.legacy.client import WebSocketClientProtocol

    class SenzaPong(WebSocketClientProtocol):
        async def pong(self, data=b""):
            pass

    async def scenario():
        async with collegamento(trasporto[0]) as ws:
            await ws.recv()
            await asyncio.sleep(0.3)
            await ws.send(json.dumps(dict(channel="chat", payload=dict(type="LIST_USERS"))))
            assert json.loads(await asyncio.wait_for(ws.recv(), 2))["payload"]["type"] == "LIST_USERS"
        async with collegamento(trasporto[0], create_protocol=SenzaPong) as ws:
            await ws.recv()
            with pytest.raises(ConnectionClosed) as errore:
                await asyncio.wait_for(ws.recv(), 2)
            assert errore.value.rcvd.code == 1011

    asyncio.run(scenario())
