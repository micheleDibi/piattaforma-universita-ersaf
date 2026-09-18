"""Funzioni comuni agli strumenti della documentazione.

Solo libreria standard e sintassi compatibile con Python 3.10: questo modulo
lo importa anche timbra_changelog.py, che gira sul PC di chi pubblica senza
dipendenze installate.
"""

from __future__ import annotations

import os
import posixpath
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]

# Nessuna richiesta interattiva di credenziali: un push che chiede la password
# deve fallire subito, non bloccare deploy.ps1.
AMBIENTE_GIT = {
    "GIT_TERMINAL_PROMPT": "0",
    "GCM_INTERACTIVE": "never",
    "GIT_SSH_COMMAND": "ssh -o BatchMode=yes",
    "LC_ALL": "C",
}


class ErroreGit(RuntimeError):
    def __init__(self, argomenti, codice, uscita, errori):
        self.argomenti = argomenti
        self.codice = codice
        self.uscita = uscita
        self.errori = errori
        super().__init__(f"git {' '.join(argomenti)} -> {codice}: {errori.strip()}")


def git_bytes(*argomenti, cwd=RADICE, controlla=True, timeout=None, ambiente=None) -> bytes:
    env = dict(os.environ)
    env.update(AMBIENTE_GIT)
    if ambiente:
        env.update(ambiente)
    try:
        esito = subprocess.run(
            ["git", *argomenti], cwd=str(cwd), env=env, capture_output=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise ErroreGit(argomenti, -1, "", f"nessuna risposta entro {timeout} secondi") from None
    if controlla and esito.returncode != 0:
        raise ErroreGit(argomenti, esito.returncode, esito.stdout.decode("utf-8", "replace"),
                        esito.stderr.decode("utf-8", "replace"))
    return esito.stdout


def git(*argomenti, cwd=RADICE, controlla=True, timeout=None, ambiente=None) -> str:
    return git_bytes(*argomenti, cwd=cwd, controlla=controlla, timeout=timeout,
                     ambiente=ambiente).decode("utf-8")


def git_riuscito(*argomenti, cwd=RADICE) -> bool:
    try:
        git_bytes(*argomenti, cwd=cwd)
    except ErroreGit:
        return False
    return True


def elenco_file(radice=RADICE) -> list[str]:
    """File del repository come li vede git (maiuscole comprese): tracciati più
    quelli nuovi non ignorati, esclusi quelli cancellati dal disco."""
    grezzo = git_bytes("ls-files", "-z", "--cached", "--others", "--exclude-standard", cwd=radice)
    nomi = {n.decode("utf-8") for n in grezzo.split(b"\0") if n}
    return sorted(n for n in nomi if (Path(radice) / n).is_file())


def leggi(percorso) -> str:
    with open(percorso, encoding="utf-8", newline="") as f:
        testo = f.read()
    return normalizza(testo)


def scrivi(percorso, testo: str) -> None:
    Path(percorso).parent.mkdir(parents=True, exist_ok=True)
    with open(percorso, "w", encoding="utf-8", newline="\n") as f:
        f.write(testo)


def normalizza(testo: str) -> str:
    """LF e niente BOM: i checkout Windows con autocrlf non devono contare."""
    if testo.startswith("\ufeff"):
        testo = testo[1:]
    return testo.replace("\r\n", "\n").replace("\r", "\n")


# =============================================================================
# Glob
# =============================================================================
def traduci_glob(pattern: str) -> re.Pattern:
    """`*` e `?` non attraversano `/`; `**` sì, e `**/` vale anche zero
    cartelle. Nessuna graffa: la mappa usa liste di pattern."""
    if any(c in pattern for c in "{}[]"):
        raise ValueError(f"pattern non ammesso (graffe o parentesi): {pattern}")
    regex = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            regex.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            regex.append(".*")
            i += 2
        elif pattern[i] == "*":
            regex.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            regex.append("[^/]")
            i += 1
        else:
            regex.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(regex) + r"\Z")


def corrisponde(percorso: str, pattern: str) -> bool:
    return traduci_glob(pattern).match(percorso) is not None


# =============================================================================
# Ancore come le calcola GitHub
# =============================================================================
_LINK_IN_TITOLO = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")


def testo_titolo(titolo: str) -> str:
    """Il testo visibile di un titolo Markdown, senza link né immagini."""
    return _LINK_IN_TITOLO.sub(r"\1", titolo).strip()


def slug_github(titolo: str) -> str:
    """Come github-slugger: minuscole, via tutto ciò che non è lettera, cifra,
    segno combinante, `-` o `_`, e ogni spazio diventa `-` senza compattare."""
    testo = unicodedata.normalize("NFC", testo_titolo(titolo)).lower()
    tenuti = []
    for carattere in testo:
        categoria = unicodedata.category(carattere)
        if carattere in "-_ " or categoria[0] in "LMN":
            tenuti.append(carattere)
    return "".join(tenuti).replace(" ", "-")


_TITOLO = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*(?:[ \t]#+[ \t]*)?$")
_RECINTO = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_ANCORA_HTML = re.compile(r"""<a\s+(?:name|id)=["']([^"']+)["']""", re.IGNORECASE)


def righe_fuori_dal_codice(testo: str):
    """(numero, riga) delle righe fuori dai blocchi di codice recintati."""
    recinto = None
    for numero, riga in enumerate(testo.split("\n"), start=1):
        aperto = _RECINTO.match(riga)
        if recinto:
            if aperto and aperto.group(1)[0] == recinto[0] and len(aperto.group(1)) >= len(recinto):
                recinto = None
            continue
        if aperto:
            recinto = aperto.group(1)
            continue
        yield numero, riga


def ancore(testo: str) -> set[str]:
    trovate: set[str] = set()
    visti: dict[str, int] = {}
    for _, riga in righe_fuori_dal_codice(testo):
        titolo = _TITOLO.match(riga)
        if titolo:
            base = slug_github(titolo.group(2))
            if base in visti:
                visti[base] += 1
                trovate.add(f"{base}-{visti[base]}")
            else:
                visti[base] = 0
                trovate.add(base)
        for nome in _ANCORA_HTML.findall(riga):
            trovate.add(nome)
    return trovate


def risolvi(da_file: str, destinazione: str) -> str | None:
    """Percorso relativo alla radice, o None se esce dal repository."""
    base = posixpath.dirname(da_file)
    percorso = posixpath.normpath(posixpath.join(base, destinazione))
    if percorso == ".":
        return ""
    if percorso.startswith("../") or percorso == "..":
        return None
    return percorso


# =============================================================================
# Valori che non devono finire in un repository pubblico
# =============================================================================
# I segnaposto usano le parentesi quadre: in Markdown `<dominio>` sarebbe un tag
# HTML, che GitHub scarta silenziosamente portandosi via il testo redatto.
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*")
_CREDENZIALI = re.compile(r"(?<=://)[^\s:@/]+:[^\s@]+@")
_CREDENZIALI_NUDE = re.compile(r"\b(?:root|admin|utente|user):[^\s@/,;]+", re.IGNORECASE)
_PERCORSO_SERVER = re.compile(r"(?<![\w.])/(?:srv|opt|home|root|data|mnt|etc|var/lib)/[^\s,;)`]+")
_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
# Candidati IPv6: si tengono solo quelli con `::` o una cifra esadecimale
# alfabetica, altrimenti un'ora come 18:40:00 verrebbe redatta.
_IPV6 = re.compile(r"(?<![\w:])(?:[0-9a-f]{1,4})?(?::{1,2}[0-9a-f]{1,4}){2,7}(?![\w:])", re.IGNORECASE)
# Suffissi di rete interna: sono quelli che non devono comparire.
SUFFISSI_INTERNI = ("local", "lan", "internal", "intranet", "corp", "localdomain", "priv", "home")
_PUBBLICI = ("it", "com", "net", "org", "eu", "io", "info", "biz", "cloud", "dev", "app", "gov", "edu")
_DOMINIO = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:" + "|".join(_PUBBLICI + SUFFISSI_INTERNI) + r")\b",
                      re.IGNORECASE)
_DOMINI_AMMESSI = re.compile(
    r"(?:^|\.)(?:example\.(?:com|net|org)|esempio\.(?:it|com|net|org)|localhost|invalid|test)$",
    re.IGNORECASE)
# Il dominio dell'ente: nei documenti non ci va, nemmeno come host di collaudo.
_DOMINIO_ENTE = re.compile(r"\b[a-z0-9-]+\.ersaf\.it\b|\bersaf\.it\b", re.IGNORECASE)
LOOPBACK = "127.0.0.1"


def _ipv6(valore: str) -> bool:
    return "::" in valore or any(c in "abcdef" for c in valore.lower())


def redigi(testo: str) -> str:
    """Sostituisce con un segnaposto i valori che non vanno pubblicati.

    La usano i generatori sui commenti e sulle intestazioni che copiano nelle
    pagine di docs/tecnica/riferimenti/. Preferisce redigere troppo.
    """
    testo = _CREDENZIALI.sub("[credenziali]@", testo)
    testo = _CREDENZIALI_NUDE.sub("[credenziali]", testo)
    testo = _PERCORSO_SERVER.sub("[percorso-server]", testo)
    testo = _EMAIL.sub("[email]", testo)
    testo = _IPV4.sub(lambda m: m.group(0) if m.group(0) == LOOPBACK else "[ip]", testo)
    testo = _IPV6.sub(lambda m: "[ip]" if _ipv6(m.group(0)) else m.group(0), testo)
    return _DOMINIO.sub(
        lambda m: m.group(0) if _DOMINI_AMMESSI.search(m.group(0)) else "[dominio]", testo)


_CATEGORIE = (
    ("indirizzo email", _EMAIL, lambda v: not _DOMINI_AMMESSI.search(v.split("@")[-1])),
    ("indirizzo IP", _IPV4, lambda v: v != LOOPBACK),
    ("indirizzo IPv6", _IPV6, _ipv6),
    ("credenziali", _CREDENZIALI, lambda v: True),
    ("credenziali", _CREDENZIALI_NUDE, lambda v: True),
    ("percorso del server", _PERCORSO_SERVER, lambda v: True),
    ("nome di rete interna", _DOMINIO,
     lambda v: v.rsplit(".", 1)[-1].lower() in SUFFISSI_INTERNI),
    ("dominio dell'ente", _DOMINIO_ENTE, lambda v: True),
)


def sospetti(testo: str) -> list[tuple[str, str]]:
    """(categoria, valore) dei dati che in un repository pubblico non vanno
    scritti nei documenti. Piu' stretta di `redigi`: qui i falsi positivi
    bloccherebbero una pull request, quindi si cercano solo le categorie
    inequivocabili."""
    trovati = []
    for categoria, regex, ammesso in _CATEGORIE:
        for corrispondenza in regex.finditer(testo):
            valore = corrispondenza.group(0)
            if ammesso(valore):
                trovati.append((categoria, valore))
    return trovati


# =============================================================================
# Messaggi
# =============================================================================
def _escape_annotazione(testo: str) -> str:
    return testo.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def segnala(messaggio: str, file: str | None = None, riga: int | None = None,
            titolo: str | None = None) -> None:
    """Errore leggibile in locale; annotazione in GitHub Actions."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        parti = []
        if file:
            parti.append(f"file={file}")
        if riga:
            parti.append(f"line={riga}")
        if titolo:
            parti.append(f"title={_escape_annotazione(titolo)}")
        intestazione = "::error " + ",".join(parti) if parti else "::error"
        print(f"{intestazione}::{_escape_annotazione(messaggio)}")
        return
    posizione = file or ""
    if file and riga:
        posizione += f":{riga}"
    prefisso = f"{posizione}: " if posizione else ""
    print(f"ERRORE {prefisso}{messaggio}", file=sys.stdout)
