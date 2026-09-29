import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from src.chat_pratiche import chiavi as modulo
from src.chat_pratiche.cifratura import codifica


def test_derivazione_identica_al_vettore_java(monkeypatch):
    vettore = json.loads((Path(__file__).parents[1]/"support/practice_crypto_vector.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(modulo, "chiavi", lambda: {1: bytes(range(32))})
    assert codifica(modulo.deriva(1, vettore["epochHour"], "PRACTICE:101:GROUP")) == vettore["key"]
    assert modulo.deriva(1, vettore["epochHour"], "PRACTICE:102:GROUP") != modulo.deriva(1, vettore["epochHour"], "PRACTICE:101:GROUP")
    with pytest.raises(HTTPException) as exc:
        modulo.deriva(2, vettore["epochHour"], "PRACTICE:101:GROUP")
    assert exc.value.status_code == 503
