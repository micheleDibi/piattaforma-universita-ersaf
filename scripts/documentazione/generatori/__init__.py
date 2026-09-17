"""Generatori delle pagine in docs/tecnica/riferimenti/."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent


class ErroreGeneratore(RuntimeError):
    """Il generatore non può produrre un risultato affidabile."""


def intestazione(titolo: str, fonti: str) -> str:
    return (
        f"# {titolo}\n\n"
        f"> Pagina generata da `python scripts/documentazione/genera.py` a partire da {fonti}.\n"
        "> Non modificarla a mano: rilancia il comando dopo aver cambiato le fonti.\n\n"
    )


def ambiente_pulito() -> dict[str, str]:
    """Solo quello che serve a far partire Python o Node: niente variabili
    dell'applicazione ereditate dalla shell (per esempio TEST_DATABASE_URL)."""
    ambiente = {k: os.environ[k] for k in ("PATH", "SYSTEMROOT", "TEMP", "TMP", "USERPROFILE", "HOME")
                if k in os.environ}
    ambiente.update(PYTHONUTF8="1", PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1", LC_ALL="C.UTF-8")
    return ambiente


def esegui_json(comando: list[str], cwd: Path) -> dict:
    try:
        esito = subprocess.run(comando, cwd=str(cwd), env=ambiente_pulito(), capture_output=True,
                               encoding="utf-8", timeout=300)
    except FileNotFoundError as errore:
        raise ErroreGeneratore(f"comando non trovato: {comando[0]}") from errore
    if esito.returncode != 0:
        raise ErroreGeneratore(f"{' '.join(comando[:2])} terminato con {esito.returncode}:\n{esito.stderr.strip()}")
    try:
        return json.loads(esito.stdout)
    except json.JSONDecodeError as errore:
        raise ErroreGeneratore(f"uscita non valida da {comando[1]}: {esito.stdout[:200]}") from errore


def python_backend(script: str, radice: Path) -> dict:
    return esegui_json([sys.executable, str(CARTELLA / script), str(radice / "backend")], radice / "backend")


def cella(testo: str) -> str:
    """Testo sicuro dentro una cella di tabella Markdown."""
    return " ".join(str(testo).split()).replace("|", "\\|")
