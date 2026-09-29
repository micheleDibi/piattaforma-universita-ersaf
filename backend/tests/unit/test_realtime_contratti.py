import pytest
from src.realtime.comandi import valida
from src.realtime.contratti import json_limitato
from src.realtime.errori import ErroreRealtime


@pytest.mark.parametrize(
    "raw",
    [
        '{"n":NaN}',
        '{"n":Infinity}',
        '{"n":1e999}',
        '{"n":1,"n":2}',
        '{"a":{"n":1,"n":2}}',
        "[]",
        "null",
        '{"\ud800":1}',
        '{"a":"\ud800"}',
        '{"a":1}'.encode("utf-16"),
        b'\xef\xbb\xbf{"a":1}',
    ],
)
def test_json_non_ambiguo(raw):
    with pytest.raises(ErroreRealtime) as errore:
        json_limitato(raw)
    assert errore.value.status_code == 400


def test_limite_json_conta_byte_utf8():
    with pytest.raises(ErroreRealtime) as errore:
        json_limitato('{"n":"' + "à" * 9000 + '"}')
    assert errore.value.status_code == 413


def test_normalizzazione_non_fa_passare_contesto_di_altri_canali():
    payload = dict(
        type="CHAT",
        destinationType="PERSON",
        to="2",
        content="u2.cifrato",
        clientMessageId="id-1",
        codice="falso",
        isPublic=False,
        destinationId="42",
    )
    d = valida(payload, 1)
    assert set(d) == {"type", "destinationType", "to", "content", "clientMessageId", "from"}
    assert d["from"] == "1"


def test_mittente_non_puo_impersonare_altro_utente():
    with pytest.raises(ErroreRealtime) as errore:
        valida({"type": "LIST_USERS", "from": "7"}, 1)
    assert errore.value.status_code == 403


@pytest.mark.parametrize("tipo", [[], {}, None, True])
def test_tipo_comando_non_testuale_rifiutato(tipo):
    with pytest.raises(ErroreRealtime):
        valida({"type": tipo}, 1)
