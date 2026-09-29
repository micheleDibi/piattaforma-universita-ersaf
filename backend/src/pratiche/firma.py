"""Acquisizione della firma: PNG normalizzato, limite risorse e versione ottimistica."""

import base64
import binascii
import hashlib
import io
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import HTTPException

from src.documenti.firma import immagine_firma

MAX_BYTE = 350_000
MAX_LATO = 2048
MAX_PIXEL = 2_097_152
PREFISSO = "data:image/png;base64,"


def versione_firma(contenuto):
    return hashlib.sha256(contenuto or b"").hexdigest()


def stato_firma(contenuto):
    png = immagine_firma(contenuto) if contenuto else None
    if png:
        try:
            with Image.open(io.BytesIO(png)) as immagine:
                risultato = io.BytesIO()
                immagine.save(risultato, "PNG")
                png = risultato.getvalue()
        except (OSError, ValueError, Image.DecompressionBombError):
            png = None
    return {
        "presente": bool(contenuto),
        "versione": versione_firma(contenuto),
        "immagine": PREFISSO + base64.b64encode(png).decode("ascii") if png else None,
    }


def normalizza_firma(valore):
    try:
        if not valore.startswith(PREFISSO):
            raise ValueError()
        dati = base64.b64decode(valore[len(PREFISSO):], validate=True)
        if len(dati) > MAX_BYTE:
            raise ValueError()
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(dati)) as sorgente:
                if (sorgente.format != "PNG" or getattr(sorgente, "n_frames", 1) != 1
                        or max(sorgente.size) > MAX_LATO or sorgente.width * sorgente.height > MAX_PIXEL):
                    raise ValueError()
                rgba = sorgente.convert("RGBA")
                tela = Image.new("RGBA", rgba.size, "white")
                tela.alpha_composite(rgba)
                grigi = tela.convert("L")
                tratto = ImageOps.invert(grigi).point(lambda v: 255 if v > 48 else 0)
                area = tratto.getbbox()
                if area is None or area[2] - area[0] < 12 or area[3] - area[1] < 4:
                    raise ValueError()
                risultato = io.BytesIO()
                grigi.save(risultato, format="PNG")
                return risultato.getvalue()
    except (ValueError, binascii.Error, OSError, UnidentifiedImageError,
            Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(422, "Disegna una firma valida nell'area indicata.") from None
