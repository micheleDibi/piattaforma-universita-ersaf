from __future__ import annotations

import pytest

pytest.importorskip("yaml")

import mappa  # noqa: E402
from comune import RADICE, elenco_file  # noqa: E402

VALIDA = """
regole:
  - nome: Sicurezza
    percorsi:
      - "backend/src/auth/**"
      - "**/Dockerfile"
    documenti:
      - docs/tecnica/sicurezza.md
"""


def test_mappa_valida():
    [regola] = mappa.analizza(VALIDA)
    assert regola.toccati(["backend/src/auth/a.py", "frontend/Dockerfile", "x.py"]) == [
        "backend/src/auth/a.py", "frontend/Dockerfile"]


@pytest.mark.parametrize(("testo", "parola"), [
    ("regole:\n  - nome: X\n    percorsi: [*/Dockerfile]\n    documenti: [docs/a.md]\n", "YAML non valido"),
    ("altro: 1\n", "solo la chiave"),
    ("regole:\n  - nome: X\n    percorsi: []\n    documenti: [docs/a.md]\n", "lista non vuota"),
    ("regole:\n  - nome: X\n    percorsi: ['a/{b,c}']\n    documenti: [docs/a.md]\n", "graffe"),
    ("regole:\n  - nome: X\n    percorsi: ['a']\n    documenti: [README.md]\n", "sotto docs/"),
    ("regole:\n  - nome: X\n    percorsi: ['a']\n    documenti: [docs/tecnica/riferimenti/api.md]\n", "generato"),
    ("regole:\n  - nome: X\n    percorsi: ['a']\n", "esattamente"),
    ("regole:\n  - {nome: X, percorsi: ['a'], documenti: [docs/a.md]}\n"
     "  - {nome: X, percorsi: ['b'], documenti: [docs/a.md]}\n", "ripetuto"),
])
def test_mappa_non_valida(testo, parola):
    with pytest.raises(mappa.MappaNonValida) as info:
        mappa.analizza(testo)
    assert any(parola in e for e in info.value.errori), info.value.errori


def test_errori_rispetto_ai_file():
    [regola] = mappa.analizza(VALIDA)
    assert mappa.errori_rispetto_ai_file([regola], ["backend/src/auth/a.py", "docs/tecnica/sicurezza.md"]) == [
        "regola 'Sicurezza': il pattern **/Dockerfile non trova nessun file"]
    assert mappa.errori_rispetto_ai_file([regola], ["backend/Dockerfile", "backend/src/auth/a.py"]) == [
        "regola 'Sicurezza': il documento docs/tecnica/sicurezza.md non esiste"]


def test_la_mappa_del_repository_e_valida():
    regole = mappa.carica(RADICE)
    assert regole
    assert mappa.errori_rispetto_ai_file(regole, elenco_file(RADICE)) == []
