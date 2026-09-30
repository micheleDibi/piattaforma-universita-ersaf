import asyncio
import threading
from builtins import bytearray as buffer_mutabile
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from src.chat_pratiche import configurazione as configurazione_chiavi
from src.realtime import avvio, crypto, scrittura, snapshot_ids, testi
from src.realtime.errori import ErroreRealtime
from src.realtime.esecutore import Esecutore
from src.realtime.uscita import BudgetUscita, Uscita


@pytest.mark.parametrize(
    "raw",
    [
        "{}",
        "[true]",
        "[0]",
        "[-1]",
        "[1,1]",
        "[1.0]",
        "[9223372036854775808]",
        "[",
        "[" * 1200,
        "[" * 1200 + "0" + "]" * 1200,
    ],
)
def test_snapshot_persistito_non_puo_ampliare_appartenenza(raw):
    with pytest.raises(ErroreRealtime):
        snapshot_ids.decodifica(raw)
    assert snapshot_ids.decodifica("[1,9223372036854775807]") == [1, 9223372036854775807]


@pytest.mark.parametrize("valore", ["a\x00b", "a\x85b", "x" * 256, "\U0001f600" * 128, "\ud800"])
def test_testi_notifiche_rispettano_controlli_e_lunghezza_java(valore):
    with pytest.raises(ErroreRealtime):
        testi.produttore(valore)
    with pytest.raises(ErroreRealtime):
        testi.strutturato(valore, 255)


def test_testi_produttore_normalizzati_e_legacy_vuoto_ammesso():
    assert testi.produttore("\0  titolo  \n") == "titolo"
    assert testi.produttore(" riga\n\triga ", True) == "riga\n\triga"
    assert testi.testo("", multilinea=True) == ""
    with pytest.raises(ErroreRealtime):
        testi.strutturato(" titolo\n ", 255)


def test_errore_archivio_cancella_plaintext(monkeypatch):
    materiale = (bytearray(b"testo temporaneo"), 1, 497376)
    monkeypatch.setattr(crypto, "apri", lambda *args: materiale)

    def errore(*args):
        raise RuntimeError("archivio non disponibile")

    monkeypatch.setattr(scrittura.archivio, "inserisci", errore)
    with pytest.raises(RuntimeError):
        scrittura.archivia(None, None, {"from": "1"})
    assert materiale[0] == bytearray(len(materiale[0]))


@pytest.mark.parametrize("motivo", ["file", "versione_corrente"])
def test_keyring_parziale_azzerato_se_il_caricamento_fallisce(monkeypatch, motivo):
    configurazione_chiavi.svuota_chiavi()
    creati = []

    def registra_buffer(valore):
        creati.append(buffer_mutabile(valore))
        return creati[-1]

    def carica(file):
        if file == "manca":
            raise HTTPException(503, "Chiave di prova mancante")
        return b"s" * 32

    config = SimpleNamespace(
        chat_chiavi_file="1=prova" + (",2=manca" if motivo == "file" else ""), chat_chiave_versione=2
    )
    monkeypatch.setattr(configurazione_chiavi, "configurazione", lambda: config)
    monkeypatch.setattr(configurazione_chiavi, "leggi_segreto", carica)
    monkeypatch.setattr(configurazione_chiavi, "bytearray", registra_buffer, raising=False)
    with pytest.raises(HTTPException):
        configurazione_chiavi.chiavi()
    assert creati and all(not any(b) for b in creati)
    assert configurazione_chiavi.chiavi.cache_info().currsize == 0


def test_batch_uscita_concorre_al_budget_e_si_libera_su_errore():
    async def scenario():
        budget = BudgetUscita(32)
        uscita = Uscita(None, budget, (16, 100, 1))
        with pytest.raises(ValueError):
            with uscita.trattieni([{"message": "abc"}]):
                assert budget.usati > 0 and uscita.frames == 1
                with pytest.raises(ErroreRealtime):
                    with uscita.trattieni([{"message": "abc"}]):
                        pass
                raise ValueError()
        assert budget.usati == uscita.frames == uscita.bytes == 0

    asyncio.run(scenario())


def test_finalizzazione_attende_query_in_corso_anche_dopo_cancellazione():
    async def scenario():
        pool = Esecutore(1, 1, 1)
        inizio, fine, ordine = asyncio.Event(), threading.Event(), []
        loop = asyncio.get_running_loop()

        def rinnova():
            loop.call_soon_threadsafe(inizio.set)
            fine.wait(5)
            ordine.append("rinnovo")

        task = asyncio.create_task(pool.esegui("socket", rinnova))
        await inizio.wait()
        task.cancel()
        chiusura = asyncio.create_task(pool.finale("socket", ordine.append, "chiusura"))
        await asyncio.sleep(0)
        assert not chiusura.done()
        fine.set()
        await asyncio.gather(task, chiusura, return_exceptions=True)
        await pool.chiudi()
        assert ordine == ["rinnovo", "chiusura"]

    asyncio.run(scenario())


def test_ciclo_attende_transazione_prima_del_teardown(monkeypatch):
    async def scenario():
        inizio, fine, terminato = asyncio.Event(), threading.Event(), threading.Event()
        loop = asyncio.get_running_loop()

        def passo(_):
            loop.call_soon_threadsafe(inizio.set)
            fine.wait(5)
            terminato.set()

        monkeypatch.setattr(avvio, "passo", passo)
        monkeypatch.setattr(
            avvio, "configurazione", lambda: SimpleNamespace(realtime_manutenzione_secondi=60)
        )
        lavoro = asyncio.create_task(avvio.ciclo({}))
        await inizio.wait()
        lavoro.cancel()
        await asyncio.sleep(0)
        assert not lavoro.done()
        fine.set()
        with pytest.raises(asyncio.CancelledError):
            await lavoro
        assert terminato.is_set()

    asyncio.run(scenario())
