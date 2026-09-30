"""Dalla risposta di EduNews24 al contratto: validazione e scarto voce per voce."""

from __future__ import annotations

from typing import get_args

import pytest

import src.edunews24.normalizza as modulo_normalizza
from src.edunews24.client import ErroreEduNews24
from src.edunews24.costanti import REGIONI
from src.edunews24.normalizza import (
    ContestoValidazione,
    normalizza_categorie,
    normalizza_notizie,
    normalizza_opportunita,
)
from src.edunews24.normalizza import testo_pulito as pulisci  # "test*" verrebbe raccolto da pytest
from src.edunews24.schemi import Area
from tests.support.edunews24 import (
    HOST_MEDIA,
    HOST_SITO,
    articolo,
    categorie,
    elenco,
    link_next,
    opportunita,
    video,
)

CONTESTO = ContestoValidazione(host_sito=HOST_SITO, host_media=frozenset({HOST_MEDIA}))
SEGNAPOSTO = "/edunews24_immagine_da_sostituire.png"


def _notizie(*voci, solo_video=False, next=None):
    return normalizza_notizie(elenco(list(voci), next), CONTESTO, solo_video=solo_video)


def _una(voce, **argomenti):
    pagina = _notizie(voce, **argomenti)
    assert len(pagina.elementi) == 1, pagina
    return pagina.elementi[0]


def _opportunita(*voci, tipo="selezione-personale"):
    return normalizza_opportunita(elenco(list(voci)), CONTESTO, tipo=tipo)


@pytest.mark.parametrize("corpo", [
    None, [], {"data": {}, "links": {}}, {"data": [], "links": None}, {"data": []}, {"links": {}},
])
def test_forma_del_corpo_non_valida_e_un_guasto(corpo):
    with pytest.raises(ErroreEduNews24) as errore:
        normalizza_notizie(corpo, CONTESTO, solo_video=False)
    assert errore.value.motivo == "risposta-non-valida"


def test_notizia_completa():
    notizia = _una(articolo(7, video=video(), title_summary="Titolo breve"))
    assert notizia.model_dump() == {
        "tipo": "notizia", "id": 7, "titolo": "Titolo inventato", "titolo_breve": "Titolo breve",
        "sintesi": "Sintesi inventata", "url": f"https://{HOST_SITO}/scuola/notizia-7",
        "pubblicato_il": "2026-09-28T10:00:00+02:00", "categoria": {"slug": "scuola", "nome": "Scuola"},
        "immagine": f"https://{HOST_MEDIA}/a.jpg",
        "video": {"url": f"https://{HOST_MEDIA}/v.mp4", "tipo_mime": "video/mp4",
                  "copertina": f"https://{HOST_MEDIA}/c.jpg", "durata_secondi": 125},
        "ha_video": True,
    }


def test_titolo_breve_e_sintesi_facoltativi():
    notizia = _una(articolo(1, excerpt=None, summary="Riassunto inventato"))
    assert notizia.titolo_breve is None
    assert notizia.sintesi == "Riassunto inventato"
    assert _una(articolo(1, excerpt=None, summary=None)).sintesi is None


def test_una_voce_che_solleva_si_scarta_da_sola():
    class Ostile(dict):
        def get(self, *argomenti):
            raise RuntimeError("voce ostile")

    pagina = _notizie(articolo(1), Ostile(type="article"), "non un oggetto", articolo(2))
    assert [n.id for n in pagina.elementi] == [1, 2]
    assert (pagina.totali, pagina.scartate) == (4, 2)


@pytest.mark.parametrize("campo", ["title", "excerpt", "title_summary", "category"])
def test_un_surrogato_isolato_non_guasta_la_pagina(campo):
    voce = articolo(2)
    if campo == "category":
        voce["category"] = {**voce["category"], "name": "Scuola \ud83d"}
    else:
        voce[campo] = "Testo con emoji tagliata \ud83d"
    pagina = _notizie(articolo(1), voce)
    assert [n.id for n in pagina.elementi] == [1, 2]
    for notizia in pagina.elementi:
        notizia.model_dump_json()


def test_una_voce_che_non_si_serializza_si_scarta_da_sola(monkeypatch):
    originale = modulo_normalizza._byte

    def byte(voce):
        if voce.id == 2:
            raise ValueError("non serializzabile")
        return originale(voce)

    monkeypatch.setattr(modulo_normalizza, "_byte", byte)
    pagina = _notizie(articolo(1), articolo(2), articolo(3))
    assert [n.id for n in pagina.elementi] == [1, 3] and pagina.scartate == 1
    pagina = _opportunita(opportunita(1), opportunita(2))
    assert [v.id for v in pagina.elementi] == [1] and pagina.scartate == 1


def test_deduplica_per_tipo_e_id():
    pagina = _notizie(articolo(1), articolo(1, titolo="Doppione"), articolo(2))
    assert [(n.id, n.titolo) for n in pagina.elementi] == [(1, "Titolo inventato"), (2, "Titolo inventato")]


@pytest.mark.parametrize("modifica", [
    {"type": "bando"},
    {"type": None},
    {"id": True},
    {"id": 0},
    {"id": 2**53},
    {"id": "7"},
    {"url": "http://edunews24.invalid/scuola/notizia-1"},
    {"url": "https://example.org/scuola/notizia-1"},
    {"url": None},
    {"title": "   "},
    {"title": None},
    {"published_at": "2026-09-28"},
    {"published_at": "2026-02-30T10:00:00Z"},
    {"published_at": "2026-09-28T10:00:00Z\n"},
    {"published_at": "2026-09-28T10:00:00"},
    {"category": {"slug": "Scuola", "name": "Scuola"}},
    {"category": {"slug": "scuola", "name": ""}},
    {"category": None},
])
def test_voci_scartate(modifica):
    voce = articolo(1)
    voce.update(modifica)
    pagina = _notizie(voce)
    assert pagina.elementi == () and pagina.scartate == 1


def test_istanti_ammessi():
    for istante in ("2026-09-28T10:00:00Z", "2026-09-28T10:00:00.123456+02:00", "2026-09-28T10:00:00-01:30"):
        assert _una(articolo(1, published_at=istante)).pubblicato_il == istante


def test_pulisci():
    assert pulisci("  a\tb\n\nc\x00d\x85e\u2028f\u2029g  ", 100) == "a b c d e f g"
    assert pulisci("\x07\x1b", 100) is None
    assert pulisci("", 100) is None
    assert pulisci(None, 100) is None
    assert pulisci(12, 100) is None
    assert pulisci("uno due tre quattro", 12) == "uno due tre…"
    assert pulisci("uno due trequattro", 12) == "uno due…"
    assert pulisci("unaparolalunghissima", 10) == "unaparola…"
    assert len(pulisci("parola " * 100, 300)) <= 300


def test_pulisci_toglie_bidi_e_surrogati_isolati():
    # Un RLO senza chiusura capovolgerebbe il testo che segue nella riga.
    assert pulisci("a\u202eb\u202ac\u2066d\u2069e\u200ef\u200fg", 100) == "abcdefg"
    # Mezza emoji: JSON valido, ma non serializzabile in UTF-8.
    assert pulisci("Titolo \ud83d", 100) == "Titolo"
    assert pulisci("\ud83d", 100) is None
    # Le emoji intere e le sequenze con ZWJ restano.
    assert pulisci("Famiglia \U0001F468\u200d\U0001F469", 100) == "Famiglia \U0001F468\u200d\U0001F469"


def test_titoli_lunghi_troncati_a_300():
    titolo = pulisci(" ".join(["parola"] * 80), 300)
    assert _una(articolo(1, titolo=" ".join(["parola"] * 80))).titolo == titolo
    assert titolo.endswith("…") and len(titolo) <= 300


def test_immagini():
    assert _una(articolo(1, immagine=None)).immagine is None
    assert _una(articolo(1, immagine=f"https://{HOST_SITO}{SEGNAPOSTO}")).immagine is None
    assert _una(articolo(1, immagine=f"https://{HOST_MEDIA}{SEGNAPOSTO}")).immagine is None
    assert _una(articolo(1, immagine="https://terzi.example.org/a.jpg")).immagine is None
    assert _una(articolo(1, immagine=f"http://{HOST_MEDIA}/a.jpg")).immagine is None
    # Il thumbnail_url di primo livello non e' una miniatura: si ignora.
    notizia = _una(articolo(1, immagine=None, thumbnail_url=f"https://{HOST_MEDIA}/m.jpg"))
    assert notizia.immagine is None


@pytest.mark.parametrize("grezzo", [
    video(mime="video/quicktime"),
    video(mime=None),
    video(url=f"http://{HOST_MEDIA}/v.mp4"),
    video(url="https://terzi.example.org/v.mp4"),
    video(url=f"https://{HOST_SITO}/v.mp4"),
])
def test_video_non_riproducibile_tiene_il_distintivo(grezzo):
    notizia = _una(articolo(1, video=grezzo))
    assert notizia.video is None and notizia.ha_video is True


def test_webm_e_ammesso():
    assert _una(articolo(1, video=video(f"https://{HOST_MEDIA}/v.webm", mime="video/webm"))).video.tipo_mime == \
        "video/webm"


def test_copertina_del_video():
    segnaposto = _una(articolo(1, video=video(copertina=f"https://{HOST_MEDIA}{SEGNAPOSTO}")))
    assert segnaposto.video.copertina == f"https://{HOST_MEDIA}/a.jpg"
    assente = _una(articolo(1, immagine=None, video=video(copertina=None)))
    assert assente.video.copertina is None
    terzi = _una(articolo(1, video=video(copertina="https://terzi.example.org/c.jpg")))
    assert terzi.video.copertina == f"https://{HOST_MEDIA}/a.jpg"


@pytest.mark.parametrize(("durata", "attesa"), [(125, 125), (1, 1), (0, None), (-3, None), (True, None),
                                               (12.5, None), ("60", None), (None, None)])
def test_durata(durata, attesa):
    assert _una(articolo(1, video=video(durata=durata))).video.durata_secondi == attesa


def test_notizie_senza_video_ne_ha_video():
    notizia = _una(articolo(1))
    assert notizia.video is None and notizia.ha_video is False


def test_solo_video_toglie_le_voci_senza_video_senza_contarle():
    pagina = _notizie(articolo(1, video=video()), articolo(2), articolo(3, video=video(mime=None)),
                      solo_video=True)
    assert [n.id for n in pagina.elementi] == [1, 3]
    assert pagina.scartate == 0


def test_cursore_successivo_e_fuori_forma():
    assert _notizie(articolo(1), next=link_next(cursore="abc")).cursore_successivo == "abc"
    pagina = _notizie(articolo(1), next=link_next(cursore="a.b"))
    assert pagina.cursore_successivo is None and pagina.cursore_fuori_forma is True
    pagina = _notizie(articolo(1))
    assert pagina.cursore_successivo is None and pagina.cursore_fuori_forma is False
    vuota = _notizie(next=link_next(cursore="abc"))
    assert vuota.elementi == () and vuota.cursore_successivo == "abc"


def test_al_massimo_cento_voci():
    pagina = _notizie(*[articolo(n) for n in range(1, 131)])
    assert len(pagina.elementi) == 100 and pagina.totali == 100


def test_selezione_completa():
    (voce,) = _opportunita(opportunita(9)).elementi
    assert voce.model_dump() == {
        "tipo": "selezione-personale", "id": 9, "titolo": "Annuncio inventato",
        "sintesi": "Descrizione inventata", "url": f"https://{HOST_SITO}/selezione-personale/voce-9",
        "ente": "Ente di prova", "sede": "Città di prova",
        "regioni": [{"slug": "lombardia", "nome": "Lombardia"}], "nazionale": False,
        "pubblicato_il": "2026-09-27T10:00:00+02:00", "scadenza": "2026-10-05", "stato": "aperto",
        "classe_concorso": None, "figura": "Figura di prova", "posti": 3,
    }


def test_interpello_completo():
    (voce,) = _opportunita(opportunita(4, tipo="interpello"), tipo="interpello").elementi
    assert voce.model_dump() == {
        "tipo": "interpello", "id": 4, "titolo": "Annuncio inventato", "sintesi": "Descrizione inventata",
        "url": f"https://{HOST_SITO}/interpelli/voce-4", "ente": None, "sede": "Città di prova",
        "regioni": [{"slug": "lombardia", "nome": "Lombardia"}], "nazionale": False,
        "pubblicato_il": "2026-09-27T10:00:00+02:00", "scadenza": None, "stato": None,
        "classe_concorso": "A022", "figura": None, "posti": None,
    }


def test_interpello_senza_ente_anche_con_il_titolo_ufficiale():
    # official_title e' il nome dell'avviso, non la scuola: non si mostra.
    grezzo = opportunita(4, tipo="interpello", dettagli={"official_title": "Avviso di interpello di prova",
                                                         "organizations": ["Ente di prova"]})
    (voce,) = _opportunita(grezzo, tipo="interpello").elementi
    assert voce.ente is None


def test_interpello_ignora_scadenza_stato_e_campi_della_selezione():
    grezzo = opportunita(4, tipo="interpello", deadline_on="2026-10-05", status="open",
                         dettagli={"official_title": None, "competition_class": None, "province": "Provincia",
                                   "city": None, "position": "Figura", "positions_count": 3})
    (voce,) = _opportunita(grezzo, tipo="interpello").elementi
    assert (voce.scadenza, voce.stato, voce.figura, voce.posti) == (None, None, None, None)
    assert voce.ente is None and voce.sede == "Provincia" and voce.classe_concorso is None


def test_selezione_ignora_la_classe_di_concorso():
    grezzo = opportunita(1, dettagli={"competition_class": "A022", "organizations": [], "locations": []})
    (voce,) = _opportunita(grezzo).elementi
    assert voce.classe_concorso is None and voce.ente is None and voce.sede is None
    assert voce.figura is None and voce.posti is None


def test_classe_di_concorso_al_massimo_16_caratteri():
    grezzo = opportunita(1, tipo="interpello",
                         dettagli={"competition_class": "Classe di prova lunghissima"})
    (voce,) = _opportunita(grezzo, tipo="interpello").elementi
    assert voce.classe_concorso == "Classe di prova…"


@pytest.mark.parametrize(("posti", "atteso"), [(3, 3), (1, 1), (0, None), (True, None), ("3", None), (2.0, None)])
def test_posti(posti, atteso):
    (voce,) = _opportunita(opportunita(1, dettagli={"positions_count": posti})).elementi
    assert voce.posti == atteso


def test_regioni_riconosciute_ordinate_e_senza_doppioni():
    regioni = [{"slug": "veneto", "name": "X"}, {"slug": "abruzzo", "name": "Y"}, {"slug": "veneto"},
               {"slug": "atlantide"}, "lazio", {"name": "Lazio"}, None]
    (voce,) = _opportunita(opportunita(1, regions=regioni)).elementi
    assert [r.model_dump() for r in voce.regioni] == [{"slug": "abruzzo", "nome": "Abruzzo"},
                                                      {"slug": "veneto", "nome": "Veneto"}]
    (voce,) = _opportunita(opportunita(1, regions=None)).elementi
    assert voce.regioni == []


def test_nazionale_solo_se_vero():
    (voce,) = _opportunita(opportunita(1, national=True)).elementi
    assert voce.nazionale is True
    (voce,) = _opportunita(opportunita(1, national="true")).elementi
    assert voce.nazionale is False


def test_la_sede_non_e_il_nome_di_una_regione():
    dettagli = {"organizations": ["", "  ", "Ente di prova"],
                "locations": ["Emilia Romagna", "Valle d'Aosta", "Trentino-Alto Adige/Sudtirol", "Città di prova"]}
    (voce,) = _opportunita(opportunita(1, dettagli=dettagli)).elementi
    assert voce.ente == "Ente di prova" and voce.sede == "Città di prova"


@pytest.mark.parametrize(("stato", "atteso"), [("open", "aperto"), ("closed", "chiuso"), (None, None),
                                               ("upcoming", "altro"), ("revoked", "altro"), (3, None)])
def test_stato(stato, atteso):
    (voce,) = _opportunita(opportunita(1, status=stato)).elementi
    assert voce.stato == atteso


@pytest.mark.parametrize(("scadenza", "attesa"), [("2026-10-05", "2026-10-05"), ("2026-02-30", None),
                                                  ("05/10/2026", None), ("2026-10-05T00:00:00Z", None),
                                                  (None, None), (20261005, None)])
def test_scadenza(scadenza, attesa):
    (voce,) = _opportunita(opportunita(1, deadline_on=scadenza)).elementi
    assert voce.scadenza == attesa


def test_opportunita_di_tipo_diverso_si_scartano():
    pagina = _opportunita(opportunita(1, tipo="interpello"), opportunita(2), opportunita(3, type="bando"))
    assert [v.id for v in pagina.elementi] == [2]
    assert pagina.scartate == 2


def test_categorie():
    pagina = normalizza_categorie(categorie("scuola", "universita", "Non_Valida", "scuola"))
    assert [c.model_dump() for c in pagina.elementi] == [{"slug": "scuola", "nome": "Scuola"},
                                                         {"slug": "universita", "nome": "Universita"}]
    assert pagina.cursore_successivo is None and pagina.scartate == 1
    # Un surrogato isolato nel nome non guasta l'elenco.
    corpo = categorie("scuola", "universita")
    corpo["data"][0]["name"] = "Scuola \ud83d"
    pagina = normalizza_categorie(corpo)
    assert [(c.slug, c.nome) for c in pagina.elementi] == [("scuola", "Scuola"), ("universita", "Universita")]
    with pytest.raises(ErroreEduNews24):
        normalizza_categorie({"data": None, "links": {}})


def test_byte_misura_le_voci():
    vuota = _notizie()
    assert vuota.byte == 64
    assert _notizie(articolo(1)).byte > 200


def test_area_allineata_alle_regioni():
    assert get_args(Area)[:2] == ("tutte", "nazionale")
    assert get_args(Area)[2:] == tuple(slug for slug, _ in REGIONI)
