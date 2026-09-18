"""Genera le pagine di docs/tecnica/riferimenti/.

    python scripts/documentazione/genera.py              scrive le pagine
    python scripts/documentazione/genera.py --verifica   controlla senza scrivere

Esce con 0 se tutto è in ordine, 1 se con --verifica una pagina non
corrisponde al codice (va rilanciato senza --verifica e le pagine vanno
committate), 2 se un generatore non riesce o se le versioni delle librerie non
sono quelle di scripts/documentazione/vincoli.txt.

Servono le dipendenze del backend e degli strumenti:
    pip install -r backend/requirements.txt -r scripts/documentazione/requisiti.txt \
        -c scripts/documentazione/vincoli.txt
e quelle del frontend (`npm ci` in frontend/), per leggere le rotte.
"""

from __future__ import annotations

import argparse
import difflib
import importlib.metadata
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from comune import RADICE, leggi, normalizza, scrivi  # noqa: E402
from generatori import ErroreGeneratore, api, configurazione, migrazioni, rotte  # noqa: E402

CARTELLA_USCITA = Path("docs/tecnica/riferimenti")
GENERATORI = {
    "api.md": api.genera,
    "configurazione.md": configurazione.genera,
    "migrazioni.md": migrazioni.genera,
    "rotte-frontend.md": rotte.genera,
}
VINCOLI = Path(__file__).resolve().parent / "vincoli.txt"
RIGHE_DIFF = 200


def versioni_diverse(vincoli: Path = VINCOLI) -> list[str]:
    diverse = []
    for riga in leggi(vincoli).split("\n"):
        trovato = re.match(r"^([A-Za-z0-9_.-]+)==(\S+)$", riga.strip())
        if not trovato:
            continue
        nome, attesa = trovato.groups()
        try:
            installata = importlib.metadata.version(nome)
        except importlib.metadata.PackageNotFoundError:
            installata = "assente"
        if installata != attesa:
            diverse.append(f"{nome}: installata {installata}, attesa {attesa}")
    return diverse


def esegui(argomenti: list[str] | None = None, radice: Path = RADICE) -> int:
    parser = argparse.ArgumentParser(description="Genera docs/tecnica/riferimenti/")
    parser.add_argument("--verifica", action="store_true", help="non scrive: controlla che le pagine siano aggiornate")
    parser.add_argument("--uscita", type=Path, help="cartella delle pagine da scrivere o controllare")
    opzioni = parser.parse_args(argomenti)
    uscita = opzioni.uscita or (radice / CARTELLA_USCITA)

    diverse = versioni_diverse()
    if diverse:
        print("ERRORE: le versioni installate non sono quelle con cui si generano le pagine:")
        for riga in diverse:
            print(f"  - {riga}")
        print("Installa: pip install -r backend/requirements.txt -r scripts/documentazione/requisiti.txt "
              "-c scripts/documentazione/vincoli.txt")
        return 2

    pagine = {}
    for nome, genera in GENERATORI.items():
        try:
            pagine[nome] = genera(radice)
        except ErroreGeneratore as errore:
            print(f"ERRORE nel generare {nome}: {errore}")
            return 2

    if not opzioni.verifica:
        for nome, testo in pagine.items():
            scrivi(uscita / nome, testo)
            print(f"scritto {uscita / nome}")
        return 0

    esito = 0
    for nome, atteso in pagine.items():
        percorso = uscita / nome
        attuale = normalizza(leggi(percorso)) if percorso.is_file() else ""
        if attuale == atteso:
            continue
        esito = 1
        print(f"ERRORE: {percorso} non corrisponde al codice. Rigenera con "
              "`python scripts/documentazione/genera.py` e committa il risultato.")
        diff = list(difflib.unified_diff(attuale.splitlines(), atteso.splitlines(),
                                         f"{nome} (nel repository)", f"{nome} (dal codice)", lineterm=""))
        for riga in diff[:RIGHE_DIFF]:
            print(riga)
        if len(diff) > RIGHE_DIFF:
            print(f"... altre {len(diff) - RIGHE_DIFF} righe di differenze")
    if esito == 0:
        print("Pagine generate aggiornate.")
    return esito


if __name__ == "__main__":
    sys.exit(esegui())
