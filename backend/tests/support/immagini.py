"""Immagini minime per i test, senza Pillow."""

from __future__ import annotations

import struct
import zlib


def png_pieno(larghezza: int = 60, altezza: int = 20, colore: tuple[int, int, int] = (20, 40, 90)) -> bytes:
    """Un PNG vero a tinta unita: basta a Typst per disegnare una firma."""
    def blocco(tipo: bytes, dati: bytes) -> bytes:
        return struct.pack(">I", len(dati)) + tipo + dati + struct.pack(">I", zlib.crc32(tipo + dati) & 0xFFFFFFFF)
    riga = b"\x00" + bytes(colore) * larghezza
    return (b"\x89PNG\r\n\x1a\n" + blocco(b"IHDR", struct.pack(">IIBBBBB", larghezza, altezza, 8, 2, 0, 0, 0))
            + blocco(b"IDAT", zlib.compress(riga * altezza)) + blocco(b"IEND", b""))
