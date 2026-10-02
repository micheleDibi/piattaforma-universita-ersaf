"""Osservazione e cleanup ordinati con le stesse risorse del servizio realtime."""

import asyncio
import anyio

from src.chat_pratiche import presenza
from src.realtime.socket_operazioni import chiudi


async def osserva(browser, token, contesto, connessione):
    letture = browser.app.state.realtime_risorse.letture
    precedenti = None
    while True:
        attuali = await letture.esegui(connessione, presenza.aggiorna, token, contesto, connessione)
        if attuali != precedenti:
            await asyncio.wait_for(browser.send_json(dict(tipo="presenza", utenti=sorted(map(str, attuali)))), timeout=5)
            precedenti = attuali
        await asyncio.sleep(5)


async def termina(browser, connessione):
    with anyio.CancelScope(shield=True):
        letture = browser.app.state.realtime_risorse.letture
        pulizia = asyncio.create_task(letture.finale(connessione, chiudi, connessione))
        try:
            await asyncio.shield(pulizia)
        except asyncio.CancelledError:
            await pulizia
