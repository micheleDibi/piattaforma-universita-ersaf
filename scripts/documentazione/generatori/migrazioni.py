"""docs/tecnica/riferimenti/migrazioni.md da db/migrations e db/rollback."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from comune import leggi, redigi
from generatori import cella, intestazione

_NOME = re.compile(r"^(\d{3})_([a-z0-9_]+)\.sql$")
_TITOLO_NUMERATO = re.compile(r"^--\s*(\d{3})\s*-\s*(.+?)\s*$")
_SEPARATORE = re.compile(r"^--\s*[=\-]{5,}\s*$")


@dataclass(frozen=True)
class Migrazione:
    numero: int
    nome: str
    descrizione: str
    numerata: bool
    rollback: str | None      # nome del file di rollback, se c'è
    rollback_regolare: bool   # nome con il suffisso _down


def descrizione(testo: str) -> tuple[str, bool]:
    """Titolo dall'intestazione: `-- NNN - Titolo` se c'è, altrimenti la prima
    riga di commento. Il secondo valore dice se l'intestazione è numerata."""
    primo_commento = None
    for riga in testo.split("\n"):
        if not riga.startswith("--"):
            break
        if _SEPARATORE.match(riga):
            continue
        numerato = _TITOLO_NUMERATO.match(riga)
        if numerato:
            return numerato.group(2).rstrip("."), True
        if primo_commento is None and riga[2:].strip():
            primo_commento = riga[2:].strip()
    return (primo_commento or "").rstrip("."), False


def leggi_migrazioni(radice: Path) -> tuple[list[Migrazione], list[str]]:
    cartella = radice / "db" / "migrations"
    rollback = {p.name for p in (radice / "db" / "rollback").glob("*.sql")}
    migrazioni, anomalie = [], []
    usati = set()
    for percorso in sorted(cartella.glob("*.sql")):
        trovato = _NOME.match(percorso.name)
        if not trovato:
            anomalie.append(f"`db/migrations/{percorso.name}`: nome fuori dallo schema `NNN_nome.sql`.")
            continue
        numero, nome = int(trovato.group(1)), trovato.group(2)
        testo, numerata = descrizione(leggi(percorso))
        regolare = f"{percorso.stem}_down.sql"
        if regolare in rollback:
            file_rollback, ok = regolare, True
        elif percorso.name in rollback:
            file_rollback, ok = percorso.name, False
        else:
            file_rollback, ok = None, False
        if file_rollback:
            usati.add(file_rollback)
        migrazioni.append(Migrazione(numero, nome, redigi(testo), numerata, file_rollback, ok))

    numeri = [m.numero for m in migrazioni]
    if numeri:
        for mancante in sorted(set(range(1, max(numeri) + 1)) - set(numeri)):
            anomalie.append(f"Il numero {mancante:03d} non è usato.")
    for m in migrazioni:
        codice = f"{m.numero:03d}"
        if m.rollback is None:
            anomalie.append(f"La {codice} non ha un file di rollback.")
        elif not m.rollback_regolare:
            anomalie.append(f"Il rollback della {codice} si chiama `{m.rollback}`, senza il suffisso `_down`.")
        if not m.numerata:
            anomalie.append(f"L'intestazione della {codice} non riporta il numero.")
    for orfano in sorted(rollback - usati):
        anomalie.append(f"`db/rollback/{orfano}` non corrisponde a nessuna migrazione.")
    return migrazioni, anomalie


def componi(migrazioni: list[Migrazione], anomalie: list[str]) -> str:
    righe = [intestazione("Migrazioni del database", "`db/migrations/` e `db/rollback/`").rstrip(), ""]
    righe += [
        "Le regole per applicarle, annullarle e correggere gli errori sono in "
        "[db/README.md](../../../db/README.md); il contesto in "
        "[database e migrazioni](../database-e-migrazioni.md).",
        "",
        "| Numero | File | Descrizione | Rollback |",
        "|---|---|---|---|",
    ]
    for m in migrazioni:
        if m.rollback is None:
            stato = "assente"
        elif m.rollback_regolare:
            stato = f"`{m.rollback}`"
        else:
            stato = f"`{m.rollback}` (nome irregolare)"
        righe.append(f"| {m.numero:03d} | `{m.numero:03d}_{m.nome}.sql` | {cella(m.descrizione)} | {stato} |")
    righe += ["", "## Anomalie", ""]
    righe += [f"- {a}" for a in anomalie] if anomalie else ["Nessuna."]
    return "\n".join(righe).rstrip() + "\n"


def genera(radice: Path) -> str:
    return componi(*leggi_migrazioni(radice))
