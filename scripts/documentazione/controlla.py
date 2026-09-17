"""Controlli della documentazione, in CI e in locale.

    python scripts/documentazione/controlla.py frammenti
    python scripts/documentazione/controlla.py link
    python scripts/documentazione/controlla.py mappa
    python scripts/documentazione/controlla.py pr --base <sha> [--head HEAD] [--etichette a,b]
    python scripts/documentazione/controlla.py tutto [--base <sha>] [--etichette a,b]

Esce con 0 se tutto è in ordine, 1 se un controllo fallisce, 2 per un errore
d'uso. Il significato dei controlli e delle etichette di esenzione è spiegato
in docs/tecnica/documentazione.md.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

from comune import (  # noqa: E402
    RADICE, ErroreGit, ancore, elenco_file, git, git_bytes, git_riuscito, leggi, risolvi,
    righe_fuori_dal_codice, segnala,
)
import frammenti  # noqa: E402

ETICHETTA_SENZA_CHANGELOG = "senza-changelog"
ETICHETTA_DOCUMENTAZIONE_INVARIATA = "documentazione-invariata"
# Le cartelle il cui cambiamento richiede un frammento (esclusi i .md).
RICHIEDONO_FRAMMENTO = ("backend/src/", "frontend/src/", "db/", "deploy/")
CHANGELOG = "CHANGELOG.md"


@dataclass(frozen=True)
class Errore:
    messaggio: str
    file: str | None = None
    riga: int | None = None
    titolo: str | None = None


# =============================================================================
# Frammenti
# =============================================================================
def controlla_frammenti(radice, file: list[str]) -> list[Errore]:
    errori = []
    for percorso in file:
        if not frammenti.e_frammento(percorso):
            if percorso.startswith(frammenti.CARTELLA + "/") and posixpath.basename(percorso) not in frammenti.ESCLUSI:
                errori.append(Errore("nella cartella dei frammenti sono ammessi solo file .md",
                                     percorso, titolo="Frammento non valido"))
            continue
        try:
            frammenti.analizza(posixpath.basename(percorso), leggi(Path(radice) / percorso))
        except frammenti.FrammentoNonValido as errore:
            for dettaglio in errore.errori:
                errori.append(Errore(dettaglio, percorso, titolo="Frammento non valido"))
    return errori


# =============================================================================
# Link
# =============================================================================
_CODICE_IN_LINEA = re.compile(r"(`+)(?:(?!\1).)+\1")
_LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'(][^)]*)?\)")
_RIFERIMENTO = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)")
_SCHEMA = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_RIGA_CODICE = re.compile(r"^L\d+(?:-L?\d+)?$")


def _destinazioni(testo: str):
    for numero, riga in righe_fuori_dal_codice(testo):
        pulita = _CODICE_IN_LINEA.sub("", riga)
        for destinazione in _LINK.findall(pulita):
            yield numero, destinazione
        riferimento = _RIFERIMENTO.match(pulita)
        if riferimento:
            yield numero, riferimento.group(1)


def controlla_link(radice, file: list[str]) -> list[Errore]:
    presenti = set(file)
    cartelle = {posixpath.dirname(f) for f in file}
    for cartella in list(cartelle):
        while cartella:
            cartella = posixpath.dirname(cartella)
            cartelle.add(cartella)
    cache_ancore: dict[str, set[str]] = {}

    def ancore_di(percorso: str) -> set[str]:
        if percorso not in cache_ancore:
            cache_ancore[percorso] = ancore(leggi(Path(radice) / percorso))
        return cache_ancore[percorso]

    errori = []
    for percorso in file:
        if not percorso.endswith(".md") or "node_modules/" in percorso:
            continue
        for numero, destinazione in _destinazioni(leggi(Path(radice) / percorso)):
            if _SCHEMA.match(destinazione):
                continue
            parte, _, ancora = destinazione.partition("#")
            parte = unquote(parte)
            ancora = unquote(ancora)
            if not parte:
                bersaglio = percorso
            else:
                bersaglio = risolvi(percorso, parte.rstrip("/"))
                if bersaglio is None:
                    errori.append(Errore(f"il link {destinazione} esce dal repository", percorso, numero,
                                         "Link rotto"))
                    continue
                if bersaglio not in presenti and bersaglio not in cartelle:
                    errori.append(Errore(f"il link {destinazione} punta a un file inesistente ({bersaglio})",
                                         percorso, numero, "Link rotto"))
                    continue
            if not ancora:
                continue
            if not bersaglio.endswith(".md"):
                if not _RIGA_CODICE.match(ancora):
                    errori.append(Errore(f"ancora #{ancora} su un file che non è Markdown", percorso, numero,
                                         "Link rotto"))
                continue
            if ancora not in ancore_di(bersaglio):
                errori.append(Errore(f"l'ancora #{ancora} non esiste in {bersaglio}", percorso, numero,
                                     "Ancora rotta"))
    return errori


# =============================================================================
# Mappa
# =============================================================================
def controlla_mappa(radice, file: list[str]) -> list[Errore]:
    import mappa

    try:
        regole = mappa.carica(radice)
    except FileNotFoundError:
        return [Errore("manca la mappa della documentazione", mappa.PERCORSO, titolo="Mappa")]
    except mappa.MappaNonValida as errore:
        return [Errore(e, mappa.PERCORSO, titolo="Mappa non valida") for e in errore.errori]
    return [Errore(e, mappa.PERCORSO, titolo="Mappa non aggiornata")
            for e in mappa.errori_rispetto_ai_file(regole, file)]


# =============================================================================
# Pull request
# =============================================================================
@dataclass(frozen=True)
class Modifica:
    stato: str          # A, M, D, R, T, ...
    percorso: str       # percorso finale (per D: quello cancellato)
    origine: str | None  # percorso di partenza delle rinomine

    @property
    def percorsi(self) -> tuple[str, ...]:
        return (self.percorso,) if self.origine is None else (self.origine, self.percorso)


def modifiche(radice, base: str, head: str) -> list[Modifica]:
    grezzo = git_bytes("diff", "-z", "--name-status", "-M", f"{base}...{head}", cwd=radice)
    campi = [c.decode("utf-8") for c in grezzo.split(b"\0")]
    if campi and campi[-1] == "":
        campi.pop()
    risultato = []
    i = 0
    while i < len(campi):
        stato = campi[i][0]
        if stato in "RC":
            risultato.append(Modifica(stato, campi[i + 2], campi[i + 1]))
            i += 3
        else:
            risultato.append(Modifica(stato, campi[i + 1], None))
            i += 2
    return risultato


def base_effettiva(radice, base: str, head: str) -> str:
    """Sul commit di merge di una PR il primo genitore e' il main su cui si
    unisce: confrontare con quello evita di attribuire alla PR i commit
    arrivati su main dopo l'evento (per esempio i timbri del changelog)."""
    genitori = git("rev-list", "--parents", "-n", "1", head, cwd=radice).split()
    return genitori[1] if len(genitori) == 3 else base


def _frammento_valido_in(radice, head: str, percorso: str) -> bool:
    try:
        testo = git("show", f"{head}:{percorso}", cwd=radice)
        frammenti.analizza(posixpath.basename(percorso), testo)
    except (ErroreGit, frammenti.FrammentoNonValido):
        return False
    return True


def controlla_pr(radice, base: str, head: str, etichette: set[str]) -> list[Errore]:
    import mappa

    elenco = modifiche(radice, base, head)
    tutti = sorted({p for m in elenco for p in m.percorsi})
    errori = []

    # Il registro lo scrive solo il timbro al deploy.
    for m in elenco:
        if CHANGELOG in m.percorsi and not (
            m.stato == "A" and not git_riuscito("cat-file", "-e", f"{base}:{CHANGELOG}", cwd=radice)
        ):
            errori.append(Errore("CHANGELOG.md si aggiorna solo al deploy, con il timbro: la PR non deve "
                                 "modificarlo. Scrivi un frammento in changelog/non-pubblicato/.",
                                 CHANGELOG, titolo="CHANGELOG modificato"))
        # Una rinomina toglie il frammento di partenza: per il timbro è una cancellazione.
        tolto = m.percorso if m.stato == "D" else (m.origine if m.stato == "R" else None)
        if tolto and frammenti.e_frammento(tolto):
            errori.append(Errore("la PR cancella o rinomina un frammento non ancora pubblicato: lo toglie "
                                 "solo il timbro al deploy", tolto, titolo="Frammento cancellato"))

    # Frammento obbligatorio.
    sorgenti = [p for p in tutti if p.startswith(RICHIEDONO_FRAMMENTO) and not p.endswith(".md")]
    if sorgenti and ETICHETTA_SENZA_CHANGELOG not in etichette:
        validi = [m.percorso for m in elenco
                  if m.stato in "AM" and frammenti.e_frammento(m.percorso)
                  and _frammento_valido_in(radice, head, m.percorso)]
        if not validi:
            esempi = ", ".join(sorgenti[:5]) + (" e altri" if len(sorgenti) > 5 else "")
            errori.append(Errore(
                "la PR modifica il codice (" + esempi + ") ma non aggiunge un frammento valido in "
                "changelog/non-pubblicato/ (formato in changelog/MODELLO.md). Se la modifica non "
                f"va raccontata, usa l'etichetta '{ETICHETTA_SENZA_CHANGELOG}'.",
                titolo="Frammento di changelog mancante"))

    # Documenti collegati.
    if ETICHETTA_DOCUMENTAZIONE_INVARIATA not in etichette:
        try:
            regole = mappa.carica(radice)
        except (FileNotFoundError, mappa.MappaNonValida):
            regole = []  # lo segnala il controllo della mappa
        candidati = [p for p in tutti if not p.startswith("docs/") and p != CHANGELOG]
        cambiati = set(tutti)
        for regola in regole:
            toccati = regola.toccati(candidati)
            if toccati and not cambiati.intersection(regola.documenti):
                errori.append(Errore(
                    f"la PR tocca {', '.join(toccati[:5])}{' e altri' if len(toccati) > 5 else ''} "
                    f"(regola '{regola.nome}') ma nessuno dei documenti collegati: controlla "
                    f"{', '.join(regola.documenti)}. Se non c'è nulla da aggiornare, usa l'etichetta "
                    f"'{ETICHETTA_DOCUMENTAZIONE_INVARIATA}'.",
                    titolo="Documentazione da controllare"))
    return errori


# =============================================================================
# Riga di comando
# =============================================================================
def _etichette(valore: str | None) -> set[str]:
    return {e.strip() for e in (valore or "").split(",") if e.strip()}


def esegui(argomenti: list[str] | None = None, radice=RADICE) -> int:
    parser = argparse.ArgumentParser(description="Controlli della documentazione")
    sotto = parser.add_subparsers(dest="comando", required=True)
    for nome in ("frammenti", "link", "mappa"):
        sotto.add_parser(nome)
    for nome in ("pr", "tutto"):
        p = sotto.add_parser(nome)
        p.add_argument("--base", required=(nome == "pr"), help="commit di base della PR")
        p.add_argument("--head", default="HEAD", help="commit finale (predefinito HEAD)")
        p.add_argument("--etichette", default="", help="etichette della PR, separate da virgole")
        p.add_argument("--merge", action="store_true",
                       help="se --head e' un commit di merge (come in GitHub Actions), usa il suo primo "
                            "genitore come base: esclude i commit arrivati su main dopo --base")
    opzioni = parser.parse_args(argomenti)

    try:
        file = elenco_file(radice)
        errori: list[Errore] = []
        if opzioni.comando in ("frammenti", "tutto"):
            errori += controlla_frammenti(radice, file)
        if opzioni.comando in ("link", "tutto"):
            errori += controlla_link(radice, file)
        if opzioni.comando in ("mappa", "tutto"):
            errori += controlla_mappa(radice, file)
        if opzioni.comando == "pr" or (opzioni.comando == "tutto" and opzioni.base):
            base = base_effettiva(radice, opzioni.base, opzioni.head) if opzioni.merge else opzioni.base
            errori += controlla_pr(radice, base, opzioni.head, _etichette(opzioni.etichette))
    except ErroreGit as errore:
        segnala(f"comando git non riuscito: {errore}", titolo="Errore interno")
        return 2

    for errore in errori:
        segnala(errore.messaggio, errore.file, errore.riga, errore.titolo)
    if errori:
        print(f"{len(errori)} problemi trovati.")
        return 1
    print("Documentazione in ordine.")
    return 0


if __name__ == "__main__":
    sys.exit(esegui())
