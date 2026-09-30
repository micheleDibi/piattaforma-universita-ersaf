"""Processo breve di compilazione PDF: la memoria nativa termina con la richiesta.

Protocollo interno: opzioni JSON su stdin, PDF su stdout. I dati non passano
dagli argomenti di processo e gli errori non riportano il contenuto del modulo:
su stderr va solo una categoria, che `esecuzione.py` riporta nel log.
"""

import json
import sys

import typst

PREFISSO_ERRORE = "Composizione PDF non riuscita"


def causa(errore: BaseException) -> str:
    """La categoria dell'errore, mai il suo testo: Typst vi cita modulo e dati."""
    testo = str(errore)
    if "canonicalize path" in testo or "os error 2" in testo or "file not found" in testo:
        return "file mancante nella cache del modello"
    return type(errore).__name__


def main() -> None:
    try:
        opzioni = json.loads(sys.stdin.buffer.read())
        pdf = typst.compile(**opzioni)
        sys.stdout.buffer.write(pdf)
    except Exception as errore:
        sys.stderr.write(f"{PREFISSO_ERRORE}: {causa(errore)}\n")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
