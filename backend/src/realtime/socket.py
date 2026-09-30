"""Un solo socket per chat, notifiche, presenza, typing e invalidazioni."""

import asyncio
import logging
import re
import time
import uuid
from collections import deque
from dataclasses import dataclass, field

import anyio
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from src.chat_pratiche import segnali
from src.chat_pratiche.configurazione import configurazione
from src.realtime import presenza, token
from src.realtime import socket_operazioni as operazioni
from src.realtime.contratti import json_limitato, uuid_canonico
from src.realtime.errori import richiedi
from src.realtime.limite_ingresso import LimiteIngresso
from src.realtime.uscita import Uscita

router = APIRouter()
PROTOCOLLO = "universo.realtime.v1"


@dataclass
class Stato:
    browser: WebSocket
    accesso: str
    connessione: str
    sid: str
    ultimo: int
    uid: int
    risorse: object
    uscita: Uscita
    inviate: dict = field(default_factory=dict)
    confermate: deque = field(default_factory=lambda: deque(maxlen=256))

    async def invia(self, dati):
        token.decodifica(self.accesso)
        await self.uscita.invia(dati)

    async def db(self, funzione, *args):
        return await self.risorse.letture.esegui(self.connessione, funzione, *args)


def handshake(browser):
    origini = {x.strip() for x in configurazione().chat_universo_origini.split(",") if x.strip()}
    origine = browser.headers.getlist("origin")
    richiedi(
        not origine or (len(origine) == 1 and origine[0] in origini),
        "origin_not_allowed",
        403,
    )
    richiedi(not browser.query_params, "invalid_handshake")
    protocolli = browser.scope.get("subprotocols", [])
    tokens = [p[4:] for p in protocolli if p.startswith("jwt.")]
    richiedi(
        PROTOCOLLO in protocolli and len(tokens) == 1 and len(protocolli) == 2,
        "invalid_token",
        401,
    )
    return tokens[0]


async def osserva(s):
    presenti, prossima = set(), 0
    with segnali.ascolta(0) as sveglia:
        while True:
            sveglia.clear()
            adesso = time.monotonic()
            valori, s.ultimo, online = await s.db(
                operazioni.aggiorna,
                s.accesso,
                (s.connessione, s.sid),
                s.ultimo,
                adesso >= prossima,
            )
            attuali = presenti if online is None else online
            with s.uscita.trattieni(valori):
                for frame in presenza.transizioni(presenti, attuali):
                    await s.invia(frame)
                if online is not None:
                    presenti, prossima = online, adesso + 5
                for frame in valori:
                    await consegna(s, frame)
            await segnali.attendi(sveglia)


async def consegna(s, frame):
    did = frame["payload"].get("deliveryId")
    if did:
        if did in s.confermate or time.monotonic() - s.inviate.get(did, -100) < 5:
            return
        richiedi(did in s.inviate or len(s.inviate) < 128, "slow_consumer", 429)
        if not await s.db(operazioni.prepara, s.accesso, (s.connessione, did)):
            return
        s.inviate[did] = time.monotonic()
    await s.invia(frame)


async def ricevi(s):
    limite = LimiteIngresso()
    while True:
        raw = await s.browser.receive_text()
        d = None
        try:
            d = json_limitato(raw)
            richiedi(
                set(d) == {"channel", "payload"}
                and type(d["payload"]) is dict
                and d["channel"] in ("chat", "notification", "system"),
                "invalid_message",
            )
        except HTTPException:
            d = None
            await errore(s, "invalid_message")
        valido, chiudi = limite.consenti(d if d and isinstance(d.get("payload"), dict) else {})
        richiedi(not chiudi, "rate_limited", 401)
        if not valido:
            await errore(s, "rate_limited", d)
        elif d is not None:
            await comando(s, d)


async def ack(s, p):
    richiedi(set(p) == {"type", "deliveryId"} and p["type"] == "DELIVERY_ACK", "invalid_ack")
    did = uuid_canonico(p["deliveryId"])
    if did in s.confermate:
        return
    richiedi(did in s.inviate, "delivery_not_received", 403)
    await s.risorse.comandi.esegui(s.uid, operazioni.conferma, s.accesso, (s.connessione, did))
    s.inviate.pop(did, None)
    s.confermate.append(did)


async def comando(s, d):
    try:
        if d["channel"] == "system":
            await ack(s, d["payload"])
            return
        risultato = await s.risorse.comandi.esegui(s.uid, operazioni.elabora, s.accesso, d)
        segnali.pubblica(0)
        if risultato:
            await consegna(s, risultato)
    except HTTPException as e:
        if e.status_code == 401:
            raise
        await errore(s, str(e.detail), d)
    except Exception:
        logging.getLogger("ersaf.realtime").exception("Comando realtime non elaborato")
        await errore(s, "processing_failed", d)


async def errore(s, codice, envelope=None):
    p = dict(type="error", code=codice, message="Operazione non disponibile.")
    envelope = envelope or {}
    payload = envelope.get("payload", {})
    cid = payload.get("clientMessageId")
    if (
        envelope.get("channel") == "chat"
        and payload.get("type") in ("CHAT", "TYPING")
        and isinstance(cid, str)
        and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", cid)
    ):
        p["clientMessageId"] = cid
    await s.invia(dict(channel="system", payload=p))


async def scadenza(accesso):
    await asyncio.sleep(max(0, token.decodifica(accesso)["exp"] - time.time()))
    richiedi(False, "invalid_token", 401)


async def ciclo(s, identita):
    await s.browser.accept(subprotocol=PROTOCOLLO)
    await s.invia(
        dict(
            channel="system",
            payload=dict(
                type="connected",
                userId=str(identita.utente_id),
                protocol=PROTOCOLLO,
                channels=["chat", "notification"],
                clientWritableChannels=["chat"],
                clientControlTypes=["DELIVERY_ACK"],
            ),
        )
    )
    lavori = [asyncio.create_task(f) for f in (osserva(s), ricevi(s), scadenza(s.accesso))]
    try:
        finiti, _ = await asyncio.wait(lavori, return_when=asyncio.FIRST_COMPLETED)
        for lavoro in finiti:
            lavoro.result()
    finally:
        for lavoro in lavori:
            lavoro.cancel()
        await asyncio.gather(*lavori, return_exceptions=True)


@router.websocket("/ws")
async def socket(browser: WebSocket):
    s, conn, codice = None, None, 1000
    try:
        accesso = handshake(browser)
        token.decodifica(accesso)
        risorse = browser.app.state.realtime_risorse
        conn = str(uuid.uuid4())
        i, conn, sid, ultimo = await risorse.letture.esegui(conn, operazioni.avvia, accesso, conn)
        c = configurazione()
        uscita = Uscita(
            browser,
            risorse.uscita,
            (
                c.realtime_outbound_queue_frames,
                c.realtime_outbound_queue_bytes,
                c.realtime_send_timeout_millis / 1000,
            ),
        )
        s = Stato(browser, accesso, conn, sid, ultimo, i.utente_id, risorse, uscita)
        await ciclo(s, i)
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    except HTTPException as e:
        codice = (
            (1008 if s else 4401)
            if e.status_code == 401
            else (1008 if s else 4403)
            if e.status_code == 403
            else 1013
        )
    except Exception:
        logging.getLogger("ersaf.realtime").exception("Connessione realtime terminata per errore interno")
        codice = 1011
    finally:
        if conn:
            with anyio.CancelScope(shield=True):
                pulizia = asyncio.create_task(risorse.letture.finale(conn, operazioni.chiudi, conn))
                try:
                    await asyncio.shield(pulizia)
                except asyncio.CancelledError:
                    await pulizia
        try:
            await browser.close(code=codice)
        except RuntimeError:
            pass
