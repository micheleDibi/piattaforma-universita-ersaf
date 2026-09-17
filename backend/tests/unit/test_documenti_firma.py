"""Firma della pratica: intestazione del gestionale e ritaglio sul tratto."""

from __future__ import annotations

import io

import pytest
from PIL import Image, ImageDraw

from src.documenti.firma import immagine_firma

INTESTAZIONE = b"BLOBpng" + b"\x00" * 9


def png(immagine: Image.Image) -> bytes:
    uscita = io.BytesIO()
    immagine.save(uscita, "PNG")
    return uscita.getvalue()


def tela_firmata(trasparente: bool = True) -> bytes:
    """Una tela come quelle del gestionale (788x724) con un tratto in mezzo."""
    tela = Image.new("RGBA", (788, 724), (255, 255, 255, 0 if trasparente else 255))
    ImageDraw.Draw(tela).line([(200, 400), (500, 360)], fill=(10, 20, 60, 255), width=6)
    return png(tela)


def misura(contenuto: bytes) -> tuple[int, int]:
    with Image.open(io.BytesIO(contenuto)) as immagine:
        return immagine.size


@pytest.mark.parametrize("trasparente", [True, False])
def test_senza_intestazione_e_ritagliata_sul_tratto(trasparente):
    firma = immagine_firma(INTESTAZIONE + tela_firmata(trasparente))
    assert firma.startswith(b"\x89PNG\r\n\x1a\n")
    larghezza, altezza = misura(firma)
    assert 300 <= larghezza <= 330 and 40 <= altezza <= 70  # il tratto e un margine, non la tela


def test_una_firma_gia_senza_intestazione_si_ritaglia_lo_stesso():
    assert misura(immagine_firma(tela_firmata())) == misura(immagine_firma(INTESTAZIONE + tela_firmata()))


@pytest.mark.parametrize("contenuto", [
    b"non-e-un-immagine",
    INTESTAZIONE + b"ancora-niente",
    tela_firmata()[:120],  # PNG troncato: l'intestazione c'e', i dati no
])
def test_un_binario_illeggibile_resta_com_e(contenuto):
    assert immagine_firma(contenuto) == contenuto


def test_tela_vuota_e_firma_assente():
    vuota = png(Image.new("RGBA", (120, 60), (255, 255, 255, 0)))
    assert immagine_firma(vuota) == vuota
    assert immagine_firma(None) is None
    assert immagine_firma(b"") is None
