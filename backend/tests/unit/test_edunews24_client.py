"""Client HTTP verso EduNews24, con httpx.MockTransport: nessuna rete."""

from __future__ import annotations

import gzip
import json
import logging
import tracemalloc
import zlib

import httpx
import pytest

import src.edunews24.client as modulo_client
from src.edunews24.client import TETTO_BYTE, ClientEduNews24, ErroreEduNews24
from tests.support.edunews24 import (
    CONTATTO,
    HOST_SITO,
    URL_BASE,
    OrologioFinto,
    elenco,
    problema,
    risposta_http,
)

USER_AGENT = f"PiattaformaUniversita/1.0 (+{CONTATTO})"
JSON = "application/json; charset=utf-8"
PROBLEMA = "application/problem+json; charset=utf-8"


def _client(gestore, *, orologio=None, base=URL_BASE, totale=8):
    return ClientEduNews24(base, CONTATTO, timeout_connessione=3, timeout_lettura=5, timeout_totale=totale,
                           orologio=orologio or OrologioFinto(), trasporto=httpx.MockTransport(gestore))


def _json(dati, stato=200, **intestazioni):
    return risposta_http(stato, json.dumps(dati).encode(), content_type=JSON, **intestazioni)


def _errore(gestore, **argomenti) -> ErroreEduNews24:
    with pytest.raises(ErroreEduNews24) as errore:
        _client(gestore).leggi("/articles", argomenti.get("parametri", []), etag=argomenti.get("etag"))
    return errore.value


def test_url_intestazioni_e_parametri_in_ordine():
    richieste = []

    def gestore(request):
        richieste.append(request)
        return _json(elenco([]), cache_control="public, s-maxage=300", age="12",
                     etag='W/"abc"', x_edunews24_cache="stale")

    esito = _client(gestore, base=URL_BASE + "/").leggi(
        "/articles", [("category", "scuola"), ("has_video", "true"), ("cursor", "abc")])
    (richiesta,) = richieste
    assert str(richiesta.url) == f"{URL_BASE}/articles?category=scuola&has_video=true&cursor=abc"
    assert richiesta.headers["accept"] == "application/json"
    assert richiesta.headers["accept-encoding"] == "gzip"
    assert richiesta.headers["user-agent"] == USER_AGENT
    assert "if-none-match" not in richiesta.headers
    assert esito.stato == 200
    assert esito.corpo == elenco([])
    assert esito.etag == 'W/"abc"'
    assert esito.cache_control == "public, s-maxage=300"
    assert esito.age == "12"
    assert esito.stantia_a_monte is True


def test_if_none_match_solo_con_un_etag():
    richieste = []

    def gestore(request):
        richieste.append(request)
        return risposta_http(304, etag='W/"abc"', cache_control="public, s-maxage=300")

    esito = _client(gestore).leggi("/categories", [], etag='W/"abc"')
    assert richieste[0].headers["if-none-match"] == 'W/"abc"'
    assert esito.stato == 304 and esito.corpo is None and esito.etag == 'W/"abc"'
    assert esito.stantia_a_monte is False


def test_un_304_senza_etag_inviato_non_e_valido():
    errore = _errore(lambda _: risposta_http(304))
    assert errore.motivo == "risposta-non-valida" and errore.stato_http == 304


def test_un_redirect_non_si_segue():
    richieste = []

    def gestore(request):
        richieste.append(request)
        return risposta_http(302, location="https://example.org/altrove")

    with pytest.raises(ErroreEduNews24) as errore:
        _client(gestore).leggi("/articles", [])
    assert errore.value.motivo == "risposta-non-valida"
    assert len(richieste) == 1


def test_200_con_gzip():
    corpo = gzip.compress(json.dumps(elenco([{"id": 1}])).encode())
    esito = _client(lambda _: risposta_http(200, corpo, content_type=JSON, content_encoding="gzip")).leggi(
        "/articles", [])
    assert esito.corpo == elenco([{"id": 1}])


@pytest.mark.parametrize(("corpo", "motivo"), [
    (problema("invalid-cursor"), "cursore-rifiutato"),
    (problema("invalid-parameter", ["cursor"]), "cursore-rifiutato"),
    (problema("invalid-parameter", ["category"]), "categoria-sconosciuta"),
    (problema("invalid-parameter", ["region"]), "richiesta-rifiutata"),
    (problema("unknown-parameter", ["pippo"]), "richiesta-rifiutata"),
])
def test_classificazione_dei_400(corpo, motivo):
    errore = _errore(lambda _: risposta_http(400, json.dumps(corpo).encode(), content_type=PROBLEMA))
    assert errore.motivo == motivo and errore.stato_http == 400
    assert errore.guasto is False


@pytest.mark.parametrize(("risposta", "motivo", "stato"), [
    (lambda: risposta_http(400, b"errore", content_type="text/plain"), "risposta-non-valida", 400),
    (lambda: risposta_http(400, b"{", content_type=PROBLEMA), "risposta-non-valida", 400),
    (lambda: risposta_http(404, b"", content_type=PROBLEMA), "non-trovata", 404),
    (lambda: risposta_http(403, b"<html>", content_type="text/html"), "risposta-non-valida", 403),
    (lambda: risposta_http(500, b"", retry_after="30"), "errore-server", 500),
    (lambda: risposta_http(502, b"<html>", content_type="text/html"), "errore-server", 502),
    (lambda: risposta_http(200, b"<html></html>", content_type="text/html"), "risposta-non-valida", 200),
    (lambda: risposta_http(200, b"{non json", content_type=JSON), "risposta-non-valida", 200),
    (lambda: risposta_http(200, b"[1, 2]", content_type=JSON), "risposta-non-valida", 200),
    (lambda: risposta_http(201, b"{}", content_type=JSON), "risposta-non-valida", 201),
])
def test_risposte_non_utilizzabili(risposta, motivo, stato):
    errore = _errore(lambda _: risposta())
    assert (errore.motivo, errore.stato_http) == (motivo, stato)
    assert errore.guasto is True
    if stato == 500:
        assert errore.retry_after is None


def test_429_e_503_leggono_retry_after():
    errore = _errore(lambda _: risposta_http(429, b"{}", content_type=PROBLEMA, retry_after="7"))
    assert (errore.motivo, errore.stato_http, errore.retry_after) == ("rifiutata", 429, 7)
    errore = _errore(lambda _: risposta_http(429, b""))
    assert (errore.motivo, errore.retry_after) == ("rifiutata", None)
    # Un 429 del CDN a monte e' una pagina HTML, anche compressa in modo non ammesso.
    errore = _errore(lambda _: risposta_http(429, b"<html>", content_type="text/html", content_encoding="br",
                                             retry_after="12"))
    assert (errore.motivo, errore.retry_after) == ("rifiutata", 12)
    errore = _errore(lambda _: risposta_http(503, b"", retry_after="Mon, 28 Sep 2026 08:00:45 GMT"))
    assert (errore.motivo, errore.stato_http, errore.retry_after) == ("rifiutata", 503, 45)


def test_content_length_oltre_il_tetto():
    errore = _errore(lambda _: risposta_http(200, b"{}", content_type=JSON, content_length=str(TETTO_BYTE + 1)))
    assert errore.motivo == "troppo-grande"


def test_corpo_grezzo_oltre_il_tetto():
    errore = _errore(lambda _: risposta_http(200, b" " * (TETTO_BYTE + 1), content_type=JSON))
    assert errore.motivo == "troppo-grande"


def _bomba_gzip(mebibyte: int) -> bytes:
    compressore = zlib.compressobj(9, zlib.DEFLATED, 16 + zlib.MAX_WBITS)
    zeri = b"\0" * (1 << 20)
    parti = [compressore.compress(zeri) for _ in range(mebibyte)]
    return b"".join(parti) + compressore.flush()


def test_bomba_gzip_si_ferma_al_tetto_senza_consumare_memoria():
    bomba = _bomba_gzip(64)
    assert len(bomba) < 100_000
    client = _client(lambda _: risposta_http(200, bomba, content_type=JSON, content_encoding="gzip"))
    tracemalloc.start()
    try:
        with pytest.raises(ErroreEduNews24) as errore:
            client.leggi("/articles", [])
        _, picco = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert errore.value.motivo == "troppo-grande"
    assert picco < 4 * (1 << 20)


@pytest.mark.parametrize("codifica", ["gzip, gzip", "deflate", "br", "compress"])
def test_codifiche_non_ammesse(codifica):
    errore = _errore(lambda _: risposta_http(200, b"{}", content_type=JSON, content_encoding=codifica))
    assert errore.motivo == "risposta-non-valida"


def test_gzip_troncato_o_con_dati_dopo_la_fine():
    completo = gzip.compress(b'{"data": [], "links": {}}')
    errore = _errore(lambda _: risposta_http(200, completo[:-6], content_type=JSON, content_encoding="gzip"))
    assert errore.motivo == "risposta-non-valida"
    errore = _errore(lambda _: risposta_http(200, completo + b"altro", content_type=JSON, content_encoding="gzip"))
    assert errore.motivo == "risposta-non-valida"


def test_gzip_corrotto_e_json_troppo_annidato_sono_risposte_non_valide():
    # Non "rete": zlib.error e RecursionError sono errori della risposta.
    errore = _errore(lambda _: risposta_http(200, b"\x1f\x8b" + b"\xff" * 30, content_type=JSON,
                                             content_encoding="gzip"))
    assert (errore.motivo, errore.stato_http) == ("risposta-non-valida", 200)
    annidato = b"[" * 200_000 + b"]" * 200_000
    assert len(annidato) < TETTO_BYTE
    errore = _errore(lambda _: risposta_http(200, annidato, content_type=JSON))
    assert (errore.motivo, errore.stato_http) == ("risposta-non-valida", 200)
    assert errore.__suppress_context__ is True


class _Blocchi(httpx.SyncByteStream):
    """Corpo in piu' blocchi: l'orologio avanza a ogni blocco."""

    def __init__(self, blocchi, orologio, passo):
        self._blocchi, self._orologio, self._passo = blocchi, orologio, passo

    def __iter__(self):
        for blocco in self._blocchi:
            self._orologio.avanza(self._passo)
            yield blocco


def test_scadenza_totale_sul_corpo():
    orologio = OrologioFinto()
    blocchi = [b'{"data": [', b"", b"", b'], "links": {}}']
    client = _client(lambda _: httpx.Response(200, headers={"content-type": JSON},
                                              stream=_Blocchi(blocchi, orologio, 3)),
                     orologio=orologio, totale=8)
    with pytest.raises(ErroreEduNews24) as errore:
        client.leggi("/articles", [])
    assert errore.value.motivo == "tempo-scaduto"
    # Con blocchi rapidi la stessa risposta passa.
    orologio = OrologioFinto()
    client = _client(lambda _: httpx.Response(200, headers={"content-type": JSON},
                                              stream=_Blocchi(blocchi, orologio, 1)),
                     orologio=orologio, totale=8)
    assert client.leggi("/articles", []).corpo == {"data": [], "links": {}}


@pytest.mark.parametrize(("eccezione", "motivo"), [
    (httpx.ConnectTimeout, "tempo-scaduto"),
    (httpx.ReadTimeout, "tempo-scaduto"),
    (httpx.ConnectError, "rete"),
    (RuntimeError, "rete"),
])
def test_errori_di_rete_senza_dettagli(eccezione, motivo):
    def gestore(request):
        raise eccezione(f"errore verso {HOST_SITO} per {CONTATTO}")

    errore = _errore(gestore)
    assert errore.motivo == motivo
    assert errore.__suppress_context__ is True
    assert errore.__cause__ is None
    testo = f"{errore} {errore!r} {errore.args}"
    assert HOST_SITO not in testo and CONTATTO not in testo


def test_nessun_errore_riporta_host_o_contatto():
    errore = _errore(lambda _: risposta_http(404))
    assert str(errore) == "Chiamata a EduNews24 non riuscita."
    assert errore.__suppress_context__ is True


@pytest.mark.parametrize(("etag", "atteso"), [
    ('W/"abc"', 'W/"abc"'),
    ('"abc"', '"abc"'),
    ("abc", None),
    ('W/"a"b"', None),
    ('"' + "a" * 127 + '"', None),        # 129 caratteri
    ('"' + "a" * 126 + '"', '"' + "a" * 126 + '"'),
])
def test_etag_fuori_forma_si_scarta(etag, atteso):
    esito = _client(lambda _: _json(elenco([]), etag=etag)).leggi("/articles", [])
    assert esito.etag == atteso


def test_crea_trasporto_si_sostituisce_con_monkeypatch(monkeypatch):
    chiamate = []

    def gestore(request):
        chiamate.append(request)
        return _json(elenco([]))

    monkeypatch.setattr(modulo_client, "crea_trasporto", lambda: httpx.MockTransport(gestore))
    client = ClientEduNews24(URL_BASE, CONTATTO, timeout_connessione=3, timeout_lettura=5, timeout_totale=8)
    assert client.leggi("/categories", []).stato == 200
    assert len(chiamate) == 1


@pytest.fixture
def logging_ripristinato():
    root = logging.getLogger()
    nomi = ("httpx", "httpcore", "uvicorn", "uvicorn.error", "uvicorn.access",
            "sqlalchemy.engine", "sqlalchemy.pool")
    salvati = (list(root.handlers), root.level,
               {n: (logging.getLogger(n).level, list(logging.getLogger(n).handlers),
                    logging.getLogger(n).propagate) for n in nomi})
    yield
    gestori, livello, altri = salvati
    for gestore in list(root.handlers):
        root.removeHandler(gestore)
    for gestore in gestori:
        root.addHandler(gestore)
    root.setLevel(livello)
    for nome, (livello_nome, gestori_nome, propaga) in altri.items():
        logger = logging.getLogger(nome)
        logger.setLevel(livello_nome)
        logger.handlers = gestori_nome
        logger.propagate = propaga


def test_configura_logging_abbassa_httpx_e_httpcore(logging_ripristinato):
    from types import SimpleNamespace

    from src.logging_config import configura_logging

    configura_logging(SimpleNamespace(percorso_log=None, log_level="DEBUG"))
    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("httpcore").level == logging.WARNING
    assert not logging.getLogger("httpx").isEnabledFor(logging.INFO)
