"""Le regioni di EduNews24 del frontend devono coincidere con quelle del backend.

Sono duplicate di proposito: il frontend le usa per il filtro Area senza una
chiamata in piu', il backend per validare i parametri e i dati a monte. La
duplicazione e' sorvegliata qui, sul modello di test_policy_allineata.py: si
confrontano insieme e ordine delle coppie (slug, nome).
"""

from __future__ import annotations

import re

import pytest

from src.config import DIR_BACKEND
from src.edunews24.costanti import REGIONI

MODULO_JS = DIR_BACKEND.parent / "frontend" / "src" / "config" / "edunews24.js"
# Forma fissata nel file JS: una regione per riga, { slug: "...", nome: "..." }.
RIGA_REGIONE = re.compile(r'\{ slug: "([a-z-]+)", nome: "([^"]+)" \}')


@pytest.fixture(scope="module")
def regioni_js() -> list[tuple[str, str]]:
    assert MODULO_JS.exists(), f"atteso {MODULO_JS}"
    sorgente = MODULO_JS.read_text(encoding="utf-8")
    blocco = re.search(r"export const REGIONI_EDUNEWS24 = Object\.freeze\(\[(.*?)\]\);", sorgente, re.S)
    assert blocco, "REGIONI_EDUNEWS24 assente da config/edunews24.js"
    return RIGA_REGIONE.findall(blocco.group(1))


def test_venti_regioni_nella_forma_attesa(regioni_js):
    assert len(regioni_js) == 20
    assert len(REGIONI) == 20


def test_stesse_regioni(regioni_js):
    assert set(regioni_js) == set(REGIONI)


def test_stesso_ordine(regioni_js):
    assert tuple(regioni_js) == REGIONI
