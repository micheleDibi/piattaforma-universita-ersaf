"""WebSocket cookie/CSRF verso il browser, protocollo Universo solo sul tratto interno."""

import asyncio
import hmac
import json
import logging
import time
from collections import deque

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from websockets.asyncio.client import connect

from src.auth.visibilita import visibilita_di
from src.chat_pratiche.contesto import contesto_chat
from src.chat_pratiche.java import ServizioJava
from src.chat_pratiche.protocollo import evento_pratica, invio_java
from src.config import get_impostazioni
from src.database import SessionLocal
from src.security.browser import nome_cookie, origine_url, token_csrf
from src.security.sessioni import valida_sessione
from src.utenti.models import Utente

router = APIRouter()
PROTOCOLLO = "ersaf.pratiche.v1"


def verifica_socket(headers, cookies):
    imp = get_impostazioni()
    if headers.get("origin") not in {origine_url(imp.frontend_base_url), *imp.lista_cors_origins}:
        raise HTTPException(403)
    token = cookies.get(nome_cookie(), "")
    protocolli = [p.strip() for p in headers.get("sec-websocket-protocol", "").split(",")]
    if (not token or PROTOCOLLO not in protocolli
            or not any(hmac.compare_digest(p, "csrf." + token_csrf(token)) for p in protocolli)):
        raise HTTPException(403)
    return token


def verifica_accesso(token, pratica_id):
    with SessionLocal() as db:
        valida = valida_sessione(db, token)
        if valida is None:
            raise HTTPException(401)
        utente = db.get(Utente, valida[1])
        return contesto_chat(db, pratica_id, visibilita_di(db, utente), utente)


async def mantieni_accesso(token, pratica_id, contesto):
    while True:
        await asyncio.sleep(20)
        if await asyncio.to_thread(verifica_accesso, token, pratica_id) != contesto:
            raise HTTPException(403)


async def dal_browser(browser, remoto, contesto, token, consegne):
    invii = deque()
    while True:
        raw = await browser.receive_text()
        if len(raw) > 4096:
            raise ValueError()
        dati = json.loads(raw)
        if not isinstance(dati, dict):
            raise ValueError()
        if dati.get("tipo") == "conferma":
            identificativo = dati.get("consegna")
            if isinstance(identificativo, str) and identificativo in consegne:
                consegne.remove(identificativo)
                await remoto.send(json.dumps({"type": "DELIVERY_ACK", "deliveryId": identificativo}))
            continue
        if await asyncio.to_thread(verifica_accesso, token, contesto.pratica_id) != contesto:
            raise HTTPException(403)
        adesso = time.monotonic()
        while invii and invii[0] < adesso - 60:
            invii.popleft()
        if len(invii) >= 20:
            raise HTTPException(429)
        invii.append(adesso)
        await remoto.send(json.dumps(invio_java(dati, contesto)))


async def da_java(browser, remoto, contesto, consegne):
    async for raw in remoto:
        envelope = json.loads(raw)
        evento = evento_pratica(envelope, contesto)
        if evento:
            if evento.get("consegna"):
                if len(consegne) >= 128:
                    raise ValueError()
                consegne.add(evento["consegna"])
            await browser.send_json(evento)
        elif envelope.get("channel") == "system" and envelope.get("payload", {}).get("type") == "error":
            await browser.send_json({"tipo": "errore", "clientMessageId": envelope["payload"].get("clientMessageId"),
                                     "messaggio": "Invio non riuscito. Riprova.",
                                     "ricifra": envelope["payload"].get("code") == "key_epoch_stale"})


@router.websocket("/pratiche/{pratica_id}/messaggi/socket")
async def chat_socket(browser: WebSocket, pratica_id: int):
    java = None
    lavori = []
    try:
        token = verifica_socket(browser.headers, browser.cookies)
        contesto = await asyncio.to_thread(verifica_accesso, token, pratica_id)
        java = await asyncio.to_thread(ServizioJava, contesto)
        async with connect(java.socket_url, origin=java.origine,
                           subprotocols=["universo.realtime.v1", "jwt." + java.token],
                           max_size=65536, max_queue=16, open_timeout=10) as remoto:
            await browser.accept(subprotocol=PROTOCOLLO)
            await browser.send_json({"tipo": "connesso"})
            consegne = set()
            lavori = [asyncio.create_task(dal_browser(browser, remoto, contesto, token, consegne)),
                      asyncio.create_task(da_java(browser, remoto, contesto, consegne)),
                      asyncio.create_task(mantieni_accesso(token, pratica_id, contesto))]
            completati, _ = await asyncio.wait(lavori, return_when=asyncio.FIRST_COMPLETED)
            for lavoro in completati:
                lavoro.result()
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    except Exception as errore:
        # Solo la classe: eccezioni di trasporto possono contenere header segreti.
        logging.getLogger("ersaf.chat").warning("Connessione chat terminata: %s", type(errore).__name__)
    finally:
        for lavoro in lavori:
            lavoro.cancel()
        if lavori:
            await asyncio.gather(*lavori, return_exceptions=True)
        if java:
            await asyncio.to_thread(java.chiudi)
        try:
            await browser.close(code=1012)
        except RuntimeError:
            pass
