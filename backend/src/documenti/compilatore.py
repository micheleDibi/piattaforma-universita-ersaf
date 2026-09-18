"""Processo breve di compilazione PDF: la memoria nativa termina con la richiesta.

Protocollo interno: opzioni JSON su stdin, PDF su stdout. I dati non passano
dagli argomenti di processo e gli errori non riportano il contenuto del modulo.
"""

import json
import sys

import typst


def main() -> None:
    try:
        opzioni = json.loads(sys.stdin.buffer.read())
        pdf = typst.compile(**opzioni)
        sys.stdout.buffer.write(pdf)
    except Exception:
        sys.stderr.write("Composizione PDF non riuscita.\n")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
