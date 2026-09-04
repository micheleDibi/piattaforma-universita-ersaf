"""Normalizzazione dell'indirizzo IP."""

from __future__ import annotations

import ipaddress

import pytest

from src.security.rete import IP_SCONOSCIUTO, impacchetta_ip, spacchetta_ip


@pytest.mark.parametrize(
    "indirizzo, byte_attesi",
    [("127.0.0.1", 4), ("203.0.113.9", 4), ("::1", 16), ("2001:db8::1", 16)],
)
def test_impacchetta_come_inet6_aton(indirizzo, byte_attesi):
    """Stessa lunghezza e stessi byte di INET6_ATON: 4 per IPv4, 16 per IPv6.
    L'equivalenza vera contro MariaDB e' verificata in tests/db."""
    pacchetto = impacchetta_ip(indirizzo)
    assert len(pacchetto) == byte_attesi
    assert pacchetto == ipaddress.ip_address(indirizzo).packed


@pytest.mark.parametrize("valore", [None, "", "testclient", "non-un-ip", "999.1.1.1"])
def test_valori_non_interpretabili_non_diventano_nulli(valore):
    """prr_ip e' VARBINARY(16) NOT NULL: INET6_ATON('testclient') darebbe NULL
    e ogni richiesta di test finirebbe in 500 per violazione del vincolo."""
    assert impacchetta_ip(valore) == IP_SCONOSCIUTO
    assert len(impacchetta_ip(valore)) == 16


def test_ipv4_mapped_finisce_nello_stesso_contenitore():
    """INET6_ATON ne produrrebbe due distinti, e chi passa da un proxy
    dual-stack raddoppierebbe il proprio limite orario."""
    assert impacchetta_ip("::ffff:203.0.113.9") == impacchetta_ip("203.0.113.9")


def test_spacchetta_per_la_mail_di_notifica():
    assert spacchetta_ip(impacchetta_ip("203.0.113.9")) == "203.0.113.9"
    assert spacchetta_ip(impacchetta_ip("2001:db8::1")) == "2001:db8::1"
    assert spacchetta_ip(IP_SCONOSCIUTO) == "non disponibile"
    assert spacchetta_ip(None) == "non disponibile"
