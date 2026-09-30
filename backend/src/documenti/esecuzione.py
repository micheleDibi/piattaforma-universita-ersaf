"""Una compilazione PDF alla volta, in un processo isolato con durata limitata."""

import json
import logging
import re
import subprocess
import sys
import threading
from pathlib import Path

from src.documenti.compilatore import PREFISSO_ERRORE

DURATA_MASSIMA_SECONDI = 60
_blocco = threading.Lock()
_COMPILATORE = Path(__file__).with_name("compilatore.py")
# La riga che il compilatore scrive su stderr quando fallisce; il resto non si registra.
_RIGA_CAUSA = re.compile(rf"^{re.escape(PREFISSO_ERRORE)}: ([A-Za-z][A-Za-z ._]{{0,60}})$")
logger = logging.getLogger("ersaf.documenti")


def causa_dal_compilatore(stderr: bytes | None) -> str:
    """La categoria scritta dal compilatore; qualunque altro testo resta fuori dal log."""
    for riga in reversed((stderr or b"").decode("utf-8", "replace").splitlines()):
        trovata = _RIGA_CAUSA.match(riga.strip())
        if trovata:
            return trovata.group(1)
    return "causa non riconosciuta"


def compila_pdf(opzioni: dict) -> bytes:
    """La chiusura del processo libera anche le cache native dei diversi modelli."""
    with _blocco:
        try:
            risultato = subprocess.run(
                [sys.executable, str(_COMPILATORE)],
                input=json.dumps(opzioni, ensure_ascii=False).encode("utf-8"),
                capture_output=True, check=True, timeout=DURATA_MASSIMA_SECONDI,
            )
        except subprocess.CalledProcessError as errore:
            logger.warning("compilatore PDF terminato con codice %s: %s",
                           errore.returncode, causa_dal_compilatore(errore.stderr))
            raise
        except subprocess.TimeoutExpired:
            logger.warning("compilatore PDF fermato dopo %s secondi", DURATA_MASSIMA_SECONDI)
            raise
    if not risultato.stdout.startswith(b"%PDF-"):
        logger.warning("compilatore PDF terminato senza produrre un PDF")
        raise ValueError("Il compilatore non ha prodotto un PDF.")
    return risultato.stdout
