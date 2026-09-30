"""Invii serializzati con budget per socket e globale; l'outbox resta nel DB."""

import asyncio
import json
from contextlib import contextmanager

from src.realtime.errori import richiedi


class BudgetUscita:
    def __init__(self, massimo=134217728):
        self.massimo, self.usati = massimo, 0

    def prenota(self, quantita):
        richiedi(self.usati + quantita <= self.massimo, "slow_consumer", 429)
        self.usati += quantita

    def libera(self, quantita):
        self.usati -= quantita


class Uscita:
    def __init__(self, browser, budget, limiti=(64, 131072, 10)):
        self.browser, self.budget = browser, budget
        self.max_frame, self.max_byte, self.timeout = limiti
        self.frames, self.bytes = 0, 0
        self.blocco = asyncio.Lock()

    @contextmanager
    def trattieni(self, frames):
        # Anche il batch estratto dal DB resta nel budget mentre un browser
        # lento blocca gli invii. Rimangono otto posti per ACK/errori/controlli.
        quantita = sum(len(json.dumps(f, ensure_ascii=False).encode("utf-8")) for f in frames)
        riserva = min(8, self.max_frame // 2)
        richiedi(
            len(frames) <= self.max_frame - riserva and self.bytes + quantita <= self.max_byte,
            "slow_consumer",
            429,
        )
        self.budget.prenota(quantita)
        self.frames += len(frames)
        self.bytes += quantita
        try:
            yield
        finally:
            self.frames -= len(frames)
            self.bytes -= quantita
            self.budget.libera(quantita)

    async def invia(self, dati):
        testo = json.dumps(dati, ensure_ascii=False, separators=(",", ":"))
        quantita = len(testo.encode("utf-8"))
        richiedi(
            self.frames < self.max_frame and self.bytes + quantita <= self.max_byte,
            "slow_consumer",
            429,
        )
        self.budget.prenota(quantita)
        self.frames += 1
        self.bytes += quantita
        try:
            # Il timeout comprende anche l'attesa dietro un altro invio bloccato.
            async with asyncio.timeout(self.timeout):
                async with self.blocco:
                    await self.browser.send_text(testo)
        finally:
            self.frames -= 1
            self.bytes -= quantita
            self.budget.libera(quantita)
