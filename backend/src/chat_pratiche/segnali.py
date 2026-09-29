"""Risveglio immediato locale; la coda SQL copre gli altri processi."""
import asyncio
from contextlib import contextmanager
from weakref import WeakKeyDictionary

_cicli = WeakKeyDictionary()


@contextmanager
def ascolta(pratica_id):
    loop = asyncio.get_running_loop()
    gruppi = _cicli.setdefault(loop, {})
    evento = asyncio.Event()
    gruppi.setdefault(pratica_id, set()).add(evento)
    try:
        yield evento
    finally:
        gruppi[pratica_id].discard(evento)
        if not gruppi[pratica_id]:
            del gruppi[pratica_id]
        if not gruppi:
            _cicli.pop(loop, None)


def pubblica(pratica_id):
    gruppi = _cicli.get(asyncio.get_running_loop(), {})
    for evento in gruppi.get(pratica_id, set()) | gruppi.get(0, set()):
        evento.set()


async def attendi(evento):
    try:
        await asyncio.wait_for(evento.wait(), timeout=0.5)
    except TimeoutError:
        pass
