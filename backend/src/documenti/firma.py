"""La firma della pratica pronta per il modulo.

Il gestionale precedente salvava la firma dietro un'intestazione propria di 16
byte ("BLOBpng" e zeri) e su una tela quasi quadrata con il tratto in mezzo: si
toglie l'intestazione e si ritaglia il tratto, cosi' nel modulo la firma ha la
sua misura e non quella della tela.
"""

from __future__ import annotations

import io

from PIL import Image, ImageOps, UnidentifiedImageError

from src.documenti.motore import estensione_immagine

INTESTAZIONE_BLOB = b"BLOB"
LUNGHEZZA_INTESTAZIONE_BLOB = 16
MARGINE_PIXEL = 8
# Sotto questa intensita' e' sfondo o rumore, non inchiostro.
SOGLIA_INCHIOSTRO = 24


def _senza_intestazione(contenuto: bytes) -> bytes:
    immagine = contenuto[LUNGHEZZA_INTESTAZIONE_BLOB:]
    if contenuto.startswith(INTESTAZIONE_BLOB) and estensione_immagine(immagine):
        return immagine
    return contenuto


def _inchiostro(immagine: Image.Image) -> Image.Image:
    """Chiaro dove c'e' tratto: la trasparenza se la tela e' trasparente, altrimenti lo scuro sul chiaro."""
    colori = immagine.convert("RGBA")
    alfa = colori.getchannel("A")
    if alfa.getextrema()[0] < 255:
        return alfa
    return ImageOps.invert(colori.convert("L"))


def _ritagliata(contenuto: bytes) -> bytes:
    try:
        with Image.open(io.BytesIO(contenuto)) as immagine:
            riquadro = _inchiostro(immagine).point(lambda v: 255 if v > SOGLIA_INCHIOSTRO else 0).getbbox()
            if riquadro is None:
                return contenuto  # tela vuota: nulla da ritagliare
            x0, y0, x1, y1 = riquadro
            margini = (max(x0 - MARGINE_PIXEL, 0), max(y0 - MARGINE_PIXEL, 0),
                       min(x1 + MARGINE_PIXEL, immagine.width), min(y1 + MARGINE_PIXEL, immagine.height))
            uscita = io.BytesIO()
            immagine.crop(margini).save(uscita, "PNG")
            return uscita.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        return contenuto  # il modulo mostra la riga vuota, la composizione non si ferma


def immagine_firma(contenuto: bytes | None) -> bytes | None:
    """La firma senza intestazione e ritagliata sul tratto; None se non c'e'."""
    if not contenuto:
        return None
    immagine = _senza_intestazione(contenuto)
    return _ritagliata(immagine) if estensione_immagine(immagine) else immagine
