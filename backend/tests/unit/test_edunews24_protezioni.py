"""Retry-After, pausa, budget e semaforo delle chiamate a EduNews24."""

from __future__ import annotations

from email.utils import format_datetime
from datetime import datetime, timedelta, timezone

import pytest

from src.edunews24.protezioni import Budget, Pausa, Semaforo, leggi_retry_after
from tests.support.edunews24 import PARETE_FISSA, OrologioFinto

ADESSO = datetime.fromtimestamp(PARETE_FISSA, tz=timezone.utc)


def _data_http(scarto: timedelta) -> str:
    return format_datetime(ADESSO + scarto, usegmt=True)


@pytest.mark.parametrize(("valore", "atteso"), [
    ("30", 30),
    (" 7 ", 7),
    ("0", 1),
    ("3600", 3600),
    ("99999", 3600),
    ("-5", None),
    ("1.5", None),
    ("", None),
    ("adesso", None),
    ("\u0663\u0660", None),   # cifre arabo-indiane: non sono secondi validi
    (None, None),
    (30, None),
])
def test_retry_after_in_secondi(valore, atteso):
    assert leggi_retry_after(valore, PARETE_FISSA) == atteso


def test_retry_after_come_data_http():
    assert leggi_retry_after(_data_http(timedelta(seconds=90)), PARETE_FISSA) == 90
    assert leggi_retry_after(_data_http(timedelta(seconds=-90)), PARETE_FISSA) == 1
    assert leggi_retry_after(_data_http(timedelta(hours=5)), PARETE_FISSA) == 3600
    # Senza fuso vale UTC.
    senza_fuso = (ADESSO + timedelta(seconds=40)).strftime("%a, %d %b %Y %H:%M:%S")
    assert leggi_retry_after(senza_fuso, PARETE_FISSA) == 40
    assert leggi_retry_after("Mon, 99 Foo 2026 00:00:00 GMT", PARETE_FISSA) is None


def test_la_pausa_di_ripiego_raddoppia_fino_al_massimo():
    orologio = OrologioFinto()
    pausa = Pausa(30, orologio)
    durate = [pausa.rifiuto(None) for _ in range(9)]
    assert durate == [30, 60, 120, 240, 480, 960, 1920, 3600, 3600]


def test_con_retry_after_il_primo_si_rispetta_alla_lettera():
    pausa = Pausa(30, OrologioFinto())
    assert [pausa.rifiuto(5) for _ in range(3)] == [5, 30, 60]


def test_un_retry_after_lungo_prevale_sul_ripiego():
    pausa = Pausa(30, OrologioFinto())
    assert pausa.rifiuto(None) == 30
    assert pausa.rifiuto(600) == 600


def test_il_successo_azzera_la_sequenza():
    orologio = OrologioFinto()
    pausa = Pausa(30, orologio)
    pausa.rifiuto(None)
    pausa.rifiuto(None)
    pausa.successo()
    orologio.avanza(1000)
    assert pausa.rifiuto(None) == 30


def test_restante_arrotonda_per_eccesso_e_non_si_accorcia():
    orologio = OrologioFinto()
    pausa = Pausa(30, orologio)
    assert pausa.restante() == 0
    pausa.rifiuto(30)
    assert pausa.restante() == 30
    orologio.avanza(0.5)
    assert pausa.restante() == 30
    orologio.avanza(29)
    assert pausa.restante() == 1
    # Un rifiuto con una pausa piu' breve non accorcia quella in corso.
    pausa.successo()
    pausa.rifiuto(1)
    assert pausa.restante() == 1
    orologio.avanza(0.5)
    assert pausa.restante() == 1
    orologio.avanza(1)
    assert pausa.restante() == 0


def test_budget_trenta_al_minuto():
    orologio = OrologioFinto()
    budget = Budget(30, orologio=orologio)
    for _ in range(30):
        assert budget.prova()
        orologio.avanza(1)
    assert not budget.prova()
    # Il piu' vecchio e' di 30 secondi fa: il posto si libera fra 30.
    assert budget.secondi_al_prossimo() == 30
    orologio.avanza(30)
    assert budget.secondi_al_prossimo() == 1
    assert budget.prova()
    assert not budget.prova()


def test_budget_svuota():
    budget = Budget(1, orologio=OrologioFinto())
    assert budget.prova()
    assert not budget.prova()
    budget.svuota()
    assert budget.prova()


def test_semaforo_quattro_posti():
    semaforo = Semaforo(4)
    assert [semaforo.prova() for _ in range(5)] == [True, True, True, True, False]
    semaforo.rilascia()
    assert semaforo.prova()
