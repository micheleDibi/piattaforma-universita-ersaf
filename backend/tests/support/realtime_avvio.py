"""Configurazione completa sintetica prima dell'avvio dei client di prova."""

import asyncio
import base64

import pytest
from src.chat_pratiche.configurazione import chiavi, configurazione
from src.database import engine
from src.realtime import avvio
from tests.support.archivi_realtime import prepara, svuota


async def ciclo_controllato(stato):
    # I test di dominio pilotano bridge/manutenzione esplicitamente, evitando
    # che un timer importi notifiche mentre la fixture costruisce lo scenario.
    # Il test di lifespan ripristina il ciclo reale e ne verifica la readiness.
    await asyncio.Future()


@pytest.fixture
def realtime_configurato(db_pulito, tmp_path, monkeypatch):
    key = tmp_path / "realtime-sintetico.txt"
    key.write_text(base64.b64encode(bytes(range(32))).decode(), encoding="ascii")
    monkeypatch.setenv("CHAT_CHIAVI_FILE", f"1={key}")
    monkeypatch.setenv("CHAT_UNIVERSO_JWT_FILE", str(key))
    monkeypatch.setenv("CHAT_UNIVERSO_ORIGINI", "https://test.example.org")
    monkeypatch.setenv("REALTIME_SCHEMA_TICKET", "ersaf_test")
    configurazione.cache_clear()
    chiavi.cache_clear()
    with engine.begin() as connessione:
        prepara(connessione)
        svuota(connessione)
    ciclo_reale = avvio.ciclo
    monkeypatch.setattr(avvio, "ciclo", ciclo_controllato)
    yield ciclo_reale
    configurazione.cache_clear()
    chiavi.cache_clear()
