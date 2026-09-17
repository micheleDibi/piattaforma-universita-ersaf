"""Formattazione dei dati per i modelli: segnaposto del gestionale, date, importi."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest

from src.documenti import dati as formato  # "testo" importato da solo sembrerebbe un test a pytest
from src.documenti.modelli import normalizza


@pytest.mark.parametrize(("valore", "atteso"), [
    (None, ""),
    ("  Maria   Della  Valle ", "Maria Della Valle"),
    (date(2026, 9, 17), "17/09/2026"),
    (datetime(2026, 9, 17, 10, 30), "17/09/2026"),
    (date(1999, 12, 31), ""),  # segnaposto del gestionale per "data mancante"
    (Decimal("1250.5"), "1.250,50"),
    (0, "0"),
    ("/", ""),  # segnaposto del gestionale per "testo mancante"
    (" - ", ""),
    ("s.n.", "s.n."),
])
def test_testo_per_il_modulo(valore, atteso):
    assert formato.testo(valore) == atteso


@pytest.mark.parametrize(("valore", "atteso"), [
    (Decimal("0"), "0,00"),
    (Decimal("999.999"), "1.000,00"),
    (Decimal("1234567.8"), "1.234.567,80"),
    (Decimal("-45"), "-45,00"),
    (150, "150,00"),
    (None, ""),
])
def test_importi_in_formato_italiano(valore, atteso):
    assert formato.importo(valore) == atteso


@pytest.mark.parametrize(("a", "b"), [
    ("Carta d'Identità", "CartaD'Identità"),
    ("Laurea (Laurea 1° Livello)", "Laurea(Laurea1°Livello)"),
    ("CICLO UNICO", "ciclo-unico"),
    ("Università di Prova", "UNIVERSITA DI PROVA"),
])
def test_normalizzazione_delle_descrizioni(a, b):
    assert normalizza(a) == normalizza(b) != ""
