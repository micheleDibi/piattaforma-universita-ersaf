"""Cursori: estrazione da links.next e registro di quelli emessi."""

from __future__ import annotations

import pytest

from src.edunews24.cursori import RegistroCursori
from src.edunews24.url import estrai_cursore
from tests.support.edunews24 import URL_BASE


@pytest.mark.parametrize(("valore", "atteso"), [
    (f"{URL_BASE}/articles?category=scuola&cursor=eyJ2IjoxfQ", "eyJ2IjoxfQ"),
    (f"{URL_BASE}/articles?cursor=a_b-C9&limit=20", "a_b-C9"),
    (None, None),
    (f"{URL_BASE}/articles?category=scuola", None),
    (f"{URL_BASE}/articles?cursor=a&cursor=b", None),
    (f"{URL_BASE}/articles?cursor=", None),
    (f"{URL_BASE}/articles?cursor=a.b", None),
    (f"{URL_BASE}/articles?cursor=a%0A", None),
    (f"{URL_BASE}/articles?cursor=" + "a" * 301, None),
    (f"{URL_BASE}/articles?cursor=abc\n", None),
    (f"{URL_BASE}/articles?cursor=abc ", None),
    ("https://[edunews24.invalid/articles?cursor=abc", None),
    (123, None),
    (["cursor=abc"], None),
    ("https://edunews24.invalid/?" + "x=1&" * 600 + "cursor=abc", None),
])
def test_estrai_cursore(valore, atteso):
    assert estrai_cursore(valore) == atteso


def test_il_cursore_di_300_caratteri_e_ammesso():
    assert estrai_cursore(f"{URL_BASE}/articles?cursor=" + "a" * 300) == "a" * 300


def test_il_registro_lega_cursore_risorsa_e_filtri():
    registro = RegistroCursori()
    registro.registra("/articles", "category=scuola", "c1")
    assert registro.emesso("/articles", "category=scuola", "c1")
    assert not registro.emesso("/articles", "", "c1")
    assert not registro.emesso("/interpelli", "category=scuola", "c1")
    assert not registro.emesso("/articles", "category=scuola", "c2")
    assert registro.dimentica("/articles", "category=scuola", "c1") is None
    assert not registro.emesso("/articles", "category=scuola", "c1")
    assert registro.dimentica("/articles", "category=scuola", "c1") is None


def test_il_registro_ricorda_la_pagina_che_ha_emesso_il_cursore():
    registro = RegistroCursori()
    registro.registra("/articles", "", "c1", emittente="/articles")
    registro.registra("/articles", "", "c2", emittente="/articles?cursor=c1")
    assert registro.emesso("/articles", "", "c1")
    assert registro.dimentica("/articles", "", "c2") == "/articles?cursor=c1"
    assert registro.dimentica("/articles", "", "c1") == "/articles"
    assert len(registro) == 0


def test_il_registro_e_una_lru_limitata():
    registro = RegistroCursori()
    for n in range(2049):
        registro.registra("/articles", "", f"c{n}")
    assert len(registro) == 2048
    assert not registro.emesso("/articles", "", "c0")
    assert registro.emesso("/articles", "", "c1")
    # Un cursore appena usato non e' il primo a uscire.
    registro.registra("/articles", "", "nuovo")
    assert registro.emesso("/articles", "", "c1")
    assert not registro.emesso("/articles", "", "c2")
    registro.svuota()
    assert len(registro) == 0
