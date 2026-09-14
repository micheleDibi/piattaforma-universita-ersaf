"""Pacchettizza il logo canonico frontend per il contesto Docker del backend."""

import argparse
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
ORIGINE = RADICE / "frontend/src/assets/pratiche-universita.png"
DESTINAZIONE = RADICE / "backend/src/notifiche/assets/pratiche-universita.png"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    opzioni = parser.parse_args()
    if opzioni.check:
        if not DESTINAZIONE.is_file() or DESTINAZIONE.read_bytes() != ORIGINE.read_bytes():
            raise SystemExit("Logo email non allineato: eseguire scripts/sync-email-logo.py")
    else:
        DESTINAZIONE.parent.mkdir(parents=True, exist_ok=True)
        DESTINAZIONE.write_bytes(ORIGINE.read_bytes())
