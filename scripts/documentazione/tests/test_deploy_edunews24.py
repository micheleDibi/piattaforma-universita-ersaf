"""compose_rel, nameserver e firewall dell'uscita verso EduNews24.

Il bundle degli script remoti, senza il dispatcher 90-main.sh, gira con bash
seguito da poche righe di prova. Un docker finto in testa al PATH stampa i
propri argomenti, uno per riga; lo script del firewall generato gira con un
iptables finto che registra le chiamate. Deve funzionare con la bash 3.2.

Gli indirizzi dei nameserver sono solo di documentazione (RFC 5737 e 3849).
"""

from __future__ import annotations

import re
import shutil
import subprocess

import pytest

from comune import RADICE

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

bash = shutil.which("bash")
pytestmark = pytest.mark.skipif(bash is None, reason="bash non disponibile")


def bundle() -> str:
    return "\n".join(p.read_bytes().decode("ascii").replace("\r\n", "\n") for p in REMOTI) + "\n"


def esegui(base, coda, *argomenti):
    finto = base.parent / "bin"
    finto.mkdir(exist_ok=True)
    docker = finto / "docker"
    docker.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\"\n", encoding="utf-8")
    docker.chmod(0o755)
    ambiente = {"PATH": f"{finto}:/usr/bin:/bin:/usr/local/bin", "ERSAF_DEPLOY_BASE": str(base), "HOME": str(base)}
    return subprocess.run([bash, "-s", "--", *argomenti], input=bundle() + coda, capture_output=True,
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
    comuni = ["compose", "-p", PROGETTO, "--project-directory", str(base),
              "--env-file", str(base / "shared" / "compose.env"), "-f", str(della_release(base, "compose.yml"))]
    for percorso in overlay:
        comuni += ["-f", str(percorso)]
    return [*comuni, "config", "--quiet", *comuni, "ps", "-q", "api"]


def verifica(esito, base, overlay, avvisi=0):
    assert esito.returncode == 0, esito.stderr
    assert "ERRORE" not in esito.stderr
    # Lo stdout di compose_active lo leggono container_id e db_query: solo
    # docker deve scriverci.
    assert esito.stdout.splitlines() == attesi(base, overlay)
    assert esito.stderr.count("ATTENZIONE") == avvisi, esito.stderr


def test_copia_in_shared_se_la_release_non_ha_l_overlay(server):
    """Rollback a una release precedente all'overlay: vale la copia in shared/."""
    compose_env(server, "USCITA_EDUNEWS24=si")
    crea(copia(server))
    verifica(esegui(server, DUE_CHIAMATE), server, [copia(server)])


def test_overlay_della_release_se_presente(server):
    compose_env(server, "USCITA_EDUNEWS24=si")
    crea(copia(server))
    overlay = crea(della_release(server, "compose.edunews24.yml"))
    verifica(esegui(server, DUE_CHIAMATE), server, [overlay])


def test_escluso_con_le_notifiche_reali(server):
    """Con due reti non interne il gateway lo sceglie Docker: l'SMTP potrebbe
    finire sul bridge EduNews24, che ammette solo la 443."""
    compose_env(server, "USCITA_EDUNEWS24=si", "NOTIFICHE_REALI=si")
    crea(copia(server))
    crea(della_release(server, "compose.edunews24.yml"))
    # Senza l'overlay delle notifiche compose_rel terminerebbe con die.
    notifiche = crea(della_release(server, "compose.notifiche.yml"))
    verifica(esegui(server, DUE_CHIAMATE), server, [notifiche])


def test_senza_copia_avvisa_una_volta_e_non_termina(server):
    """Regole mai installate: la rete resta scollegata anche se la release
    contiene l'overlay, e l'avviso compare una volta sola su stderr."""
    compose_env(server, "USCITA_EDUNEWS24=si")
    crea(della_release(server, "compose.edunews24.yml"))
    esito = esegui(server, DUE_CHIAMATE)
    verifica(esito, server, [], avvisi=1)
    assert "USCITA_EDUNEWS24" in esito.stderr


@pytest.mark.parametrize("riga", ["USCITA_EDUNEWS24=no", "USCITA_EDUNEWS24=si ", 'USCITA_EDUNEWS24="si"',
                                  "USCITA_EDUNEWS24=SI", "ALTRA_CHIAVE=si", "VECCHIA_USCITA_EDUNEWS24=si",
                                  "# USCITA_EDUNEWS24=si"])
def test_chiave_diversa_da_si(server, riga):
    compose_env(server, riga)
    crea(copia(server))
    crea(della_release(server, "compose.edunews24.yml"))
    verifica(esegui(server, DUE_CHIAMATE), server, [])


def test_ordine_con_esposizione(server):
    compose_env(server, "ESPOSIZIONE=si", "USCITA_EDUNEWS24=si")
    esposizione = crea(della_release(server, "compose.esposizione.yml"))
    crea(copia(server))
    verifica(esegui(server, DUE_CHIAMATE), server, [esposizione, copia(server)])


# Valore finto: non deve mai comparire nell'output.
SEGRETO = "SKEBBY_ACCESS_TOKEN=valore-di-prova-da-non-stampare"


def api_env(base, *righe):
    """shared/api.env con una chiave finta e le righe indicate."""
    (base / "shared" / "api.env").write_text("\n".join([SEGRETO, *righe]) + "\n", encoding="utf-8",
                                             newline="")


def nessun_valore(esito):
    assert "valore-di-prova" not in esito.stdout + esito.stderr


@pytest.mark.parametrize("notifiche", [[], ["NOTIFICHE_REALI=no"]], ids=["notifiche-assenti", "notifiche-no"])
@pytest.mark.parametrize("righe", [
    pytest.param(["SMS_BACKEND=skebby"], id="skebby"),
    pytest.param(["SMS_BACKEND=file", "SMS_BACKEND=skebby"], id="ultima-occorrenza"),
    pytest.param(['SMS_BACKEND="skebby"'], id="apici-doppi"),
    pytest.param(["SMS_BACKEND='skebby'"], id="apici-singoli"),
    pytest.param(["SMS_BACKEND=skebby \r"], id="spazio-e-cr"),
    pytest.param(["SMS_BACKEND=skebby # invii reali"], id="commento-in-coda"),
    # Forme che Docker Compose accetta nell'env_file; il nome in minuscolo lo
    # accetta anche l'API, che legge le variabili senza distinguere maiuscole.
    pytest.param(["export SMS_BACKEND=skebby"], id="export"),
    pytest.param(["export\tSMS_BACKEND=skebby"], id="export-tab"),
    pytest.param(["sms_backend=skebby"], id="minuscolo"),
    pytest.param(["Sms_Backend=skebby"], id="maiuscole-miste"),
    pytest.param(["SMS_BACKEND = skebby"], id="spazi-attorno-all-uguale"),
    pytest.param(["  SMS_BACKEND=skebby"], id="rientro"),
    pytest.param(["\tSMS_BACKEND=skebby"], id="rientro-tab"),
    pytest.param(["SMS_BACKEND: skebby"], id="due-punti"),
    pytest.param(['  export  sms_backend  =  "skebby"  # invii reali'], id="tutto-insieme"),
    pytest.param(["SMS_BACKEND=file", "export SMS_BACKEND = skebby"], id="ultima-occorrenza-altra-forma"),
])
def test_sms_reali_escludono_la_rete(server, notifiche, righe):
    """Con SMS_BACKEND=skebby e senza NOTIFICHE_REALI=si la 443 del bridge
    farebbe partire gli SMS reali: niente rete, un avviso, nessun die, e
    nulla di api.env sullo stdout o nell'avviso."""
    compose_env(server, "USCITA_EDUNEWS24=si", *notifiche)
    api_env(server, *righe)
    crea(copia(server))
    crea(della_release(server, "compose.edunews24.yml"))
    esito = esegui(server, DUE_CHIAMATE)
    verifica(esito, server, [], avvisi=1)
    assert "SMS_BACKEND=skebby" in esito.stderr
    nessun_valore(esito)


def test_sms_reali_senza_copia_un_solo_avviso(server):
    """Senza copia vale l'avviso degli SMS, non quello delle regole mancanti."""
    compose_env(server, "USCITA_EDUNEWS24=si")
    api_env(server, "SMS_BACKEND=skebby")
    esito = esegui(server, DUE_CHIAMATE)
    verifica(esito, server, [], avvisi=1)
    assert "SMS_BACKEND=skebby" in esito.stderr
    assert "non sono installate" not in esito.stderr


@pytest.mark.parametrize("righe", [
    pytest.param(["SMS_BACKEND=memoria"], id="memoria"),
    pytest.param(["SMS_BACKEND=disabilitato"], id="disabilitato"),
    pytest.param(["SMS_BACKEND=file"], id="file"),
    pytest.param([], id="chiave-assente"),
    pytest.param(None, id="api-env-assente"),
    pytest.param(["SMS_BACKEND=skebby", "SMS_BACKEND=memoria"], id="ultima-occorrenza"),
    pytest.param(["# SMS_BACKEND=skebby"], id="commentata"),
    pytest.param(["VECCHIO_SMS_BACKEND=skebby"], id="altra-chiave"),
    pytest.param(["SMS_BACKENDX=skebby"], id="chiave-piu-lunga"),
    pytest.param(["exportSMS_BACKEND=skebby"], id="export-senza-spazio"),
    pytest.param(["SMS_BACKEND=skebby2"], id="altro-valore"),
    pytest.param(["export SMS_BACKEND=skebby", "SMS_BACKEND = memoria"], id="ultima-occorrenza-altra-forma"),
])
def test_sms_non_reali_collegano_la_rete(server, righe):
    compose_env(server, "USCITA_EDUNEWS24=si")
    if righe is not None:
        api_env(server, *righe)
    crea(copia(server))
    overlay = crea(della_release(server, "compose.edunews24.yml"))
    esito = esegui(server, DUE_CHIAMATE)
    verifica(esito, server, [overlay])
    nessun_valore(esito)


def test_sms_reali_con_le_notifiche_reali_invariato(server):
    """Con NOTIFICHE_REALI=si gli SMS escono dal bridge delle notifiche: vale
    solo l'esclusione per le due reti, senza avvisi."""
    compose_env(server, "USCITA_EDUNEWS24=si", "NOTIFICHE_REALI=si")
    api_env(server, "SMS_BACKEND=skebby")
    crea(copia(server))
    crea(della_release(server, "compose.edunews24.yml"))
    notifiche = crea(della_release(server, "compose.notifiche.yml"))
    verifica(esegui(server, DUE_CHIAMATE), server, [notifiche])


def righe_docker(esito):
    """Stdout senza le righe di log, che iniziano con l'ora fra parentesi."""
    return [r for r in esito.stdout.splitlines() if not r.startswith("[")]


def test_prepara_con_sms_reali_toglie_la_copia(server):
    """Come in cmd_deploy: compose_rel (da cmd_release), poi
    prepara_edunews24, poi di nuovo compose_rel. La copia sparisce, nessuna
    regola si installa, l'avviso compare una volta sola e il deploy prosegue."""
    compose_env(server, "USCITA_EDUNEWS24=si")
    api_env(server, "SMS_BACKEND=skebby")
    crea(copia(server))
    crea(della_release(server, "compose.edunews24.yml"))
    coda = (f"ACTIVE_ID={ID}\ncompose_active config --quiet </dev/null\nprepara_edunews24 </dev/null\n"
            "compose_active ps -q api </dev/null\n")
    esito = esegui(server, coda)
    assert esito.returncode == 0, esito.stderr
    assert "ERRORE" not in esito.stderr
    assert esito.stderr.count("ATTENZIONE") == 1, esito.stderr
    assert not copia(server).exists()
    # Nessuna validazione dell'overlay con docker: solo le due chiamate.
    assert righe_docker(esito) == attesi(server, [])
    assert any("copia in shared/ rimossa" in r for r in esito.stdout.splitlines())
    nessun_valore(esito)


def test_prepara_da_sola_con_sms_reali_avvisa(server):
    compose_env(server, "USCITA_EDUNEWS24=si", "NOTIFICHE_REALI=no")
    api_env(server, "SMS_BACKEND=skebby")
    crea(copia(server))
    esito = esegui(server, f"ACTIVE_ID={ID}\nprepara_edunews24 </dev/null\n")
    assert esito.returncode == 0, esito.stderr
    assert "ERRORE" not in esito.stderr
    assert esito.stderr.count("ATTENZIONE") == 1, esito.stderr
    assert "SMS_BACKEND=skebby" in esito.stderr
    assert not copia(server).exists()
    assert righe_docker(esito) == []


@pytest.mark.parametrize(("chiavi", "righe"), [
    pytest.param(["NOTIFICHE_REALI=si"], ["SMS_BACKEND=skebby"], id="notifiche-reali"),
    pytest.param([], ["SMS_BACKEND=memoria"], id="memoria"),
    pytest.param([], [], id="chiave-assente"),
])
def test_prepara_senza_il_caso_sms_non_tocca_la_copia(server, chiavi, righe):
    """Fuori dal caso degli SMS, prepara_edunews24 segue il percorso di sempre:
    con la release senza overlay avvisa e lascia la copia com'e'."""
    compose_env(server, "USCITA_EDUNEWS24=si", *chiavi)
    api_env(server, *righe)
    crea(copia(server))
    esito = esegui(server, f"ACTIVE_ID={ID}\nprepara_edunews24 </dev/null\n")
    assert esito.returncode == 0, esito.stderr
    assert esito.stderr.count("ATTENZIONE") == 1, esito.stderr
    assert "non contiene deploy/compose.edunews24.yml" in esito.stderr
    assert copia(server).exists()


def test_prepara_con_bridge_diverso_toglie_la_copia(server):
    """Overlay della release su un bridge diverso da quello filtrato (release
    di un'altra versione, con -Ref): nessuna regola installata, copia tolta,
    un avviso e il deploy prosegue. /usr/local/sbin non viene toccata."""
    compose_env(server, "USCITA_EDUNEWS24=si")
    crea(copia(server))
    overlay = della_release(server, "compose.edunews24.yml")
    overlay.write_text("networks:\n  edunews24:\n    driver_opts:\n      com.docker.network.bridge.name: br-uni-altro\n",
                       encoding="utf-8")
    esito = esegui(server, f"ACTIVE_ID={ID}\nprepara_edunews24 </dev/null\n")
    assert esito.returncode == 0, esito.stderr
    assert "ERRORE" not in esito.stderr
    assert esito.stderr.count("ATTENZIONE") == 1, esito.stderr
    assert "bridge filtrato" in esito.stderr
    assert not copia(server).exists()
    # Solo la validazione dell'overlay con docker, prima del confronto.
    validazione = attesi(server, [overlay])
    assert righe_docker(esito) == validazione[:validazione.index("--quiet") + 1]


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
    esito = esegui(server, NAMESERVER, str(file_host), str(tmp_path / "assente.conf"))
    assert esito.returncode == 0, esito.stderr
    assert esito.stdout == ""


def firewall(server, tmp_path, forward=True):
    """Genera lo script del firewall e lo esegue con un iptables finto che
    registra le chiamate: -C FORWARD riesce solo con forward, ogni altro -C e
    ogni -D falliscono (regola assente), il resto riesce."""
    script = tmp_path / "firewall.sh"
    generato = esegui(server, 'edunews24_script_firewall > "$1" </dev/null\n', str(script))
    assert generato.returncode == 0, generato.stderr
    assert generato.stdout == ""
    finti = tmp_path / "finti"
    finti.mkdir()
    registro = tmp_path / "registro.txt"
    iptables = finti / "iptables"
    iptables.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> '{registro}'\n"
        'case " $* " in\n'
        f"    *' -C FORWARD '*) exit {0 if forward else 1};;\n"
        "    *' -C '*|*' -D '*) exit 1;;\n"
        "esac\n"
        "exit 0\n", encoding="utf-8")
    iptables.chmod(0o755)
    resolv = tmp_path / "resolv.conf"
    resolv.write_text("nameserver 192.0.2.10\n", encoding="utf-8")
    esito = subprocess.run([bash, str(script), str(resolv), str(tmp_path / "assente.conf")],
                           stdin=subprocess.DEVNULL, capture_output=True, encoding="utf-8",
                           env={"PATH": f"{finti}:/usr/bin:/bin"}, timeout=60)
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
