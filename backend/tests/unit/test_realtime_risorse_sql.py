"""Una release priva delle query non puo dichiararsi pronta."""
from pathlib import Path

import pytest
from src.realtime import avvio, dati


def test_tutte_le_query_richieste_sono_disponibili():
    dati.verifica_query()


@pytest.mark.parametrize("mancante", dati.QUERY_RICHIESTE)
@pytest.mark.parametrize("contenuto", [None, " \n"])
def test_query_assente_o_vuota_impedisce_avvio(monkeypatch, mancante, contenuto):
    leggi = Path.read_text

    def risorsa(path, *args, **kwargs):
        if path.stem == mancante and path.parent.name == "sql":
            if contenuto is None:
                raise FileNotFoundError(path.name)
            return contenuto
        return leggi(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", risorsa)
    with pytest.raises(RuntimeError, match=mancante):
        avvio.verifica()
    dati.query.cache_clear()
