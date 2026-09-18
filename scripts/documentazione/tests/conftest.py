"""Ambiente dei test degli strumenti: moduli importabili e git isolato.

Ogni processo git dei test legge una configurazione vuota più quella iniettata
qui, così firma dei commit, hook o ramo predefinito del PC non cambiano i
risultati.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CARTELLA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CARTELLA))

CONFIG_GIT = {
    "user.name": "Test",
    "user.email": "test@example.invalid",
    "commit.gpgsign": "false",
    "tag.gpgsign": "false",
    "init.defaultBranch": "main",
    "core.autocrlf": "false",
    "advice.detachedHead": "false",
}


@pytest.fixture(autouse=True)
def git_isolato(tmp_path_factory, monkeypatch):
    vuoto = tmp_path_factory.getbasetemp() / "gitconfig-vuoto"
    vuoto.touch()
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(vuoto))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_COUNT", str(len(CONFIG_GIT)))
    for indice, (chiave, valore) in enumerate(CONFIG_GIT.items()):
        monkeypatch.setenv(f"GIT_CONFIG_KEY_{indice}", chiave)
        monkeypatch.setenv(f"GIT_CONFIG_VALUE_{indice}", valore)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    for variabile in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        monkeypatch.delenv(variabile, raising=False)


class Repo:
    """Piccolo repository git di prova."""

    def __init__(self, percorso: Path):
        self.percorso = percorso

    def git(self, *argomenti: str, controlla: bool = True) -> str:
        esito = subprocess.run(["git", *argomenti], cwd=self.percorso, capture_output=True,
                               encoding="utf-8")
        if controlla and esito.returncode != 0:
            raise AssertionError(f"git {' '.join(argomenti)}: {esito.stderr}")
        return esito.stdout.strip()

    def scrivi(self, relativo: str, testo: str) -> Path:
        destinazione = self.percorso / relativo
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        destinazione.write_text(testo, encoding="utf-8", newline="\n")
        return destinazione

    def cancella(self, relativo: str) -> None:
        (self.percorso / relativo).unlink()

    def commit(self, messaggio: str = "modifica") -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", messaggio)
        return self.git("rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path) -> Repo:
    cartella = tmp_path / "repo"
    cartella.mkdir()
    r = Repo(cartella)
    r.git("init", "-q", "-b", "main")
    return r


FRAMMENTO_VALIDO = """---
pr: 7
---

## Novità e correzioni

- aggiunto: Negli elenchi compare lo stato di verifica dei contatti.

## Dettagli tecnici

- modificato: `GET /clienti/` restituisce un campo in più.
"""
