"""Una compilazione PDF alla volta, in un processo isolato con durata limitata."""

import json
import subprocess
import sys
import threading
from pathlib import Path

DURATA_MASSIMA_SECONDI = 60
_blocco = threading.Lock()
_COMPILATORE = Path(__file__).with_name("compilatore.py")


def compila_pdf(opzioni: dict) -> bytes:
    """La chiusura del processo libera anche le cache native dei diversi modelli."""
    with _blocco:
        risultato = subprocess.run(
            [sys.executable, str(_COMPILATORE)],
            input=json.dumps(opzioni, ensure_ascii=False).encode("utf-8"),
            capture_output=True, check=True, timeout=DURATA_MASSIMA_SECONDI,
        )
    if not risultato.stdout.startswith(b"%PDF-"):
        raise ValueError("Il compilatore non ha prodotto un PDF.")
    return risultato.stdout
