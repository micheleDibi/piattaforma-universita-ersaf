"""Rotte /edunews24: contratto, filtri, cursori, funzione spenta e 503.

Con EDUNEWS24_BACKEND=memoria (conftest) i dati sono inventati; i casi del
backend http usano un MockTransport: nessuna chiamata di rete.
"""

from __future__ import annotations

import json

import httpx
import pytest

from src.config import Impostazioni
from src.edunews24.servizio import ServizioEduNews24
from tests.support import factories as f
from tests.support.edunews24 import CONTATTO, HOST_MEDIA, URL_BASE, OrologioFinto, problema, risposta_http
from tests.support.scenari import accedi, accedi_nazionale

pytestmark = pytest.mark.mariadb

ROTTE = ("/edunews24/notizie", "/edunews24/interpelli", "/edunews24/selezione-personale",
         "/edunews24/categorie")
CHIAVI = {"attiva", "elementi", "meta"}
CHIAVI_META = {"cursore_successivo", "aggiornato_il", "stantio"}
CHIAVI_NOTIZIA = {"tipo", "id", "titolo", "titolo_breve", "sintesi", "url", "pubblicato_il", "categoria",
                  "immagine", "video", "ha_video"}
CHIAVI_VIDEO = {"url", "tipo_mime", "copertina", "durata_secondi"}
CHIAVI_OPPORTUNITA = {"tipo", "id", "titolo", "sintesi", "url", "ente", "sede", "regioni", "nazionale",
                      "pubblicato_il", "scadenza", "stato", "classe_concorso", "figura", "posti"}
CHIAVI_SLUG_NOME = {"slug", "nome"}


@pytest.fixture
def sessione(client, db):
    _, intestazioni = accedi(client, db, ruolo=f.RUOLO_REGIONALE)
    return intestazioni


@pytest.fixture(params=["aderente", "provinciale", "regionale", "nazionale"])
def sessione_per_ruolo(request, client, db, mailer):
    if request.param == "nazionale":
        _, intestazioni = accedi_nazionale(client, db, mailer)
    else:
        ruolo = {"aderente": f.RUOLO_ADERENTE, "provinciale": f.RUOLO_PROVINCIALE,
                 "regionale": f.RUOLO_REGIONALE}[request.param]
        _, intestazioni = accedi(client, db, ruolo=ruolo)
    return intestazioni


def _servizio_http(monkeypatch, gestore):
    imp = Impostazioni(_env_file=None, edunews24_backend="http", edunews24_url_base=URL_BASE,
                       edunews24_contatto=CONTATTO, edunews24_host_media=HOST_MEDIA)
    servizio = ServizioEduNews24.da_impostazioni(imp, trasporto=httpx.MockTransport(gestore),
                                                 orologio=OrologioFinto())
    monkeypatch.setattr("src.edunews24.servizio._servizio", servizio)


def test_notizie_per_ogni_ruolo_con_due_pagine(client, sessione_per_ruolo):
    prima = client.get("/edunews24/notizie", headers=sessione_per_ruolo)
    assert prima.status_code == 200, prima.text
    assert prima.headers["cache-control"] == "no-store"
    corpo = prima.json()
    assert corpo["attiva"] is True and len(corpo["elementi"]) == 20
    cursore = corpo["meta"]["cursore_successivo"]
    assert cursore
    seconda = client.get("/edunews24/notizie", params={"cursore": cursore}, headers=sessione_per_ruolo)
    assert seconda.status_code == 200, seconda.text
    assert len(seconda.json()["elementi"]) == 10
    assert seconda.json()["meta"]["cursore_successivo"] is None


def test_chiavi_esatte_del_contratto(client, sessione):
    notizie = client.get("/edunews24/notizie", headers=sessione).json()
    assert set(notizie) == CHIAVI and set(notizie["meta"]) == CHIAVI_META
    assert notizie["meta"]["stantio"] is False and notizie["meta"]["aggiornato_il"]
    for notizia in notizie["elementi"]:
        assert set(notizia) == CHIAVI_NOTIZIA and notizia["tipo"] == "notizia"
        assert set(notizia["categoria"]) == CHIAVI_SLUG_NOME
    video = [n["video"] for n in notizie["elementi"] if n["video"]]
    assert video and all(set(v) == CHIAVI_VIDEO for v in video)
    assert any(n["titolo_breve"] for n in notizie["elementi"])
    assert any(n["titolo_breve"] is None for n in notizie["elementi"])

    for rotta, tipo in (("/edunews24/interpelli", "interpello"),
                        ("/edunews24/selezione-personale", "selezione-personale")):
        corpo = client.get(rotta, headers=sessione).json()
        assert set(corpo) == CHIAVI and set(corpo["meta"]) == CHIAVI_META
        for voce in corpo["elementi"]:
            assert set(voce) == CHIAVI_OPPORTUNITA and voce["tipo"] == tipo
            assert all(set(r) == CHIAVI_SLUG_NOME for r in voce["regioni"])
        assert any(v["regioni"] for v in corpo["elementi"])
        if tipo == "interpello":
            assert any(v["classe_concorso"] for v in corpo["elementi"])
            assert all(v["scadenza"] is None and v["stato"] is None and v["figura"] is None
                       and v["posti"] is None for v in corpo["elementi"])
        else:
            assert any(v["figura"] for v in corpo["elementi"]) and any(v["posti"] for v in corpo["elementi"])
            assert all(v["classe_concorso"] is None for v in corpo["elementi"])

    categorie = client.get("/edunews24/categorie", headers=sessione).json()
    assert set(categorie) == CHIAVI and categorie["meta"]["cursore_successivo"] is None
    assert [c["slug"] for c in categorie["elementi"]] == ["scuola", "universita", "concorsi", "rubriche"]
    assert all(set(c) == CHIAVI_SLUG_NOME for c in categorie["elementi"])


def test_filtri(client, sessione):
    video = client.get("/edunews24/notizie", params={"solo_video": "si"}, headers=sessione)
    assert video.status_code == 200 and video.json()["elementi"]
    assert all(n["ha_video"] for n in video.json()["elementi"])
    assert client.get("/edunews24/notizie", params={"solo_video": "true"}, headers=sessione).status_code == 422

    nazionale = client.get("/edunews24/interpelli", params={"area": "nazionale"}, headers=sessione)
    assert nazionale.status_code == 400
    assert nazionale.json() == {"detail": "L'area nazionale non è disponibile per gli interpelli."}
    selezione = client.get("/edunews24/selezione-personale", params={"area": "nazionale"}, headers=sessione)
    assert selezione.status_code == 200
    assert selezione.json()["elementi"] and all(v["nazionale"] for v in selezione.json()["elementi"])
    assert client.get("/edunews24/interpelli", params={"area": "atlantide"}, headers=sessione).status_code == 422

    vuota = client.get("/edunews24/interpelli", params={"area": "molise"}, headers=sessione)
    assert vuota.status_code == 200 and vuota.json()["elementi"] == []
    rubriche = client.get("/edunews24/notizie", params={"categoria": "rubriche"}, headers=sessione)
    assert rubriche.status_code == 200 and rubriche.json()["elementi"] == []

    sconosciuta = client.get("/edunews24/notizie", params={"categoria": "inesistente"}, headers=sessione)
    assert sconosciuta.status_code == 400 and sconosciuta.json() == {"detail": "Categoria sconosciuta."}
    fuori_forma = client.get("/edunews24/notizie", params={"categoria": "Non_Valida"}, headers=sessione)
    assert fuori_forma.status_code == 422
    assert fuori_forma.headers["cache-control"] == "no-store"


def test_cursore_inventato_da_409(client, sessione):
    risposta = client.get("/edunews24/notizie", params={"cursore": "inventato"}, headers=sessione)
    assert risposta.status_code == 409
    assert risposta.json() == {"detail": "L'elenco di EduNews24 è cambiato: ricarica dalla prima pagina."}
    assert risposta.headers["cache-control"] == "no-store"
    # Un cursore emesso per un'altra sezione non vale qui.
    cursore = client.get("/edunews24/notizie", headers=sessione).json()["meta"]["cursore_successivo"]
    altra = client.get("/edunews24/interpelli", params={"cursore": cursore}, headers=sessione)
    assert altra.status_code == 409


def test_funzione_disattivata(client, sessione, monkeypatch):
    spento = ServizioEduNews24.da_impostazioni(Impostazioni(_env_file=None, edunews24_backend="disabilitato"))
    monkeypatch.setattr("src.edunews24.servizio._servizio", spento)
    for rotta in ROTTE:
        risposta = client.get(rotta, headers=sessione)
        assert risposta.status_code == 200, rotta
        assert risposta.json() == {"attiva": False, "elementi": [], "meta": None}
        assert risposta.headers["cache-control"] == "no-store"
    # Anche con parametri che altrimenti sarebbero un errore della richiesta.
    risposta = client.get("/edunews24/interpelli", params={"area": "nazionale", "cursore": "x"}, headers=sessione)
    assert risposta.status_code == 200 and risposta.json()["attiva"] is False


def test_503_a_monte_con_retry_after(client, sessione, monkeypatch):
    _servizio_http(monkeypatch, lambda _: risposta_http(503, b"", retry_after="30"))
    risposta = client.get("/edunews24/notizie", headers=sessione)
    assert risposta.status_code == 503
    assert risposta.headers["retry-after"] == "30"
    assert risposta.headers["cache-control"] == "no-store"
    assert risposta.json() == {"detail": "EduNews24 non è raggiungibile in questo momento. Riprova più tardi."}


def test_un_429_a_monte_non_arriva_mai_come_429(client, sessione, monkeypatch):
    _servizio_http(monkeypatch, lambda _: risposta_http(429, b"<html>troppe</html>", content_type="text/html"))
    risposta = client.get("/edunews24/interpelli", headers=sessione)
    assert risposta.status_code == 503
    assert risposta.headers["retry-after"] == "30"


def test_il_dettaglio_di_un_400_a_monte_non_si_inoltra(client, sessione, monkeypatch):
    corpo = json.dumps(problema("unknown-parameter", ["pippo"])).encode()
    _servizio_http(monkeypatch, lambda _: risposta_http(400, corpo, content_type="application/problem+json"))
    risposta = client.get("/edunews24/selezione-personale", headers=sessione)
    assert risposta.status_code == 503
    assert "Dettaglio a monte" not in risposta.text and "pippo" not in risposta.text


def test_il_backend_http_normalizza_la_risposta(client, sessione, monkeypatch):
    chiamate = []

    def gestore(request):
        chiamate.append(str(request.url))
        dati = {"data": [{"type": "interpello", "id": 5, "url": "https://edunews24.invalid/interpelli/voce-5",
                          "title": "Interpello inventato", "summary": None,
                          "published_at": "2026-09-27T00:00:00+02:00", "regions": [], "national": False,
                          "details": {"competition_class": "A022"}}],
                "meta": {}, "links": {"next": None}}
        return risposta_http(200, json.dumps(dati).encode(), content_type="application/json",
                             cache_control="public, s-maxage=300")

    _servizio_http(monkeypatch, gestore)
    risposta = client.get("/edunews24/interpelli", params={"area": "lazio"}, headers=sessione)
    assert risposta.status_code == 200, risposta.text
    assert [v["id"] for v in risposta.json()["elementi"]] == [5]
    assert risposta.json()["elementi"][0]["classe_concorso"] == "A022"
    assert chiamate == [f"{URL_BASE}/interpelli?region=lazio"]


def test_senza_sessione_401(client):
    for rotta in ROTTE:
        assert client.get(rotta).status_code == 401
