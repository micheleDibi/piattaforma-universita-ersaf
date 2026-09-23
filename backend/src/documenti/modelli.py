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
from functools import partial
from dataclasses import dataclass, field
from typing import Callable

from src.documenti.dati import normalizza
from src.documenti.ecampus import laurea as ecampus_laurea
from src.documenti.ecampus.rateizzazione import pagine_rateizzazione
from src.documenti.moduli import compila
from src.pratiche.models import Pratica


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

    def compila(self, dati: dict) -> dict:
        """Modulo e allegati dell'ente, attraverso una sola pipeline di composizione."""
        documento = self.arricchisci(dati)
        if normalizza(self.ente) == normalizza(ECAMPUS):
            documento = {**documento, "pagine": [*documento["pagine"], *pagine_rateizzazione(dati)]}
        return documento


ECAMPUS = "Università Telematica eCampus"
SSML = "Scuola Superiore Universitaria di Mediazione Linguistica Lamezia Terme"
# Il primo nome e' quello realmente presente nel catalogo legacy.
LINK = ("Link Campus Univesity", "Link Campus University")


def _moduli(ente: str, associazioni: dict[str, tuple[str, ...]]) -> tuple[Modello, ...]:
    return tuple(Modello(nome, ente, tipo, partial(compila, nome))
                 for nome, tipi in associazioni.items() for tipo in tipi)


# Solo associazioni documentate. Percorso docenti e corsi speciali restano esclusi.
MODELLI: tuple[Modello, ...] = (
    Modello(ecampus_laurea.NOME, ECAMPUS, "Lauree", ecampus_laurea.arricchisci),
    *_moduli(ECAMPUS, {
        "ecampus-master": ("MASTER", "MASTER AREA SCUOLA", "MASTER CLASSI DI CONCORSO"),
        "ecampus-perfezionamento": ("CORSI DI PERFEZIONAMENTO",),
        "ecampus-formazione": ("CORSI DI FORMAZIONE", "CORSI DI ALTA FORMAZIONE"),
        "ecampus-singoli": ("CORSI SINGOLI",),
    }),
    *_moduli(SSML, {
        "ssml-laurea": ("LAUREE",), "ssml-master": ("MASTER",),
        "ssml-perfezionamento": ("CORSI DI PERFEZIONAMENTO",),
        "ssml-formazione": ("CORSI DI FORMAZIONE", "CORSI DI ALTA FORMAZIONE", "CORSI SPECIALI"),
        "ssml-singoli": ("CORSI SINGOLI",),
    }),
    *(m for ente in LINK for m in _moduli(ente, {
        "link-perfezionamento": ("CORSI DI PERFEZIONAMENTO",), "link-singoli": ("CORSI SINGOLI",),
    })),
    *_moduli("Avatar4University", {"a4u-perfezionamento": ("CORSI DI PERFEZIONAMENTO",)}),
)


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
