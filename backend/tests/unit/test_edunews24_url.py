"""Validazione di host e URL di EduNews24: si scarta, non si corregge."""

from __future__ import annotations

import pytest

from src.edunews24.url import e_segnaposto, host_base, host_pubblico, host_valido, url_sicuro

MEDIA = frozenset({"media.edunews24.invalid"})


def test_url_valido_restituisce_la_stringa_originale():
    for valore in ("https://media.edunews24.invalid/a.jpg",
                   "https://media.edunews24.invalid/percorso/a%20b.jpg?v=2#f",
                   "https://MEDIA.edunews24.invalid/A.JPG"):
        assert url_sicuro(valore, MEDIA) is valore


def test_la_porta_443_esplicita_e_ammessa():
    assert url_sicuro("https://media.edunews24.invalid:443/a.jpg", MEDIA) is not None


@pytest.mark.parametrize("valore", [
    "http://media.edunews24.invalid/a.jpg",               # mai promosso a https
    "https://utente:segreto@media.edunews24.invalid/a.jpg",
    "https://utente@media.edunews24.invalid/a.jpg",
    "https://media.edunews24.invalid:8443/a.jpg",
    "https://media.edunews24.invalid:99999/a.jpg",       # porta fuori intervallo: ValueError
    "https://media.edunews24.invalid:/a.jpg",
    "https:media.edunews24.invalid/a.jpg",                # senza //
    "//media.edunews24.invalid/a.jpg",
    "/a.jpg",
    "ftp://media.edunews24.invalid/a.jpg",
    "javascript:alert(1)",
])
def test_url_non_ammessi(valore):
    assert url_sicuro(valore, MEDIA) is None


@pytest.mark.parametrize("valore", [
    "https://media.edunews24.invalid\\@example.org/a.jpg",
    "https://media.edunews24.invalid/a b.jpg",
    "https://media.edunews24.invalid/a.jpg\n",
    "https://media.edunews24.invalid/a\x00.jpg",
    "https://media.edunews24.invalid/a\x7f.jpg",
    "https://media.edunews24.invalid/à.jpg",
    "https://mèdia.edunews24.invalid/a.jpg",
    "https://[x/",
    "https://[::1]/a",
    "https://media.edunews24.invalid/[a].jpg",
])
def test_caratteri_non_ammessi_si_scartano_senza_sollevare(valore):
    assert url_sicuro(valore, MEDIA) is None


def test_l_host_deve_essere_esattamente_in_elenco():
    assert url_sicuro("https://x.media.edunews24.invalid/a.jpg", MEDIA) is None
    assert url_sicuro("https://edunews24.invalid/a.jpg", MEDIA) is None
    assert url_sicuro("https://media.edunews24.invalid./a.jpg", MEDIA) is None
    assert url_sicuro("https://media.edunews24.invalid.example.org/a.jpg", MEDIA) is None


def test_lunghezza_massima_e_tipi():
    lungo = "https://media.edunews24.invalid/" + "a" * 1000
    assert url_sicuro(lungo, MEDIA) is None
    assert url_sicuro(None, MEDIA) is None
    assert url_sicuro(123, MEDIA) is None
    assert url_sicuro("", MEDIA) is None
    assert url_sicuro("https://media.edunews24.invalid/a.jpg", frozenset()) is None


def test_segnaposto_su_qualunque_host():
    assert e_segnaposto("https://edunews24.invalid/edunews24_immagine_da_sostituire.png")
    assert e_segnaposto("https://media.edunews24.invalid/edunews24_immagine_da_sostituire.png")
    assert not e_segnaposto("https://media.edunews24.invalid/a/edunews24_immagine_da_sostituire.png")
    assert not e_segnaposto("https://[x/edunews24_immagine_da_sostituire.png")
    assert not e_segnaposto(None)


def test_host_valido():
    assert host_valido("media.edunews24.invalid")
    assert host_valido("a-b.example.org")
    for valore in ("", "Media.example.org", "a..b", "a.b.", "-a.b", "a-.b", "a_b.c", "a b.c", None, 1,
                   "a" * 64 + ".org", "*.example.org"):
        assert not host_valido(valore), valore


@pytest.mark.parametrize("host", [
    "192.0.2.10", "localhost", "intranet", "server.lan", "server.local", "server.internal",
    "server.localhost", "server.corp",
    # Forme IPv4 che il browser legge come numero: 127.0.0.1 e 192.0.2.10.
    "127.0x1", "0x7f.0x1", "192.0.2.0xa", "0xc0.0x0.0x2.0xa", "0x.0x", "media.0x", "192.0.2.012",
])
def test_host_pubblico_rifiuta_ip_e_nomi_interni(host):
    assert not host_pubblico(host)


def test_host_pubblico_ammette_i_nomi_pubblici():
    assert host_pubblico("edunews24.invalid")
    assert host_pubblico("media.example.org")
    # Non e' un numero esadecimale: resta un nome.
    assert host_pubblico("media.0xg")


def test_host_base():
    assert host_base("https://edunews24.invalid/api/v1") == "edunews24.invalid"
    assert host_base("https://edunews24.invalid:443/api/v1/") == "edunews24.invalid"
    for valore in (
        "https://www.edunews24.invalid/api/v1",
        "https://edunews24.invalid/api/v1?x=1",
        "https://edunews24.invalid/api/v1?",
        "https://edunews24.invalid/api/v1#frammento",
        "https://edunews24.invalid:8443/api/v1",
        "http://edunews24.invalid/api/v1",
        "https://192.0.2.10/api/v1",
        "https://localhost/api/v1",
        "https://utente:segreto@edunews24.invalid/api/v1",
        "edunews24.invalid/api/v1",
        "https://[x/api",
        "https://edunews24 .invalid/api",
        "",
    ):
        assert host_base(valore) is None, valore
