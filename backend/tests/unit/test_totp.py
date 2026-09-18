"""TOTP sui vettori della RFC 6238, tolleranza, anti-replay e cifratura del segreto."""

from __future__ import annotations

import pytest

from src.mfa import totp

# Appendice B della RFC 6238: segreto ASCII "12345678901234567890", SHA-1.
# I vettori sono a 8 cifre; con 6 cifre restano le ultime sei.
SEGRETO_RFC = b"12345678901234567890"
VETTORI = [
    (59, "287082"),
    (1111111109, "081804"),
    (1111111111, "050471"),
    (1234567890, "005924"),
    (2000000000, "279037"),
    (20000000000, "353130"),
]


@pytest.mark.parametrize("istante, atteso", VETTORI)
def test_vettori_rfc_6238(istante, atteso):
    assert totp.codice(SEGRETO_RFC, totp.passo_corrente(istante)) == atteso


def test_accetta_il_passo_corrente_e_i_due_adiacenti():
    adesso = 1111111111
    centro = totp.passo_corrente(adesso)
    for passo in (centro - 1, centro, centro + 1):
        assert totp.verifica(SEGRETO_RFC, totp.codice(SEGRETO_RFC, passo), None, adesso) == passo
    assert totp.verifica(SEGRETO_RFC, totp.codice(SEGRETO_RFC, centro - 2), None, adesso) is None
    assert totp.verifica(SEGRETO_RFC, totp.codice(SEGRETO_RFC, centro + 2), None, adesso) is None


def test_un_codice_gia_usato_non_vale_piu():
    adesso = 1234567890
    passo = totp.passo_corrente(adesso)
    codice = totp.codice(SEGRETO_RFC, passo)
    assert totp.verifica(SEGRETO_RFC, codice, None, adesso) == passo
    assert totp.verifica(SEGRETO_RFC, codice, passo, adesso) is None, "stesso passo: replay"
    precedente = totp.codice(SEGRETO_RFC, passo - 1)
    assert totp.verifica(SEGRETO_RFC, precedente, passo, adesso) is None, "passo piu' vecchio dell'ultimo accettato"


@pytest.mark.parametrize("inserito", ["", "12345", "1234567", "12345a", "١٢٣٤٥٦"])
def test_codici_malformati_respinti_senza_confronti(inserito):
    assert totp.verifica(SEGRETO_RFC, inserito, None, 59) is None


def test_segreto_base32_senza_riempimento_e_uri_per_l_app():
    segreto = totp.genera_segreto()
    assert len(segreto) == totp.BYTE_SEGRETO
    b32 = totp.base32_segreto(segreto)
    assert "=" not in b32 and b32.isupper()
    uri = totp.uri_otpauth(segreto, "collaudo.prova")
    assert uri.startswith("otpauth://totp/Piattaforma%20Universit")
    assert f"secret={b32}" in uri and "algorithm=SHA1" in uri and "digits=6" in uri and "period=30" in uri
    assert "collaudo.prova" in uri


def test_cifratura_reversibile_e_diversa_a_ogni_chiamata():
    segreto = totp.genera_segreto()
    primo, secondo = totp.cifra(segreto), totp.cifra(segreto)
    assert primo != secondo, "nonce casuale: due cifrature dello stesso segreto differiscono"
    assert len(primo) == 12 + totp.BYTE_SEGRETO + 16
    assert totp.decifra(primo) == segreto and totp.decifra(secondo) == segreto
    assert segreto not in primo, "il segreto non deve comparire in chiaro nel blob"


def test_blob_manomesso_non_si_decifra():
    blob = bytearray(totp.cifra(totp.genera_segreto()))
    blob[-1] ^= 0x01
    with pytest.raises(Exception):
        totp.decifra(bytes(blob))
