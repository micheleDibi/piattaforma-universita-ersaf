"""Socket nativa con la sessione cookie esistente; nessun trasporto Java."""
import asyncio
import hmac
import json
import logging
import time
import uuid
from collections import deque
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from src.config import get_impostazioni
from src.security.browser import nome_cookie, origine_url, token_csrf
from src.chat_pratiche.socket_nativo import avvia, aggiorna, invia
from src.chat_pratiche import presenza, segnali, socket_presenza

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


async def ricevi(browser, token, contesto):
    richieste = deque()
    while True:
        raw = await browser.receive_text()
        adesso = time.monotonic()
        while richieste and adesso - richieste[0] >= 60:
            richieste.popleft()
        if len(raw.encode()) > 4096 or len(richieste) >= 60:
            raise HTTPException(429)
        richieste.append(adesso)
        dati = json.loads(raw)
        if not isinstance(dati, dict):
            raise ValueError()
        try:
            evento = await asyncio.to_thread(invia, token, contesto, dati)
            segnali.pubblica(contesto.pratica_id)
            await asyncio.wait_for(browser.send_json(evento), timeout=5)
        except HTTPException as errore:
            if errore.status_code in (401, 403, 404, 503):
                raise
            await browser.send_json(dict(tipo="errore", clientMessageId=dati.get("clientMessageId"),
                messaggio=str(errore.detail), ricifra=errore.detail == "key_epoch_stale"))


async def osserva(browser, token, contesto, ultimo):
    # Il DB resta la sorgente durevole anche tra processi e dopo un riavvio.
    # Il lock della pratica in scrittura serializza gli ID della conversazione.
    with segnali.ascolta(contesto.pratica_id) as segnale:
        while True:
            segnale.clear()
            for evento in await asyncio.to_thread(aggiorna, token, contesto, ultimo):
                await asyncio.wait_for(browser.send_json(evento), timeout=5)
                ultimo = int(evento["id"])
            await segnali.attendi(segnale)


async def esegui(browser, token, dati):
    contesto, ultimo = dati
    connessione, lavori = str(uuid.uuid4()), []
    try:
        await browser.app.state.realtime_risorse.letture.esegui(connessione, presenza.apri, token, contesto, connessione)
        await browser.accept(subprotocol=PROTOCOLLO)
        await browser.send_json({"tipo": "connesso"})
        lavori = [asyncio.create_task(ricevi(browser, token, contesto)),
                  asyncio.create_task(osserva(browser, token, contesto, ultimo)),
                  asyncio.create_task(socket_presenza.osserva(browser, token, contesto, connessione))]
        completati, _ = await asyncio.wait(lavori, return_when=asyncio.FIRST_COMPLETED)
        for lavoro in completati:
            lavoro.result()
    finally:
        for lavoro in lavori:
            lavoro.cancel()
        await asyncio.gather(*lavori, return_exceptions=True)
        await socket_presenza.termina(browser, connessione)


@router.websocket("/pratiche/{pratica_id}/messaggi/socket")
async def chat_socket(browser: WebSocket, pratica_id: int):
    codice = 1000
    try:
        token = verifica_socket(browser.headers, browser.cookies)
        dati = await asyncio.to_thread(avvia, token, pratica_id)
        await esegui(browser, token, dati)
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    except HTTPException as errore:
        codice = 4401 if errore.status_code == 401 else 4403 if errore.status_code in (403, 404) else 1013
    except Exception as errore:
        codice = 1011
        logging.getLogger("ersaf.chat").warning("Connessione chat terminata: %s", type(errore).__name__)
    finally:
        try:
            await browser.close(code=codice)
        except RuntimeError:
            pass
