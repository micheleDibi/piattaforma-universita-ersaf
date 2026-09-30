"""Overlay EduNews24 e isolamento rispetto alle notifiche reali."""

import pytest

from supporto_edunews24 import (
    ATTIVA, DUE_CHIAMATE, ID, attesi, compose_env, copia, crea,
    della_release, esegui, pytestmark, server, verifica,
)


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


@pytest.mark.parametrize("uscita", ATTIVA)
def test_escluso_con_le_notifiche_reali(server, uscita):
    """Con due reti non interne il gateway lo sceglie Docker: l'SMTP potrebbe
    finire sul bridge EduNews24, che ammette solo la 443."""
    compose_env(server, *uscita, "NOTIFICHE_REALI=si")
    crea(copia(server))
    crea(della_release(server, "compose.edunews24.yml"))
    # Senza l'overlay delle notifiche compose_rel terminerebbe con die.
    notifiche = crea(della_release(server, "compose.notifiche.yml"))
    verifica(esegui(server, DUE_CHIAMATE), server, [notifiche])


@pytest.mark.parametrize("uscita", ATTIVA)
def test_senza_copia_avvisa_una_volta_e_non_termina(server, uscita):
    """Regole mai installate: la rete resta scollegata anche se la release
    contiene l'overlay, e l'avviso compare una volta sola su stderr."""
    compose_env(server, *uscita)
    crea(della_release(server, "compose.edunews24.yml"))
    esito = esegui(server, DUE_CHIAMATE)
    verifica(esito, server, [], avvisi=1)
    assert "USCITA_EDUNEWS24" in esito.stderr


@pytest.mark.parametrize("righe", [
    pytest.param([], id="chiave-assente"),
    pytest.param(["USCITA_EDUNEWS24="], id="riga-vuota"),
    pytest.param(["USCITA_EDUNEWS24=no", "USCITA_EDUNEWS24="], id="ultima-riga-vuota"),
    pytest.param(["USCITA_EDUNEWS24=no", "USCITA_EDUNEWS24=si"], id="ultima-occorrenza"),
    pytest.param(["ALTRA_CHIAVE=no"], id="altra-chiave"),
    pytest.param(["VECCHIA_USCITA_EDUNEWS24=no"], id="chiave-piu-lunga"),
    pytest.param(["# USCITA_EDUNEWS24=no"], id="commentata"),
])
def test_attiva_per_difetto(server, righe):
    """Senza un valore esplicito diverso da si l'uscita e' attiva: con la copia
    in shared/ l'overlay si collega, senza avvisi."""
    compose_env(server, *righe)
    crea(copia(server))
    overlay = crea(della_release(server, "compose.edunews24.yml"))
    verifica(esegui(server, DUE_CHIAMATE), server, [overlay])


@pytest.mark.parametrize("situazione", ["copia", "senza-copia", "sms-reali"])
@pytest.mark.parametrize("righe", [
    pytest.param(["USCITA_EDUNEWS24=no"], id="no"),
    pytest.param(["USCITA_EDUNEWS24=si "], id="spazio-in-coda"),
    pytest.param(['USCITA_EDUNEWS24="si"'], id="apici"),
    pytest.param(["USCITA_EDUNEWS24=SI"], id="maiuscolo"),
    pytest.param(["USCITA_EDUNEWS24=off"], id="altro-valore"),
    pytest.param(["USCITA_EDUNEWS24=si", "USCITA_EDUNEWS24=no"], id="ultima-occorrenza"),
])
def test_spenta_con_un_valore_diverso_da_si(server, righe, situazione):
    """Solo un valore esplicito diverso da si spegne l'uscita: niente overlay e
    nessun avviso, ne' senza copia ne' con gli SMS reali."""
    compose_env(server, *righe)
    if situazione != "senza-copia":
        crea(copia(server))
    if situazione == "sms-reali":
        api_env(server, "SMS_BACKEND=skebby")
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


@pytest.mark.parametrize("uscita", ATTIVA[1:])
def test_sms_reali_escludono_la_rete_anche_per_difetto(server, uscita):
    """Uscita attiva per difetto: gli SMS reali tengono scollegata la rete
    come con si, con un avviso e senza stampare nulla di api.env."""
    compose_env(server, *uscita)
    api_env(server, "SMS_BACKEND=skebby")
    crea(copia(server))
    crea(della_release(server, "compose.edunews24.yml"))
    esito = esegui(server, DUE_CHIAMATE)
    verifica(esito, server, [], avvisi=1)
    assert "SMS_BACKEND=skebby" in esito.stderr
    nessun_valore(esito)


@pytest.mark.parametrize("uscita", ATTIVA)
def test_sms_reali_senza_copia_un_solo_avviso(server, uscita):
    """Senza copia vale l'avviso degli SMS, non quello delle regole mancanti."""
    compose_env(server, *uscita)
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


@pytest.mark.parametrize("uscita", ATTIVA)
def test_sms_reali_con_le_notifiche_reali_invariato(server, uscita):
    """Con NOTIFICHE_REALI=si gli SMS escono dal bridge delle notifiche: vale
    solo l'esclusione per le due reti, senza avvisi."""
    compose_env(server, *uscita, "NOTIFICHE_REALI=si")
    api_env(server, "SMS_BACKEND=skebby")
    crea(copia(server))
    crea(della_release(server, "compose.edunews24.yml"))
    notifiche = crea(della_release(server, "compose.notifiche.yml"))
    verifica(esegui(server, DUE_CHIAMATE), server, [notifiche])


def righe_docker(esito):
    """Stdout senza le righe di log, che iniziano con l'ora fra parentesi."""
    return [r for r in esito.stdout.splitlines() if not r.startswith("[")]


@pytest.mark.parametrize("uscita", ATTIVA)
def test_prepara_con_sms_reali_toglie_la_copia(server, uscita):
    """Come in cmd_deploy: compose_rel (da cmd_release), poi
    prepara_edunews24, poi di nuovo compose_rel. La copia sparisce, nessuna
    regola si installa, l'avviso compare una volta sola e il deploy prosegue."""
    compose_env(server, *uscita)
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


@pytest.mark.parametrize("uscita", ATTIVA)
def test_prepara_da_sola_con_sms_reali_avvisa(server, uscita):
    compose_env(server, *uscita, "NOTIFICHE_REALI=no")
    api_env(server, "SMS_BACKEND=skebby")
    crea(copia(server))
    esito = esegui(server, f"ACTIVE_ID={ID}\nprepara_edunews24 </dev/null\n")
    assert esito.returncode == 0, esito.stderr
    assert "ERRORE" not in esito.stderr
    assert esito.stderr.count("ATTENZIONE") == 1, esito.stderr
    assert "SMS_BACKEND=skebby" in esito.stderr
    assert not copia(server).exists()
    assert righe_docker(esito) == []


@pytest.mark.parametrize("uscita", ATTIVA)
@pytest.mark.parametrize(("chiavi", "righe"), [
    pytest.param(["NOTIFICHE_REALI=si"], ["SMS_BACKEND=skebby"], id="notifiche-reali"),
    pytest.param([], ["SMS_BACKEND=memoria"], id="memoria"),
    pytest.param([], [], id="chiave-assente"),
])
def test_prepara_senza_il_caso_sms_non_tocca_la_copia(server, chiavi, righe, uscita):
    """Fuori dal caso degli SMS, prepara_edunews24 segue il percorso di sempre:
    con la release senza overlay avvisa e lascia la copia com'e'."""
    compose_env(server, *uscita, *chiavi)
    api_env(server, *righe)
    crea(copia(server))
    esito = esegui(server, f"ACTIVE_ID={ID}\nprepara_edunews24 </dev/null\n")
    assert esito.returncode == 0, esito.stderr
    assert esito.stderr.count("ATTENZIONE") == 1, esito.stderr
    assert "non contiene deploy/compose.edunews24.yml" in esito.stderr
    assert copia(server).exists()


@pytest.mark.parametrize("uscita", ATTIVA)
def test_prepara_con_bridge_diverso_toglie_la_copia(server, uscita):
    """Overlay della release su un bridge diverso da quello filtrato (release
    di un'altra versione, con -Ref): nessuna regola installata, copia tolta,
    un avviso e il deploy prosegue. /usr/local/sbin non viene toccata."""
    compose_env(server, *uscita)
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


@pytest.mark.parametrize("righe", [pytest.param([], id="sms-assenti"),
                                   pytest.param(["SMS_BACKEND=skebby"], id="sms-reali")])
@pytest.mark.parametrize("uscita", ["USCITA_EDUNEWS24=no", "USCITA_EDUNEWS24=SI"])
def test_prepara_con_l_uscita_spenta_non_fa_nulla(server, uscita, righe):
    """Con un valore diverso da si prepara_edunews24 esce subito: nessuna
    chiamata a docker, nessun log, nessun avviso e copia lasciata com'e',
    anche con gli SMS reali. L'overlay della release su un altro bridge
    farebbe altrimenti togliere la copia con un avviso."""
    compose_env(server, uscita)
    api_env(server, *righe)
    crea(copia(server))
    della_release(server, "compose.edunews24.yml").write_text(
        "networks:\n  edunews24:\n    driver_opts:\n      com.docker.network.bridge.name: br-uni-altro\n",
        encoding="utf-8")
    esito = esegui(server, f"ACTIVE_ID={ID}\nprepara_edunews24 </dev/null\n")
    assert esito.returncode == 0, esito.stderr
    assert esito.stdout == "" and esito.stderr == ""
    assert copia(server).exists()
