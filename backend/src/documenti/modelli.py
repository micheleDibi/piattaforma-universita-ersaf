"""Quale modello di stampa usa una pratica.

Ogni ente (eCampus, Link Campus, ...) e ogni tipo di corso ha il suo modulo.
La corrispondenza passa dalle descrizioni del listino confrontate in forma
normalizzata ("Corsi di Laurea", "CORSI DI LAUREA" e "corsi-di-laurea" sono
la stessa cosa), perche' gli id delle tabelle di decodifica non sono garantiti
uguali tra il gestionale e i suoi cloni. Una pratica senza modello non ha il
documento: il frontend nasconde il pulsante.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable

from src.pratiche.models import Pratica


def normalizza(valore) -> str:
    """Minuscole, senza accenti, spazi e punteggiatura: 'Carta d'Identità' -> 'cartadidentita'."""
    if valore is None:
        return ""
    scomposto = unicodedata.normalize("NFKD", str(valore))
    senza_accenti = "".join(c for c in scomposto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", senza_accenti.casefold())


def _identita(dati: dict) -> dict:
    return dati


@dataclass(frozen=True)
class Modello:
    """Un modulo stampabile: cartella in `modelli/`, ente e tipo di corso a cui si applica."""

    nome: str
    ente: str
    tipo_corso: str
    # Aggiunge ai dati comuni le scelte proprie del modulo (crocette, campi nascosti).
    arricchisci: Callable[[dict], dict] = field(default=_identita, compare=False)

    def si_applica(self, ente: str, tipo_corso: str) -> bool:
        return normalizza(self.ente) == normalizza(ente) and normalizza(self.tipo_corso) == normalizza(tipo_corso)


# I moduli si aggiungono qui man mano che vengono calibrati sulle immagini.
MODELLI: tuple[Modello, ...] = ()


def modello_per(pratica: Pratica, modelli: tuple[Modello, ...] | None = None) -> Modello | None:
    listino = pratica.listino_testa
    ente = getattr(getattr(listino, "universita", None), "nome_universita_descrizione", None)
    tipo_corso = getattr(getattr(listino, "tipo_corso", None), "listino_tipoCorso_descrizione", None)
    if not ente or not tipo_corso:
        return None
    return next((m for m in (MODELLI if modelli is None else modelli) if m.si_applica(ente, tipo_corso)), None)


def nome_file(pratica: Pratica) -> str:
    """pratica-000045.pdf; solo caratteri sicuri in un nome di file e in un header."""
    identificativo = re.sub(r"[^A-Za-z0-9_-]+", "-", str(pratica.pratica_numero or "")).strip("-")
    return f"pratica-{identificativo or pratica.pratica_id}.pdf"
