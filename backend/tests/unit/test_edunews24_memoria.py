"""Backend `memoria`: dati inventati, deterministici, nella forma dell'API."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlsplit

import pytest

from src.edunews24.client import ErroreEduNews24
from src.edunews24.memoria import FonteMemoria, dati_inventati
from src.edunews24.normalizza import ContestoValidazione, normalizza_notizie, normalizza_opportunita
from src.edunews24.url import estrai_cursore
from tests.support.edunews24 import HOST_MEDIA, HOST_SITO, PARETE_FISSA, OrologioFinto

OGGI = datetime.fromtimestamp(PARETE_FISSA, tz=timezone.utc).date()
CONTESTO = ContestoValidazione(host_sito=HOST_SITO, host_media=frozenset({HOST_MEDIA}))


@pytest.fixture
def fonte():
    return FonteMemoria(HOST_SITO, OrologioFinto())


def _pagine(fonte, percorso, parametri=()):
    """Tutte le pagine di un elenco, seguendo i cursori."""
    pagine, cursore = [], None
    while True:
        completi = list(parametri) + ([("cursor", cursore)] if cursore else [])
        corpo = fonte.leggi(percorso, completi).corpo
        pagine.append(corpo["data"])
        cursore = estrai_cursore(corpo["links"]["next"])
        if corpo["links"]["next"] is None:
            return pagine
        assert cursore is not None


def test_deterministico_con_l_orologio_fissato():
    assert dati_inventati(PARETE_FISSA, HOST_SITO) == dati_inventati(PARETE_FISSA, HOST_SITO)
    # Le date sono arrotondate all'ora: dentro la stessa ora i dati non cambiano.
    assert dati_inventati(PARETE_FISSA, HOST_SITO) == dati_inventati(PARETE_FISSA + 1800, HOST_SITO)


def test_risposta_nella_forma_dell_api(fonte):
    risposta = fonte.leggi("/articles", [])
    assert risposta.stato == 200 and risposta.etag is None and risposta.stantia_a_monte is False
    assert "s-maxage=300" in risposta.cache_control
    assert set(risposta.corpo) == {"data", "meta", "links"}
    assert all("_video_a_monte" not in voce for voce in risposta.corpo["data"])
    assert "s-maxage=3600" in fonte.leggi("/categories", []).cache_control


def test_trenta_notizie_in_venti_piu_dieci(fonte):
    pagine = _pagine(fonte, "/articles")
    assert [len(p) for p in pagine] == [20, 10]
    ids = [v["id"] for p in pagine for v in p]
    assert len(set(ids)) == 30


def test_il_cursore_di_altri_filtri_si_rifiuta(fonte):
    prossimo = fonte.leggi("/articles", []).corpo["links"]["next"]
    assert urlsplit(prossimo).hostname == HOST_SITO and prossimo.startswith(f"https://{HOST_SITO}/api/v1/articles?")
    cursore = estrai_cursore(prossimo)
    with pytest.raises(ErroreEduNews24) as errore:
        fonte.leggi("/articles", [("has_video", "true"), ("cursor", cursore)])
    assert errore.value.motivo == "cursore-rifiutato"
    with pytest.raises(ErroreEduNews24):
        fonte.leggi("/interpelli", [("cursor", cursore)])
    with pytest.raises(ErroreEduNews24):
        fonte.leggi("/articles", [("cursor", "inventato")])


def test_filtri(fonte):
    scuola = [v for p in _pagine(fonte, "/articles", [("category", "scuola")]) for v in p]
    assert scuola and all(v["category"]["slug"] == "scuola" for v in scuola)
    con_video = fonte.leggi("/articles", [("has_video", "true")]).corpo["data"]
    assert con_video and len(con_video) < 20
    # Il filtro a monte guarda il file: esce anche una voce con video null.
    assert any(v["video"] is None for v in con_video)
    lazio = fonte.leggi("/interpelli", [("region", "lazio")]).corpo["data"]
    assert lazio and all(any(r["slug"] == "lazio" for r in v["regions"]) for v in lazio)
    nazionali = fonte.leggi("/selezione-personale", [("national", "true")]).corpo["data"]
    assert nazionali and all(v["national"] for v in nazionali)
    assert any(v["regions"] for v in nazionali)


def test_stati_vuoti(fonte):
    for percorso, parametri in (("/articles", [("category", "rubriche")]), ("/interpelli", [("region", "molise")]),
                                ("/selezione-personale", [("region", "molise")])):
        corpo = fonte.leggi(percorso, parametri).corpo
        assert corpo["data"] == [] and corpo["links"]["next"] is None


def test_categoria_sconosciuta_e_parametri_non_ammessi(fonte):
    with pytest.raises(ErroreEduNews24) as errore:
        fonte.leggi("/articles", [("category", "inesistente")])
    assert errore.value.motivo == "categoria-sconosciuta"
    for percorso, parametri in (("/interpelli", [("national", "true")]), ("/articles", [("limit", "5")]),
                                ("/categories", [("x", "1")]), ("/bandi", []),
                                ("/articles", [("category", "scuola"), ("category", "concorsi")])):
        with pytest.raises(ErroreEduNews24) as errore:
            fonte.leggi(percorso, parametri)
        assert errore.value.motivo == "richiesta-rifiutata"


def test_varianti_di_immagini_e_video():
    notizie = dati_inventati(PARETE_FISSA, HOST_SITO)["articles"]
    immagini = [v["image_url"] for v in notizie]
    assert immagini.count(None) == 2
    assert any(i and i.endswith("edunews24_immagine_da_sostituire.png") for i in immagini)
    assert any(i and i.startswith("https://terzi.example.org/") for i in immagini)
    assert any(i and i.startswith("http://") for i in immagini)
    assert sum(1 for v in notizie if v["thumbnail_url"]) == 1
    video = [v["video"] for v in notizie if v["video"]]
    assert {v["mime_type"] for v in video} == {"video/mp4", "video/webm", "video/quicktime"}
    assert any(v["duration_seconds"] is None for v in video)
    assert any(v["url"].startswith("http://") for v in video)
    assert any(v["video"] is None and v["_video_a_monte"] for v in notizie)
    titoli = [len(v["title"]) for v in notizie]
    assert sum(1 for n in titoli if n > 200) >= 3 and any(n > 300 for n in titoli)
    assert any(v["title_summary"] for v in notizie) and any(v["title_summary"] is None for v in notizie)


def test_campi_arricchiti_con_e_senza_valore():
    dati = dati_inventati(PARETE_FISSA, HOST_SITO)
    classi = [v["details"]["competition_class"] for v in dati["interpelli"]]
    assert None in classi and any(classi)
    assert any(not v["regions"] for v in dati["interpelli"])
    figure = [v["details"]["position"] for v in dati["selezione-personale"]]
    posti = [v["details"]["positions_count"] for v in dati["selezione-personale"]]
    assert None in figure and any(figure) and None in posti and any(posti)
    assert any(v["summary"] is None for v in dati["selezione-personale"])


def test_scadenze_della_selezione():
    selezione = dati_inventati(PARETE_FISSA, HOST_SITO)["selezione-personale"]
    coppie = {(None if v["deadline_on"] is None else (date.fromisoformat(v["deadline_on"]) - OGGI).days,
               v["status"]) for v in selezione}
    for attesa in ((0, "open"), (1, "open"), (3, "open"), (-1, "open"), (-5, "closed"), (None, None),
                   (None, "open")):
        assert attesa in coppie
    assert any(d is not None and d >= 30 and s == "open" for d, s in coppie)


def test_nessun_host_reale():
    testo = json.dumps(dati_inventati(PARETE_FISSA, HOST_SITO))
    host = set(re.findall(r"https?://([^/\"]+)", testo))
    assert host == {HOST_SITO, HOST_MEDIA, "terzi.example.org"}


def test_date_relative_all_orologio(fonte):
    orologio = OrologioFinto()
    prima = FonteMemoria(HOST_SITO, orologio).leggi("/articles", []).corpo["data"][0]["published_at"]
    orologio.avanza(timedelta(days=1).total_seconds())
    dopo = FonteMemoria(HOST_SITO, orologio).leggi("/articles", []).corpo["data"][0]["published_at"]
    assert prima != dopo and prima.endswith("Z")


def test_la_normalizzazione_accetta_i_dati_inventati(fonte):
    notizie = normalizza_notizie(fonte.leggi("/articles", []).corpo, CONTESTO, solo_video=False)
    assert len(notizie.elementi) == 20 and notizie.scartate == 0
    assert any(n.immagine is None for n in notizie.elementi)
    assert any(n.video is not None for n in notizie.elementi)
    for percorso, tipo in (("/interpelli", "interpello"), ("/selezione-personale", "selezione-personale")):
        pagina = normalizza_opportunita(fonte.leggi(percorso, []).corpo, CONTESTO, tipo=tipo)
        assert len(pagina.elementi) == 20 and pagina.scartate == 0
