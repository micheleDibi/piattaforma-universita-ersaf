"""Moduli a campi: dove scrivere sulle immagini delle pagine e con quale valore.

Le posizioni sono millimetri dall'angolo in alto a sinistra di un A4, misurati
sulle immagini a 150 dpi dei modelli. Ogni campo legge il suo valore da un
dizionario piatto ("residenza.cap", "sesso.m"): una chiave che manca e' un
errore di programmazione e fa fallire la composizione, non un campo vuoto.
Il disegno vero lo fa `modelli/_comune/impaginato.typ`.
"""

from __future__ import annotations

from dataclasses import dataclass

SINISTRA, CENTRO, DESTRA = "left", "center", "right"


def _testo(valori: dict, chiave: str) -> str:
    valore = valori[chiave]
    if not isinstance(valore, str):
        raise TypeError(f"il campo {chiave} vuole un testo, non {type(valore).__name__}")
    return valore


@dataclass(frozen=True)
class Testo:
    """Testo su una linea di scrittura che va da x0 a x1 alla quota y."""

    chiave: str
    x0: float
    x1: float
    y: float
    allinea: str = SINISTRA

    def campo(self, valori: dict) -> dict | None:
        testo = _testo(valori, self.chiave)
        if not testo:
            return None
        return {"tipo": "testo", "x0": self.x0, "x1": self.x1, "y": self.y, "allinea": self.allinea, "testo": testo}


@dataclass(frozen=True)
class Griglia:
    """Un carattere per casella, come nel riquadro del codice fiscale."""

    chiave: str
    x0: float
    x1: float
    y: float
    celle: int

    def campo(self, valori: dict) -> dict | None:
        testo = _testo(valori, self.chiave)
        if not testo:
            return None
        return {"tipo": "griglia", "x0": self.x0, "x1": self.x1, "y": self.y, "celle": self.celle, "testo": testo}


@dataclass(frozen=True)
class Casella:
    """Quadratino da barrare: angolo in alto a sinistra e lato."""

    chiave: str
    x: float
    y: float
    lato: float

    def campo(self, valori: dict) -> dict | None:
        barrata = valori[self.chiave]
        if not isinstance(barrata, bool):
            raise TypeError(f"la casella {self.chiave} vuole un booleano, non {type(barrata).__name__}")
        return {"tipo": "casella", "x": self.x, "y": self.y, "lato": self.lato} if barrata else None


@dataclass(frozen=True)
class Firma:
    """La firma della pratica sulla linea da x0 a x1: il modello la disegna solo se c'e'."""

    x0: float
    x1: float
    y: float
    altezza: float = 12.0

    def campo(self, valori: dict) -> dict:
        return {"tipo": "firma", "x0": self.x0, "x1": self.x1, "y": self.y, "altezza": self.altezza}


@dataclass(frozen=True)
class Pagina:
    """Un'immagine del modello e i campi da scriverci sopra."""

    sfondo: str
    campi: tuple[Testo | Griglia | Casella | Firma, ...] = ()


def impagina(pagine: tuple[Pagina, ...], valori: dict) -> list[dict]:
    """Le pagine come le legge il modello Typst, senza i campi vuoti."""
    return [
        {"sfondo": pagina.sfondo, "campi": [c for c in (campo.campo(valori) for campo in pagina.campi) if c]}
        for pagina in pagine
    ]


def data(chiave: str, y: float, giorno: tuple[float, float], mese: tuple[float, float],
         anno: tuple[float, float]) -> tuple[Testo, Testo, Testo]:
    """Una data scritta su tre linee: chiave.gg / chiave.mm / chiave.aaaa."""
    return (
        Testo(f"{chiave}.gg", *giorno, y, CENTRO),
        Testo(f"{chiave}.mm", *mese, y, CENTRO),
        Testo(f"{chiave}.aaaa", *anno, y, CENTRO),
    )


def luogo_data_firma(y: float, luogo: tuple[float, float], giorno: tuple[float, float],
                     firma: tuple[float, float], altezza: float = 12.0) -> tuple[Testo, Testo, Firma]:
    """La riga "Luogo ____, Data ____ Firma ____" in fondo alle pagine."""
    return (
        Testo("firma.luogo", *luogo, y),
        Testo("firma.data", *giorno, y, CENTRO),
        Firma(*firma, y, altezza),
    )
