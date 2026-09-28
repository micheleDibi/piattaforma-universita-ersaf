"""Trasporto Universo: riusa il token già emesso, senza creare altre sessioni."""
import asyncio
import json
import time
from collections import deque

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from src.database import SessionLocal
from src.chat_pratiche.configurazione import chiavi, configurazione
from src.chat_pratiche.identita_universo import valida
from src.chat_pratiche.partecipanti import autorizza
from src.chat_pratiche.protocollo import valida_invio
from src.chat_pratiche.scrittura import salva
from src.chat_pratiche.consegne import pendenti, conferma
from src.chat_pratiche import segnali
from src.chat_pratiche.consegne import conferma_invio

router = APIRouter()
PROTOCOLLO = "universo.realtime.v1"


def handshake(browser):
    origini = {x.strip() for x in configurazione().chat_universo_origini.split(",") if x.strip()}
    origine = browser.headers.get("origin")
    if origine is not None and origine not in origini:
        raise HTTPException(403)
    protocolli = [x.strip() for x in browser.headers.get("sec-websocket-protocol", "").split(",")]
    token = [x[4:] for x in protocolli if x.startswith("jwt.")]
    if PROTOCOLLO not in protocolli or len(token) != 1:
        raise HTTPException(401)
    return token[0]


def aggiorna(token):
    chiavi()
    with SessionLocal.begin() as db:
        identita = valida(db, token)
        return pendenti(db, identita.utente_id)


def invia(token, envelope):
    if set(envelope) - {"channel", "payload", "timestamp"} or envelope.get("channel") != "chat":
        raise ValueError()
    dati = envelope.get("payload", {})
    consentiti = {"type", "from", "to", "content", "timestamp", "destinationType", "destinationId", "codice", "clientMessageId", "isPublic"}
    if not isinstance(dati, dict) or set(dati) - consentiti or dati.get("type") != "CHAT" or dati.get("destinationType") != "PRACTICE":
        raise ValueError()
    with SessionLocal.begin() as db:
        identita = valida(db, token, attivita=True)
        contesto, _ = autorizza(db, identita.utente_id, int(dati["destinationId"]))
        if (str(dati.get("from")) != str(identita.utente_id) or dati.get("codice") != contesto.numero
                or str(dati.get("to")) != str(contesto.pratica_id) or dati.get("isPublic") not in (None, True)):
            raise HTTPException(403)
        comando = dict(tipo="invia", clientMessageId=dati.get("clientMessageId"), cifrato=dati.get("content"))
        valida_invio(comando)
        message_id = salva(db, contesto, comando)
        return conferma_invio(db, contesto, message_id, comando["clientMessageId"])


def ricevuta(token, identificativo):
    with SessionLocal.begin() as db:
        identita = valida(db, token)
        conferma(db, identita.utente_id, identificativo)


async def ricevi(browser, token, consegnate):
    richieste = deque()
    confermate = deque(maxlen=128)
    while True:
        raw = await browser.receive_text()
        ora = time.monotonic()
        while richieste and ora-richieste[0] > 60:
            richieste.popleft()
        if len(raw.encode()) > 4096 or len(richieste) >= 180:
            raise HTTPException(429)
        richieste.append(ora)
        envelope = json.loads(raw)
        if not isinstance(envelope, dict):
            raise ValueError()
        p = envelope.get("payload", {})
        if not isinstance(p, dict):
            raise ValueError()
        if envelope.get("channel") == "system" and p.get("type") == "DELIVERY_ACK":
            identificativo = p.get("deliveryId")
            if identificativo not in consegnate:
                if identificativo in confermate:
                    continue
                raise HTTPException(403)
            await asyncio.to_thread(ricevuta, token, identificativo)
            consegnate.discard(identificativo)
            confermate.append(identificativo)
        else:
            await invia_o_errore(browser, token, envelope, consegnate)


async def invia_o_errore(browser, token, envelope, consegnate):
    try:
        evento = await asyncio.to_thread(invia, token, envelope)
        segnali.pubblica(int(evento["payload"]["destinationId"]))
        identificativo = evento["payload"]["deliveryId"]
        if identificativo not in consegnate:
            if len(consegnate) >= 128:
                raise HTTPException(429)
            consegnate.add(identificativo)
            await asyncio.wait_for(browser.send_json(evento), timeout=5)
    except HTTPException as errore:
        if errore.status_code in (401, 403, 404, 503):
            raise
        code = "key_epoch_stale" if errore.detail == "key_epoch_stale" else "message_rejected"
        await browser.send_json(dict(channel="system", payload=dict(type="error", code=code,
            clientMessageId=envelope.get("payload", {}).get("clientMessageId"))))


async def osserva(browser, token, consegnate):
    with segnali.ascolta(0) as segnale:
        while True:
            segnale.clear()
            for evento in await asyncio.to_thread(aggiorna, token):
                identificativo = evento["payload"]["deliveryId"]
                if identificativo not in consegnate:
                    if len(consegnate) >= 128:
                        raise HTTPException(429)
                    consegnate.add(identificativo)
                    await asyncio.wait_for(browser.send_json(evento), timeout=5)
            await segnali.attendi(segnale)


async def esegui(browser, token):
    await asyncio.to_thread(aggiorna, token)
    await browser.accept(subprotocol=PROTOCOLLO)
    consegnate = set()
    lavori = [asyncio.create_task(ricevi(browser, token, consegnate)),
              asyncio.create_task(osserva(browser, token, consegnate))]
    try:
        completati, _ = await asyncio.wait(lavori, return_when=asyncio.FIRST_COMPLETED)
        for lavoro in completati:
            lavoro.result()
    finally:
        for lavoro in lavori:
            lavoro.cancel()
        await asyncio.gather(*lavori, return_exceptions=True)


@router.websocket("/chat-universo/ws")
async def socket_universo(browser: WebSocket):
    codice = 1000
    try:
        await esegui(browser, handshake(browser))
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    except HTTPException as errore:
        codice = 4401 if errore.status_code == 401 else 4403 if errore.status_code in (403, 404) else 1013
    except Exception:
        codice = 1011
    finally:
        try:
            await browser.close(code=codice)
        except RuntimeError:
            pass
