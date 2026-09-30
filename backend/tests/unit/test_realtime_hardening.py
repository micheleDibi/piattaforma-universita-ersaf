import asyncio
import threading

import pytest
from src.realtime.contratti import json_limitato
from src.realtime.errori import ErroreRealtime
from src.realtime.esecutore import Esecutore
from src.realtime.limite_ingresso import LimiteIngresso
from src.realtime.uscita import BudgetUscita, Uscita


def test_profondita_json_e_limiti_dedicati():
    assert json_limitato('{"a":' * 32 + "0" + "}" * 32)
    with pytest.raises(ErroreRealtime):
        json_limitato('{"a":' * 33 + "0" + "}" * 33)
    with pytest.raises(ErroreRealtime) as errore:
        json_limitato('{"a":"' + "x" * 4100 + '"}', 4096)
    assert errore.value.status_code == 413


def frame(tipo, canale="chat"):
    return dict(channel=canale, payload=dict(type=tipo))


@pytest.mark.parametrize("tipo,capacita", [("CHAT", 20), ("TYPING", 30), ("LIST_USERS", 5)])
def test_bucket_per_tipo_e_chiusura_solo_dopo_tre_violazioni(tipo, capacita):
    adesso = [0.0]
    limite = LimiteIngresso(lambda: adesso[0])
    for _ in range(capacita):
        assert limite.consenti(frame(tipo)) == (True, False)
    assert limite.consenti(frame(tipo)) == (False, False)
    assert limite.consenti(frame(tipo)) == (False, False)
    assert limite.consenti(frame(tipo)) == (False, True)
    adesso[0] = 1.0
    assert limite.consenti(frame(tipo)) == (True, False)


def test_limite_globale_e_ack_indipendenti():
    limite = LimiteIngresso(lambda: 0)
    for tipo, n in (("CHAT", 20), ("TYPING", 30), ("LIST_USERS", 5)):
        for _ in range(n):
            assert limite.consenti(frame(tipo))[0]
    for _ in range(45):
        assert limite.consenti(frame("DELIVERY_ACK", "system"))[0]
    assert not limite.consenti(frame("DELIVERY_ACK", "system"))[0]
    limite = LimiteIngresso(lambda: 0)
    for _ in range(20):
        limite.consenti(frame("CHAT"))
    assert not limite.consenti(frame("CHAT"))[0]
    assert limite.consenti(frame("DELIVERY_ACK", "system")) == (True, False)


def test_worker_limiti_ordine_per_utente_e_rilascio_dopo_errore():
    async def scenario():
        coda = Esecutore(workers=2, limite=3, per_chiave=2)
        avviato, sblocca, eseguiti = asyncio.Event(), threading.Event(), []
        loop = asyncio.get_running_loop()

        def lento():
            loop.call_soon_threadsafe(avviato.set)
            sblocca.wait(5)
            eseguiti.append(1)

        primo = asyncio.create_task(coda.esegui("a", lento))
        await avviato.wait()
        secondo = asyncio.create_task(coda.esegui("a", eseguiti.append, 2))
        await asyncio.sleep(0)
        with pytest.raises(ErroreRealtime, match="server_busy"):
            await coda.esegui("a", lambda: None)
        # Un utente diverso procede pur con la prima chiave impegnata.
        assert await coda.esegui("b", lambda: 9) == 9
        sblocca.set()
        await asyncio.gather(primo, secondo)
        assert eseguiti == [1, 2]
        with pytest.raises(ValueError):
            await coda.esegui("a", lambda: int("errato"))
        assert await coda.esegui("a", lambda: 7) == 7
        await coda.chiudi()
        assert coda.totale == 0 and not coda.code and not coda.conteggi
        with pytest.raises(ErroreRealtime):
            await coda.esegui("a", lambda: None)

    asyncio.run(scenario())


def test_worker_limite_globale_e_cancellazione_in_coda():
    async def scenario():
        coda = Esecutore(workers=1, limite=2, per_chiave=2)
        avviato, sblocca, eseguiti = asyncio.Event(), threading.Event(), []
        loop = asyncio.get_running_loop()

        def lento():
            loop.call_soon_threadsafe(avviato.set)
            sblocca.wait(5)

        primo = asyncio.create_task(coda.esegui("a", lento))
        await avviato.wait()
        secondo = asyncio.create_task(coda.esegui("b", eseguiti.append, "non eseguire"))
        await asyncio.sleep(0)
        with pytest.raises(ErroreRealtime):
            await coda.esegui("c", lambda: None)
        secondo.cancel()
        sblocca.set()
        await asyncio.gather(primo, secondo, return_exceptions=True)
        await coda.chiudi()
        assert not eseguiti and coda.totale == 0

    asyncio.run(scenario())


def test_uscita_limita_memoria_serializza_e_libera_su_cancellazione():
    async def scenario():
        iniziato, sblocca = asyncio.Event(), asyncio.Event()

        class Browser:
            async def send_text(self, testo):
                iniziato.set()
                await sblocca.wait()

        budget = BudgetUscita(20)
        uscita = Uscita(Browser(), budget, (2, 20, 5))
        primo = asyncio.create_task(uscita.invia(dict(a="b")))
        await iniziato.wait()
        secondo = asyncio.create_task(uscita.invia(dict(a="c")))
        await asyncio.sleep(0)
        with pytest.raises(ErroreRealtime):
            await uscita.invia(dict(a="d"))
        altra = Uscita(Browser(), budget)
        with pytest.raises(ErroreRealtime):
            await altra.invia(dict(a="e"))
        primo.cancel()
        secondo.cancel()
        await asyncio.gather(primo, secondo, return_exceptions=True)
        assert budget.usati == uscita.frames == uscita.bytes == 0

    asyncio.run(scenario())
