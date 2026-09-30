"""DNS, regole firewall e verifica del bridge EduNews24, senza rete reale."""

import re
import subprocess

import pytest

from comune import RADICE
from supporto_edunews24 import (
    CATENA, INTERVALLI, NAMESERVER, PONTE, STUB, bash, esegui, pytestmark, server,
)
from supporto_shell import percorso_shell


@pytest.mark.parametrize(("host", "resolved", "trovati"), [
    pytest.param(STUB, "nameserver 192.0.2.10\nnameserver 198.51.100.7\n", ["192.0.2.10", "198.51.100.7"],
                 id="solo-lo-stub"),
    pytest.param("nameserver 127.0.0.53\nnameserver 203.0.113.5\n", "nameserver 192.0.2.10\n", ["203.0.113.5"],
                 id="stub-e-altro-nameserver"),
    pytest.param("# nameserver 192.0.2.99\n; nameserver 192.0.2.98\nnameserver 198.51.100.7\n"
                 "nameserver 198.51.100.7\nnameserver 256.0.2.1\nnameserver 2001:db8::1\nnameserver 192.0.2.10\n",
                 "nameserver 203.0.113.5\n", ["192.0.2.10", "198.51.100.7"], id="commenti-doppioni-e-scarti"),
    pytest.param("nameserver 127.0.0.1\nnameserver 127.0.1.1\n", "nameserver 192.0.2.10\n", [],
                 id="solo-loopback"),
])
def test_nameserver_letti_come_docker(server, tmp_path, host, resolved, trovati):
    """systemd-resolved vale solo quando l'host ha come unico nameserver lo
    stub locale; loopback, IPv6 e indirizzi non validi si scartano."""
    file_host = tmp_path / "resolv.conf"
    file_host.write_text(host, encoding="utf-8")
    file_resolved = tmp_path / "resolved.conf"
    file_resolved.write_text(resolved, encoding="utf-8")
    esito = esegui(server, NAMESERVER, str(file_host), str(file_resolved))
    assert esito.returncode == 0, esito.stderr
    assert esito.stdout.splitlines() == trovati


@pytest.mark.parametrize("host", [None, STUB], ids=["senza-resolv", "stub-senza-resolved"])
def test_nameserver_senza_file(server, tmp_path, host):
    file_host = tmp_path / "resolv.conf"
    if host is not None:
        file_host.write_text(host, encoding="utf-8")
    esito = esegui(server, NAMESERVER, str(file_host), percorso_shell(tmp_path / "assente.conf"))
    assert esito.returncode == 0, esito.stderr
    assert esito.stdout == ""


def firewall(server, tmp_path, forward=True):
    """Genera lo script del firewall e lo esegue con un iptables finto che
    registra le chiamate: -C FORWARD riesce solo con forward, ogni altro -C e
    ogni -D falliscono (regola assente), il resto riesce."""
    script = tmp_path / "firewall.sh"
    generato = esegui(server, 'edunews24_script_firewall > "$1" </dev/null\n', percorso_shell(script))
    assert generato.returncode == 0, generato.stderr
    assert generato.stdout == ""
    finti = tmp_path / "finti"
    finti.mkdir()
    registro = tmp_path / "registro.txt"
    iptables = finti / "iptables"
    iptables.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> '{percorso_shell(registro)}'\n"
        'case " $* " in\n'
        f"    *' -C FORWARD '*) exit {0 if forward else 1};;\n"
        "    *' -C '*|*' -D '*) exit 1;;\n"
        "esac\n"
        "exit 0\n", encoding="utf-8", newline="\n")
    iptables.chmod(0o755)
    resolv = tmp_path / "resolv.conf"
    resolv.write_text("nameserver 192.0.2.10\n", encoding="utf-8")
    esito = subprocess.run([bash, percorso_shell(script), percorso_shell(resolv), percorso_shell(tmp_path / "assente.conf")],
                           stdin=subprocess.DEVNULL, capture_output=True, encoding="utf-8",
                           env={"PATH": f"{percorso_shell(finti)}:/usr/bin:/bin"}, timeout=60)
    righe = registro.read_text(encoding="utf-8").splitlines() if registro.exists() else []
    return esito, righe


def test_script_firewall_in_ordine(server, tmp_path):
    """Cancello prima della catena, DNS prima dei blocchi, 443 dopo i blocchi,
    salto e regola INPUT solo se mancano, cancello tolto alla fine."""
    esito, righe = firewall(server, tmp_path)
    assert esito.returncode == 0, esito.stderr
    assert righe == [
        "-w -N DOCKER-USER", f"-w -I DOCKER-USER 1 -i {PONTE} -j REJECT", "-w -C FORWARD -j DOCKER-USER",
        f"-w -N {CATENA}", f"-w -F {CATENA}", f"-w -A {CATENA} -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN",
        f"-w -A {CATENA} -d 192.0.2.10/32 -p udp --dport 53 -j RETURN",
        f"-w -A {CATENA} -d 192.0.2.10/32 -p tcp --dport 53 -j RETURN",
        *[f"-w -A {CATENA} -d {r} -j REJECT" for r in INTERVALLI], f"-w -A {CATENA} -p tcp --dport 443 -j RETURN",
        f"-w -A {CATENA} -j REJECT", f"-w -C DOCKER-USER -i {PONTE} -j {CATENA}",
        f"-w -I DOCKER-USER 2 -i {PONTE} -j {CATENA}",
        f"-w -C INPUT -i {PONTE} -m conntrack --ctstate NEW -j REJECT",
        f"-w -I INPUT 1 -i {PONTE} -m conntrack --ctstate NEW -j REJECT",
        f"-w -D DOCKER-USER -i {PONTE} -j REJECT"]


def test_script_firewall_senza_forward(server, tmp_path):
    """Senza il salto da FORWARD a DOCKER-USER (backend nftables di Docker)
    l'unita' fallisce e il cancello resta: il bridge non esce."""
    esito, righe = firewall(server, tmp_path, forward=False)
    assert esito.returncode != 0
    assert righe == ["-w -N DOCKER-USER", f"-w -I DOCKER-USER 1 -i {PONTE} -j REJECT", "-w -C FORWARD -j DOCKER-USER"]
    assert "DOCKER-USER" in esito.stderr


def test_overlay_sul_bridge_filtrato():
    """L'overlay deve creare proprio il bridge che le regole filtrano: con un
    nome diverso l'API uscirebbe da un bridge senza regole. Il nome di
    un'interfaccia Linux ha al massimo 15 caratteri."""
    testo = (RADICE / "deploy" / "compose.edunews24.yml").read_text(encoding="ascii")
    assert f"com.docker.network.bridge.name: {PONTE}\n" in testo
    assert re.search(r"^ +enable_ipv6: false$", testo, re.M)
    assert not re.search(r"^ *ports *:", testo, re.M)
    assert len(PONTE) <= 15


@pytest.mark.parametrize(("riga", "riconosciuto"), [
    pytest.param(None, True, id="overlay-del-repository"),
    pytest.param(f"      com.docker.network.bridge.name: {PONTE} \r\n", True, id="spazio-e-cr"),
    pytest.param("      com.docker.network.bridge.name: br-uni-altro\n", False, id="altro-bridge"),
    pytest.param(f"      com.docker.network.bridge.name: {PONTE}x\n", False, id="nome-piu-lungo"),
    pytest.param(f"      # com.docker.network.bridge.name: {PONTE}\n", False, id="commentata"),
    pytest.param(f'      com.docker.network.bridge.name: "{PONTE}"\n', False, id="fra-apici"),
    pytest.param("# file di prova\n", False, id="senza-bridge"),
])
def test_overlay_sul_bridge_confrontato_con_le_regole(server, tmp_path, riga, riconosciuto):
    """prepara_edunews24 copia l'overlay solo se crea il bridge scritto nello
    script del firewall dello stesso bundle; nel dubbio, bridge diverso."""
    if riga is None:
        overlay = RADICE / "deploy" / "compose.edunews24.yml"
    else:
        overlay = tmp_path / "overlay.yml"
        overlay.write_text(riga, encoding="utf-8", newline="")
    esito = esegui(server, 'edunews24_overlay_sul_bridge "$1" </dev/null\n', str(overlay))
    assert esito.returncode == (0 if riconosciuto else 1), esito.stderr
    assert esito.stdout == ""


def test_copia_solo_dopo_il_riavvio_dell_unita():
    """compose_rel collega la rete solo se la copia esiste: la copia deve
    seguire le regole applicate, non precederle come in 26-notifiche.sh."""
    testo = (RADICE / "deploy" / "remote" / "27-edunews24.sh").read_text(encoding="ascii")
    assert testo.count('cp "$overlay" "$copia"') == 1
    assert testo.index('systemctl restart "$unit"') < testo.index('cp "$overlay" "$copia"')
