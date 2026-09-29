import ssl
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pymysql
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from src.database_trasporto import opzioni

URL = "mysql+pymysql://utente:segreto-fittizio@{host}/ersaf_test"


def config(modo="verify-full", ca="", ambiente="produzione"):
    return SimpleNamespace(database_trasporto=modo, database_ca_file=ca, ersaf_env=ambiente)


@pytest.mark.parametrize("host", ["10.0.0.2", "172.16.0.1", "172.31.255.254", "192.168.40.12"])
def test_eccezione_richiede_ipv4_privato_e_scelta_esplicita(host):
    with pytest.raises(ValueError):
        opzioni(URL.format(host=host), config())
    assert opzioni(URL.format(host=host), config("rete-privata"))["ssl_disabled"] is True


@pytest.mark.parametrize(
    "host", ["8.8.8.8", "172.32.0.1", "127.0.0.1", "db", "db.example.org", "[::1]", "[fd00::1]"]
)
def test_eccezione_non_accetta_host_pubblico_o_da_risolvere(host):
    with pytest.raises(ValueError):
        opzioni(URL.format(host=host), config("rete-privata"))


@pytest.mark.parametrize(
    "query",
    ["ssl_disabled=true", "ssl_ca=altro", "host=10.0.0.1", "password=esempio", "charset=utf8&CHARSET=latin1"],
)
def test_url_non_puo_sovrascrivere_policy_o_credenziali(query):
    with pytest.raises(ValueError) as errore:
        opzioni(URL.format(host="10.0.0.1") + "?" + query, config("rete-privata"))
    assert "segreto-fittizio" not in str(errore.value)


def test_tls_verifica_hostname_e_fida_solo_la_ca_configurata(tmp_path):
    chiave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CA sintetica test")])
    adesso = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(nome)
        .issuer_name(nome)
        .public_key(chiave.public_key())
        .serial_number(1)
        .not_valid_before(adesso - timedelta(days=1))
        .not_valid_after(adesso + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(chiave, hashes.SHA256())
    )
    file = tmp_path / "ca-test.pem"
    file.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    risultato = opzioni(URL.format(host="db.example.org"), config(ca=str(file)))
    contesto = risultato["ssl"]
    assert contesto.verify_mode == ssl.CERT_REQUIRED and contesto.check_hostname
    assert len(contesto.get_ca_certs()) == 1
    assert risultato["connect_timeout"] == 5 and risultato["read_timeout"] == 10
    # Handshake senza supporto SSL: il driver deve rifiutare PRIMA di inviare
    # il pacchetto di autenticazione, non limitarsi a controllare dopo il login.
    conn = pymysql.Connection(
        host="db.example.org", user="test", password="fittizia", defer_connect=True, **risultato
    )
    conn.server_version, conn.server_capabilities = "10.11", 0
    pacchetti = []
    conn.write_packet = pacchetti.append
    with pytest.raises(pymysql.OperationalError):
        conn._request_authentication()
    assert not pacchetti


def test_test_locale_senza_tls_e_nessun_fallback_ca_in_produzione():
    assert "ssl" not in opzioni(URL.format(host="127.0.0.1"), config(ambiente="test"))
    with pytest.raises(ValueError):
        opzioni(URL.format(host="db.example.org"), config(ca="ca-inesistente.pem"))
