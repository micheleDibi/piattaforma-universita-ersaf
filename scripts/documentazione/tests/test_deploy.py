"""Parte server del timbro e vincoli sugli script di deploy.

Gli script remoti vengono concatenati ed eseguiti come fa deploy.ps1
(Get-RemoteBundle), con la base del server in una cartella temporanea.
"""

from __future__ import annotations

import re
import shutil
import subprocess

import pytest

from comune import RADICE

REMOTI = sorted((RADICE / "deploy" / "remote").glob("*.sh"))
ID = "20260917-184000-abcdef1"
SHA = "abcdef1" + "0" * 33

bash = shutil.which("bash")
richiede_bash = pytest.mark.skipif(bash is None, reason="bash non disponibile")


def bundle() -> str:
    parti = [p.read_bytes().decode("ascii").replace("\r\n", "\n") for p in REMOTI]
    return "\n".join(parti) + "\n# fine bundle"


def esegui_bundle(base, *argomenti):
    ambiente = {"PATH": "/usr/bin:/bin:/usr/local/bin", "ERSAF_DEPLOY_BASE": str(base), "HOME": str(base)}
    return subprocess.run([bash, "-s", "--", *argomenti], input=bundle(), capture_output=True,
                          encoding="utf-8", env=ambiente, timeout=60)


@pytest.fixture
def server(tmp_path):
    base = tmp_path / "server"
    (base / "shared").mkdir(parents=True)
    (base / "shared" / "compose.env").write_text("RELEASE_TAG=none\n", encoding="utf-8")
    (base / "shared" / "ultima_versione").write_text("11\n", encoding="utf-8")
    rilascio = base / "releases" / ID
    rilascio.mkdir(parents=True)
    (rilascio / "RELEASE_INFO").write_text(
        f"release={ID}\ngit_sha={SHA}\nalbero_modificato=false\nversione=12\n"
        "aggiornata=2026-09-17T18:40:00+02:00\ndata=2026-09-17T16:40:05+00:00\noperatore=root@server\n",
        encoding="utf-8")
    return base


def test_script_ascii_senza_bom():
    """Windows PowerShell 5.1 legge i file senza BOM come cp1252: un carattere
    non ASCII in una stringa può rompere l'analisi dell'intero script."""
    for percorso in [RADICE / "scripts" / "deploy.ps1", RADICE / "scripts" / "verify-local.ps1", *REMOTI]:
        dati = percorso.read_bytes()
        assert not dati.startswith(b"\xef\xbb\xbf"), percorso
        assert all(b < 128 for b in dati), percorso


@richiede_bash
def test_bundle_sintatticamente_valido(tmp_path):
    esito = subprocess.run([bash, "-n"], input=bundle(), capture_output=True, encoding="utf-8")
    assert esito.returncode == 0, esito.stderr


@richiede_bash
def test_release_info(server):
    esito = esegui_bundle(server, "release-info", ID)
    assert esito.returncode == 0, esito.stderr
    righe = esito.stdout.strip().split("\n")
    assert righe == [f"release={ID}", f"git_sha={SHA}", "albero_modificato=false", "versione=12",
                     "aggiornata=2026-09-17T18:40:00+02:00", "ultima_versione=11"]
    assert "operatore" not in esito.stdout and "data=" not in esito.stdout


@richiede_bash
@pytest.mark.parametrize("argomenti", [(), ("../../etc",), ("20260917-184000-ABCDEF1",),
                                       ("20260917-184000-abcdef2",)])
def test_release_info_rifiuta_id_non_validi_o_assenti(server, argomenti):
    esito = esegui_bundle(server, "release-info", *argomenti)
    assert esito.returncode != 0
    assert esito.stdout == ""


@richiede_bash
def test_release_info_senza_installazione(tmp_path):
    esito = esegui_bundle(tmp_path / "vuoto", "release-info", ID)
    assert esito.returncode != 0
    assert "non installato" in esito.stderr


@richiede_bash
def test_status_invariato(server):
    esito = esegui_bundle(server, "status")
    assert esito.returncode == 0, esito.stderr
    assert "release attiva: none" in esito.stdout


def _funzione(nome: str) -> str:
    testo = (RADICE / "scripts" / "deploy.ps1").read_bytes().decode("ascii").replace("\r\n", "\n")
    corrispondenza = re.search(rf"^function {nome} \{{\n(.*?)^\}}\n", testo, re.MULTILINE | re.DOTALL)
    assert corrispondenza, nome
    return corrispondenza.group(1)


# Funzioni di deploy.ps1 che terminano il processo: chiamarle dal timbro
# riporterebbe il deploy a uscire con 1 quando il changelog non riesce.
TERMINANO = ("Stop-WithError", "Invoke-Remote(?!Output)", "Invoke-Preflight", "Confirm-Typed",
             "Test-LocalTools", "Test-Vpn", "Test-ConnessioneCompleta", "Publish-Release")


def test_timbro_non_termina_mai_il_deploy():
    """Controlli statici sul codice PowerShell del timbro (qui non si esegue)."""
    for nome in ("Invoke-RemoteOutput", "Find-PythonTimbro", "Invoke-TimbroChangelog"):
        corpo = _funzione(nome)
        assert not re.search(r"(?<![.\w])exit\b", corpo), nome
        for vietata in TERMINANO:
            assert not re.search(rf"(?<![-\w]){vietata}\b", corpo), (nome, vietata)
        assert "$ErrorActionPreference = 'Continue'" in corpo, nome
    corpo = _funzione("Invoke-TimbroChangelog")
    assert "try {" in corpo and "catch {" in corpo
    # Il comando manuale deve restare incollabile anche con spazi nel percorso.
    assert '(@("& `"$($python[0])`"")' in _funzione("Invoke-TimbroChangelog")
    # Tutte le corrispondenze del PATH, non solo la prima.
    assert "Select-Object -First 1" not in _funzione("Find-PythonTimbro")
    assert "\"--aggiornata=$($info['aggiornata'])\"" in corpo
    assert "$Ref -ne 'origin/main'" in corpo
    for sintassi_ps7 in ("??", "&&", "||", " ? "):
        for nome in ("Invoke-RemoteOutput", "Find-PythonTimbro", "Invoke-TimbroChangelog"):
            assert sintassi_ps7 not in _funzione(nome), (nome, sintassi_ps7)


def test_timbro_chiamato_solo_dopo_deploy_e_install():
    testo = (RADICE / "scripts" / "deploy.ps1").read_bytes().decode("ascii").replace("\r\n", "\n")
    chiamate = re.findall(r"^( +)Invoke-TimbroChangelog -Uscita \$uscita$", testo, re.MULTILINE)
    assert len(chiamate) == 2
    for azione in ("install", "deploy"):
        blocco = re.search(rf"^    '{azione}' \{{\n(.*?)^    \}}\n", testo, re.MULTILINE | re.DOTALL).group(1)
        assert "$uscita = Publish-Release 'deploy'" in blocco
        assert blocco.rstrip().endswith("Invoke-TimbroChangelog -Uscita $uscita")
    assert "Publish-Release 'build' @() | Out-Null" in testo
