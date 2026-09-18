"""Forma dei workflow GitHub: controllo della documentazione solo sulle PR,
e nessun workflow che possa bloccare i commit del timbro su main."""

from __future__ import annotations

import pytest

yaml = pytest.importorskip("yaml")

from comune import RADICE  # noqa: E402

CARTELLA = RADICE / ".github" / "workflows"


def carica(percorso):
    dati = yaml.safe_load(percorso.read_text(encoding="utf-8"))
    # PyYAML legge la chiave `on` come True.
    return dati, dati.get("on", dati.get(True))


def test_nessun_workflow_su_push_a_main():
    for percorso in sorted(CARTELLA.glob("*.y*ml")):
        _, eventi = carica(percorso)
        nomi = set(eventi) if isinstance(eventi, dict) else set([eventi] if isinstance(eventi, str) else eventi)
        assert not nomi & {"push", "workflow_run", "merge_group"}, percorso.name


def test_workflow_della_documentazione():
    dati, eventi = carica(CARTELLA / "documentazione.yml")
    assert set(eventi) == {"pull_request"}
    assert eventi["pull_request"]["branches"] == ["main"]
    assert set(eventi["pull_request"]["types"]) == {"opened", "synchronize", "reopened", "labeled", "unlabeled"}
    assert dati["permissions"] == {"contents": "read"}
    passi = dati["jobs"]["documentazione"]["steps"]
    comandi = "\n".join(p.get("run", "") for p in passi)
    assert "-c scripts/documentazione/vincoli.txt" in comandi
    assert "genera.py --verifica" in comandi
    [controllo] = [p for p in passi if "controlla.py tutto" in p.get("run", "")]
    assert '--base "$BASE_SHA" --merge --etichette "$ETICHETTE"' in controllo["run"]
    assert "${{" not in controllo["run"]
    assert controllo["env"]["BASE_SHA"] == "${{ github.event.pull_request.base.sha }}"
    assert "labels" in controllo["env"]["ETICHETTE"]
    checkout = passi[0]
    assert checkout["with"]["fetch-depth"] == 0 and checkout["with"]["persist-credentials"] is False
    assert "secrets." not in (CARTELLA / "documentazione.yml").read_text(encoding="utf-8")
