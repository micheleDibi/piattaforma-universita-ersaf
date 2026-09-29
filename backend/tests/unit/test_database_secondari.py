"""I database facoltativi non avviano connessioni implicite o fuori dai test."""

import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src import config, database_secondari as secondari

URL_TEST = "mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test"


@pytest.fixture(autouse=True)
def ambiente(monkeypatch):
    impostazioni = SimpleNamespace(
        ersaf_env="test", database_url=URL_TEST,
        database_url_gestione_pagamenti="mysql+pymysql://utente:esempio@db.invalid/gestione",
        database_url_sys_admin="mysql+pymysql://utente:esempio@db.invalid/amministrazione",
    )
    monkeypatch.setattr(secondari, "get_impostazioni", lambda: impostazioni)
    monkeypatch.setattr(config, "get_impostazioni", lambda: impostazioni)
    for variabile in secondari.VARIABILI:
        monkeypatch.delenv("TEST_" + variabile, raising=False)
    yield impostazioni
    for fabbrica in secondari._fabbriche.values():
        fabbrica.kw["bind"].dispose()
    secondari._fabbriche.clear()


def test_import_principale_tollera_database_facoltativi_malformati(ambiente):
    ambiente.database_url_gestione_pagamenti = "non-un-url"
    ambiente.database_url_sys_admin = "altro-valore-non-valido"
    modulo = runpy.run_path(str(Path(secondari.__file__).with_name("database.py")))
    assert not secondari._fabbriche
    modulo["engine"].dispose()


@pytest.mark.parametrize("variabile", secondari.VARIABILI)
def test_assenza_override_non_eredita_database_reali(variabile):
    with pytest.raises(RuntimeError, match="non e' configurata"):
        next(secondari.sessione_secondaria(variabile))
    assert not secondari._fabbriche


@pytest.mark.parametrize("url", [
    "mysql+pymysql://ersaf:ersaf@db.invalid:3307/ersaf_test",
    "mysql+pymysql://ersaf:ersaf@127.0.0.1:3306/ersaf_test",
    "mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/amministrazione",
    URL_TEST + "?unix_socket=/tmp/esempio.sock",
    "sqlite:///:memory:",
])
def test_override_esterno_al_perimetro_rifiutato(monkeypatch, url):
    variabile = "DATABASE_URL_SYS_ADMIN"
    monkeypatch.setenv("TEST_" + variabile, url)
    with pytest.raises(RuntimeError, match="loopback:3307/ersaf_test"):
        next(secondari.sessione_secondaria(variabile))
    assert not secondari._fabbriche


@pytest.mark.parametrize("variabile", secondari.VARIABILI)
@pytest.mark.parametrize("fallimento", [False, True])
def test_sessione_si_chiude_anche_se_il_consumatore_fallisce(monkeypatch, variabile, fallimento):
    monkeypatch.setenv("TEST_" + variabile, URL_TEST)
    generatore = secondari.sessione_secondaria(variabile)
    db = next(generatore)
    with patch.object(db, "close", wraps=db.close) as chiudi:
        if fallimento:
            with pytest.raises(ValueError, match="operazione fallita"):
                generatore.throw(ValueError("operazione fallita"))
        else:
            generatore.close()
        chiudi.assert_called_once()


def test_url_malformato_non_compare_nell_errore(monkeypatch, ambiente):
    ambiente.ersaf_env = "sviluppo"
    ambiente.database_url_sys_admin = "valore-riservato-non-valido"
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL_SYS_ADMIN non e' valida") as errore:
        next(secondari.sessione_secondaria("DATABASE_URL_SYS_ADMIN"))
    assert "valore-riservato" not in str(errore.value)
    assert errore.value.__suppress_context__
