"""compose_rel, nameserver e firewall dell'uscita verso EduNews24.

Il bundle degli script remoti, senza il dispatcher 90-main.sh, gira con bash
seguito da poche righe di prova. Un docker finto in testa al PATH stampa i
propri argomenti, uno per riga; lo script del firewall generato gira con un
iptables finto che registra le chiamate. Deve funzionare con la bash 3.2.

Gli indirizzi dei nameserver sono solo di documentazione (RFC 5737 e 3849).
"""

from __future__ import annotations

import re
import subprocess

import pytest

from comune import RADICE
from supporto_shell import percorso_shell, trova_bash

REMOTI = [p for p in sorted((RADICE / "deploy" / "remote").glob("*.sh")) if p.name != "90-main.sh"]
ID = "20260917-184000-abcdef1"
PROGETTO = re.search(r'^PROJECT="([^"]+)"', (RADICE / "deploy" / "remote" / "00-lib.sh").read_text(encoding="ascii"),
                     re.M).group(1)
# </dev/null: un figlio che legge stdin consumerebbe il resto dello script
# (come l'ultima riga di 90-main.sh).
DUE_CHIAMATE = "compose_active config --quiet </dev/null\ncompose_active ps -q api </dev/null\n"
NAMESERVER = 'edunews24_nameserver "$1" "$2" </dev/null\n'
PONTE, CATENA = "br-uni-edu24", "ERSAF-UNI-EDU24"
INTERVALLI = ["0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8", "169.254.0.0/16", "172.16.0.0/12",
              "192.0.0.0/24", "192.168.0.0/16", "198.18.0.0/15", "224.0.0.0/4", "240.0.0.0/4"]
STUB = "nameserver 127.0.0.53\noptions edns0 trust-ad\nsearch example.invalid\n"
# Righe di shared/compose.env con cui l'uscita e' attiva: si, oppure la chiave
# assente o vuota (attiva per difetto).
ATTIVA = [pytest.param(["USCITA_EDUNEWS24=si"], id="si"), pytest.param([], id="chiave-assente"),
          pytest.param(["USCITA_EDUNEWS24="], id="riga-vuota")]

bash = trova_bash()
pytestmark = pytest.mark.skipif(bash is None, reason="bash non disponibile")


def bundle() -> str:
    return "\n".join(p.read_bytes().decode("ascii").replace("\r\n", "\n") for p in REMOTI) + "\n"


def esegui(base, coda, *argomenti):
    finto = base.parent / "bin"
    finto.mkdir(exist_ok=True)
    docker = finto / "docker"
    docker.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\"\n", encoding="utf-8", newline="\n")
    docker.chmod(0o755)
    ambiente = {"PATH": f"{percorso_shell(finto)}:/usr/bin:/bin:/usr/local/bin", "ERSAF_DEPLOY_BASE": percorso_shell(base), "HOME": percorso_shell(base)}
    return subprocess.run([bash, "-s", "--", *(percorso_shell(a) for a in argomenti)], input=bundle() + coda, capture_output=True,
                          encoding="utf-8", env=ambiente, timeout=60)


def crea(percorso):
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text("# file di prova\n", encoding="utf-8")
    return percorso


def compose_env(base, *righe):
    """shared/compose.env con la release di prova e le righe indicate."""
    testo = "\n".join([f"RELEASE_TAG={ID}", *righe]) + "\n"
    (base / "shared" / "compose.env").write_text(testo, encoding="utf-8")


def della_release(base, nome):
    return base / "releases" / ID / "deploy" / nome


def copia(base):
    return base / "shared" / "compose.edunews24.yml"


@pytest.fixture
def server(tmp_path):
    base = tmp_path / "server"
    (base / "shared").mkdir(parents=True)
    crea(della_release(base, "compose.yml"))
    return base


def attesi(base, overlay):
    """Righe del docker finto per le due chiamate di DUE_CHIAMATE, con gli
    overlay indicati dopo compose.yml."""
    comuni = ["compose", "-p", PROGETTO, "--project-directory", percorso_shell(base),
              "--env-file", percorso_shell(base / "shared" / "compose.env"), "-f", percorso_shell(della_release(base, "compose.yml"))]
    for percorso in overlay:
        comuni += ["-f", percorso_shell(percorso)]
    return [*comuni, "config", "--quiet", *comuni, "ps", "-q", "api"]


def verifica(esito, base, overlay, avvisi=0):
    assert esito.returncode == 0, esito.stderr
    assert "ERRORE" not in esito.stderr
    # Lo stdout di compose_active lo leggono container_id e db_query: solo
    # docker deve scriverci.
    assert esito.stdout.splitlines() == attesi(base, overlay)
    assert esito.stderr.count("ATTENZIONE") == avvisi, esito.stderr
