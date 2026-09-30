"""Ammissione limitata e ordine per chiave, anche fra socket dello stesso utente."""

import asyncio
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from src.realtime.errori import richiedi


class Esecutore:
    def __init__(self, workers=2, limite=256, per_chiave=8):
        self.limite, self.per_chiave = limite, per_chiave
        self.totale, self.aperto = 0, True
        self.vuoto = asyncio.Event()
        self.vuoto.set()
        self.avanzamento = asyncio.Event()
        self.code, self.conteggi = {}, defaultdict(int)
        self.pronte = asyncio.Queue(maxsize=limite + workers)
        self.pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="realtime")
        self.lavoratori = [asyncio.create_task(self.lavora()) for _ in range(workers)]

    async def esegui(self, chiave, funzione, *args):
        richiedi(
            self.aperto and self.totale < self.limite and self.conteggi.get(chiave, 0) < self.per_chiave,
            "server_busy",
            503,
        )
        futuro = asyncio.get_running_loop().create_future()
        self.totale += 1
        self.vuoto.clear()
        self.conteggi[chiave] += 1
        if chiave not in self.code:
            self.code[chiave] = deque()
            self.pronte.put_nowait(chiave)
        self.code[chiave].append((futuro, partial(funzione, *args)))
        return await futuro

    async def finale(self, chiave, funzione, *args):
        # La chiusura attende uno spazio nella stessa coda: non puo essere
        # sorpassata da una lettura gia in corso che rinnova la presenza.
        while self.aperto and (self.totale >= self.limite or self.conteggi.get(chiave, 0) >= self.per_chiave):
            self.avanzamento.clear()
            await self.avanzamento.wait()
        return await self.esegui(chiave, funzione, *args)

    async def lavora(self):
        while (chiave := await self.pronte.get()) is not None:
            futuro, funzione = self.code[chiave].popleft()
            try:
                if not futuro.cancelled():
                    risultato = await asyncio.get_running_loop().run_in_executor(self.pool, funzione)
                    if not futuro.done():
                        futuro.set_result(risultato)
            except Exception as errore:
                if not futuro.done():
                    futuro.set_exception(errore)
            finally:
                self.rilascia(chiave)

    def rilascia(self, chiave):
        self.avanzamento.set()
        self.totale -= 1
        if not self.totale:
            self.vuoto.set()
        self.conteggi[chiave] -= 1
        if self.code[chiave]:
            self.pronte.put_nowait(chiave)
        else:
            del self.code[chiave]
            del self.conteggi[chiave]

    async def chiudi(self):
        self.aperto = False
        for coda in self.code.values():
            for futuro, _ in coda:
                futuro.cancel()
        # Le operazioni DB gia iniziate finiscono prima del rilascio delle risorse.
        await self.vuoto.wait()
        for _ in self.lavoratori:
            self.pronte.put_nowait(None)
        await asyncio.gather(*self.lavoratori)
        self.pool.shutdown(wait=True, cancel_futures=True)
