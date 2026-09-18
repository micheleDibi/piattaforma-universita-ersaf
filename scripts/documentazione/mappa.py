"""Lettura e validazione di docs/mappa-documentazione.yml.

Unico modulo degli strumenti che importa PyYAML: il timbro non ne ha bisogno.
"""

from __future__ import annotations

from dataclasses import dataclass

import yaml

from comune import corrisponde, leggi, traduci_glob

PERCORSO = "docs/mappa-documentazione.yml"


@dataclass(frozen=True)
class Regola:
    nome: str
    percorsi: tuple[str, ...]
    documenti: tuple[str, ...]

    def toccati(self, cambiati: list[str]) -> list[str]:
        return sorted(p for p in cambiati if any(corrisponde(p, g) for g in self.percorsi))


class MappaNonValida(ValueError):
    def __init__(self, errori: list[str]):
        self.errori = errori
        super().__init__("; ".join(errori))


def _lista_di_stringhe(valore, campo: str, nome: str, errori: list[str]) -> tuple[str, ...]:
    if not isinstance(valore, list) or not valore or not all(isinstance(v, str) and v for v in valore):
        errori.append(f"regola '{nome}': '{campo}' deve essere una lista non vuota di stringhe")
        return ()
    return tuple(valore)


def analizza(testo: str) -> list[Regola]:
    try:
        dati = yaml.safe_load(testo)
    except yaml.YAMLError as errore:
        raise MappaNonValida([f"YAML non valido: {errore}"]) from errore
    errori: list[str] = []
    if not isinstance(dati, dict) or set(dati) != {"regole"} or not isinstance(dati["regole"], list):
        raise MappaNonValida(["il file deve contenere solo la chiave 'regole' con una lista"])
    regole = []
    nomi = set()
    for posizione, grezza in enumerate(dati["regole"], start=1):
        if not isinstance(grezza, dict) or set(grezza) != {"nome", "percorsi", "documenti"}:
            errori.append(f"regola {posizione}: servono esattamente le chiavi nome, percorsi, documenti")
            continue
        nome = grezza["nome"]
        if not isinstance(nome, str) or not nome.strip():
            errori.append(f"regola {posizione}: nome mancante")
            continue
        if nome in nomi:
            errori.append(f"regola '{nome}': nome ripetuto")
        nomi.add(nome)
        percorsi = _lista_di_stringhe(grezza["percorsi"], "percorsi", nome, errori)
        documenti = _lista_di_stringhe(grezza["documenti"], "documenti", nome, errori)
        for pattern in percorsi:
            try:
                traduci_glob(pattern)
            except ValueError as errore:
                errori.append(f"regola '{nome}': {errore}")
        for documento in documenti:
            if not documento.startswith("docs/") or not documento.endswith(".md"):
                errori.append(f"regola '{nome}': il documento {documento} deve essere un .md sotto docs/")
            elif documento.startswith("docs/tecnica/riferimenti/"):
                errori.append(f"regola '{nome}': {documento} è generato e non conta come documento collegato")
        regole.append(Regola(nome, percorsi, documenti))
    if errori:
        raise MappaNonValida(errori)
    return regole


def carica(radice) -> list[Regola]:
    return analizza(leggi(f"{radice}/{PERCORSO}"))


def errori_rispetto_ai_file(regole: list[Regola], file: list[str]) -> list[str]:
    """Documenti inesistenti e pattern che non trovano più nulla."""
    presenti = set(file)
    errori = []
    for regola in regole:
        for documento in regola.documenti:
            if documento not in presenti:
                errori.append(f"regola '{regola.nome}': il documento {documento} non esiste")
        for pattern in regola.percorsi:
            if not any(corrisponde(f, pattern) for f in file):
                errori.append(f"regola '{regola.nome}': il pattern {pattern} non trova nessun file")
    return errori
