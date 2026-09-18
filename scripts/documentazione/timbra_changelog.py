"""Timbro del changelog dopo un deploy riuscito di origin/main.

    python scripts/documentazione/timbra_changelog.py --ref=origin/main \
        --versione=12 --aggiornata=2026-09-17T18:40:00+02:00 --sha=<40 caratteri>

Raccoglie i frammenti di changelog/non-pubblicato presenti nel commit
pubblicato e ancora identici su main, scrive in CHANGELOG.md la sezione
"## Versione N — gg/mm/aaaa hh:mm" (stesso numero e stessa ora del menu,
fuso Europe/Rome), cancella quei frammenti, fa il commit
"Changelog: Versione N" e lo invia a main. Lavora in un worktree temporaneo:
la cartella di chi pubblica non viene toccata. Rilanciarlo con gli stessi
argomenti non cambia nulla.

Esiti: 0 fatto (o già fatto, o deploy di prova); 2 argomenti non validi;
3 il numero è già usato da un altro commit; 4 invio a main non riuscito;
5 CHANGELOG.md o marcatore assente; 6 errore di git. Dettagli e procedure:
docs/tecnica/deploy.md.

Solo libreria standard e Python >= 3.10: gira sul PC di chi pubblica.
"""

from __future__ import annotations

import argparse
import datetime as dt
import posixpath
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from comune import RADICE, ErroreGit, git, git_bytes, git_riuscito, leggi, scrivi  # noqa: E402
import frammenti  # noqa: E402

REF_PUBBLICATO = "origin/main"
REMOTO = "origin"
RAMO = "main"
CHANGELOG = "CHANGELOG.md"
PREFISSO_WORKTREE = "ersaf-timbro-"
TIMEOUT_RETE = 120
RICHIEDONO_FRAMMENTO = ("backend/src/", "frontend/src/", "db/", "deploy/")

MARCATORE_INSERIMENTO = "<!-- nuove-versioni:"
_MARCATORE_TIMBRO = re.compile(r"^<!-- timbro: versione=(\d+) sha=([0-9a-f]{40}) -->$")
_TITOLO_VERSIONE = re.compile(r"^## Versione (\d+)(?:\s|$)")
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(Z|[+-]\d{2}:\d{2})$")
_SHA = re.compile(r"^[0-9a-f]{40}$")

OK, USO, NUMERO_USATO, PUSH_FALLITO, CHANGELOG_ASSENTE, ERRORE_GIT = 0, 2, 3, 4, 5, 6


class Interruzione(Exception):
    def __init__(self, codice: int, messaggio: str):
        self.codice = codice
        super().__init__(messaggio)


def avviso(testo: str) -> None:
    print(f"ATTENZIONE: {testo}")


# =============================================================================
# Ora del menu: Europe/Rome senza database dei fusi
# =============================================================================
def _ultima_domenica(anno: int, mese: int) -> int:
    giorno = dt.date(anno, mese, 31)
    return 31 - (giorno.weekday() + 1) % 7


def ora_di_roma(istante: dt.datetime) -> dt.datetime:
    """Regola dell'Unione europea: ora legale dalle 01:00 UTC dell'ultima
    domenica di marzo alle 01:00 UTC dell'ultima domenica di ottobre. Evita di
    dipendere da tzdata, che su Windows non c'è."""
    utc = istante.astimezone(dt.timezone.utc)
    inizio = dt.datetime(utc.year, 3, _ultima_domenica(utc.year, 3), 1, tzinfo=dt.timezone.utc)
    fine = dt.datetime(utc.year, 10, _ultima_domenica(utc.year, 10), 1, tzinfo=dt.timezone.utc)
    scarto = dt.timedelta(hours=2 if inizio <= utc < fine else 1)
    return (utc + scarto).replace(tzinfo=None)


def leggi_istante(testo: str) -> dt.datetime | None:
    """ISO 8601 come lo scrive deploy.ps1; `fromisoformat` accetta la Z solo
    dalla 3.11, quindi si legge a mano."""
    if not testo:
        return None
    parti = _ISO.match(testo)
    if not parti:
        raise ValueError(f"istante non valido: {testo!r}")
    anno, mese, giorno, ora, minuto, secondo, zona = parti.groups()
    if zona == "Z":
        fuso = dt.timezone.utc
    else:
        segno = 1 if zona[0] == "+" else -1
        fuso = dt.timezone(segno * dt.timedelta(hours=int(zona[1:3]), minutes=int(zona[4:6])))
    return dt.datetime(int(anno), int(mese), int(giorno), int(ora), int(minuto), int(secondo), tzinfo=fuso)


# =============================================================================
# Composizione del CHANGELOG
# =============================================================================
def titolo(versione: int, istante: dt.datetime | None) -> str:
    if istante is None:
        return f"## Versione {versione}"
    return f"## Versione {versione} — {ora_di_roma(istante):%d/%m/%Y %H:%M}"


def sezione(versione: int, sha: str, istante: dt.datetime | None, raccolti: list) -> list[str]:
    return [titolo(versione, istante), "", f"<!-- timbro: versione={versione} sha={sha} -->", "",
            *frammenti.componi(raccolti).split("\n")]


def timbri(testo: str) -> dict[int, str]:
    trovati = {}
    for riga in testo.split("\n"):
        corrispondenza = _MARCATORE_TIMBRO.match(riga.strip())
        if corrispondenza:
            trovati[int(corrispondenza.group(1))] = corrispondenza.group(2)
    return trovati


def versioni_con_titolo(testo: str) -> set[int]:
    return {int(m.group(1)) for m in (_TITOLO_VERSIONE.match(r) for r in testo.split("\n")) if m}


def stato(testo: str, versione: int, sha: str) -> str:
    """'fatto' se la stessa versione è già timbrata con lo stesso commit,
    'conflitto' se il numero c'è già con un altro commit, altrimenti 'nuovo'."""
    presenti = timbri(testo)
    if presenti.get(versione) == sha:
        return "fatto"
    if versione in presenti or versione in versioni_con_titolo(testo):
        return "conflitto"
    return "nuovo"


def inserisci(testo: str, versione: int, righe_sezione: list[str]) -> str:
    """Inserisce la sezione sotto il marcatore, con le versioni in ordine
    decrescente e comunque prima del primo titolo che non è una versione."""
    righe = testo.split("\n")
    try:
        marcatore = next(i for i, r in enumerate(righe) if r.startswith(MARCATORE_INSERIMENTO))
    except StopIteration:
        raise Interruzione(CHANGELOG_ASSENTE, "in CHANGELOG.md manca il marcatore di inserimento "
                                              f"({MARCATORE_INSERIMENTO} …)") from None
    fine = next((i for i in range(marcatore + 1, len(righe))
                 if righe[i].startswith("## ") and not _TITOLO_VERSIONE.match(righe[i])), len(righe))
    posizione = fine
    for i in range(marcatore + 1, fine):
        esistente = _TITOLO_VERSIONE.match(righe[i])
        if esistente and int(esistente.group(1)) < versione:
            posizione = i
            break
    blocco = list(righe_sezione)
    if blocco[-1] != "":
        blocco.append("")
    if posizione == marcatore + 1 or righe[posizione - 1] != "":
        blocco.insert(0, "")
    righe[posizione:posizione] = blocco
    return "\n".join(righe)


# =============================================================================
# Git
# =============================================================================
def _pulisci_worktree_orfani(repo: Path) -> None:
    git("worktree", "prune", cwd=repo, controlla=False)
    elenco = git("worktree", "list", "--porcelain", cwd=repo, controlla=False)
    for riga in elenco.split("\n"):
        if riga.startswith("worktree ") and Path(riga[9:]).name.startswith(PREFISSO_WORKTREE):
            percorso = riga[9:]
            if not git_riuscito("worktree", "remove", "--force", percorso, cwd=repo):
                shutil.rmtree(percorso, ignore_errors=True)
    git("worktree", "prune", cwd=repo, controlla=False)


def _aggiorna_main(repo: Path) -> str:
    try:
        git("fetch", "--quiet", REMOTO, f"+refs/heads/{RAMO}:refs/remotes/{REMOTO}/{RAMO}",
            cwd=repo, timeout=TIMEOUT_RETE)
    except ErroreGit as errore:
        raise Interruzione(ERRORE_GIT, f"aggiornamento di {REMOTO}/{RAMO} non riuscito: {errore.errori.strip()}") from None
    return git("rev-parse", f"{REMOTO}/{RAMO}", cwd=repo).strip()


def _blob(cartella: Path, riferimento: str) -> str | None:
    try:
        return git("rev-parse", "--verify", "--quiet", riferimento, cwd=cartella).strip() or None
    except ErroreGit:
        return None


def raccogli(worktree: Path, sha: str) -> tuple[list, list[str]]:
    """Frammenti validi presenti nel commit pubblicato e ancora identici su
    main (HEAD del worktree), con i loro percorsi."""
    grezzo = git_bytes("ls-tree", "-z", "--name-only", sha, "--", frammenti.CARTELLA + "/", cwd=worktree)
    raccolti, percorsi = [], []
    for percorso in sorted(n.decode("utf-8") for n in grezzo.split(b"\0") if n):
        if not frammenti.e_frammento(percorso):
            continue
        pubblicato = _blob(worktree, f"{sha}:{percorso}")
        attuale = _blob(worktree, f"HEAD:{percorso}")
        if pubblicato is None or pubblicato != attuale:
            if attuale is not None:
                avviso(f"{percorso} è cambiato dopo il commit pubblicato: resta per la prossima versione")
            continue
        testo = git_bytes("cat-file", "-p", pubblicato, cwd=worktree).decode("utf-8")
        try:
            raccolti.append(frammenti.analizza(posixpath.basename(percorso), testo))
        except frammenti.FrammentoNonValido as errore:
            avviso(f"frammento non valido, lasciato dov'è: {errore}")
            continue
        percorsi.append(percorso)
    return raccolti, percorsi


def commit_senza_frammento(worktree: Path, dal_sha: str | None, al_sha: str) -> list[str]:
    """Commit fra l'ultimo timbro e quello pubblicato che toccano il codice
    senza aggiungere un frammento: di solito push diretti su main."""
    if not dal_sha or not git_riuscito("merge-base", "--is-ancestor", dal_sha, al_sha, cwd=worktree):
        return []
    log = git("log", "--no-merges", "--format=%x01%h %s", "--name-status", f"{dal_sha}..{al_sha}", cwd=worktree)
    trovati = []
    for blocco in log.split("\x01")[1:]:
        intestazione, *righe = blocco.strip().split("\n")
        codice = aggiunto = False
        for riga in righe:
            parti = riga.split("\t")
            if len(parti) < 2:
                continue
            stato_file, percorso = parti[0], parti[-1]
            if percorso.startswith(RICHIEDONO_FRAMMENTO) and not percorso.endswith(".md"):
                codice = True
            if stato_file[0] in "AM" and frammenti.e_frammento(percorso):
                aggiunto = True
        if codice and not aggiunto:
            trovati.append(intestazione)
    return trovati


def componi_nel_worktree(worktree: Path, versione: int, sha: str, istante, ultima_versione: int | None) -> bool:
    """Prepara il commit. Restituisce False se la versione è già timbrata."""
    percorso_changelog = worktree / CHANGELOG
    if not percorso_changelog.is_file():
        raise Interruzione(CHANGELOG_ASSENTE, "CHANGELOG.md non esiste su main")
    testo = leggi(percorso_changelog)
    esito = stato(testo, versione, sha)
    if esito == "fatto":
        print(f"La versione {versione} è già nel changelog: niente da fare.")
        return False
    if esito == "conflitto":
        raise Interruzione(NUMERO_USATO, (
            f"CHANGELOG.md contiene già la versione {versione} con un altro commit. Il contatore delle "
            "pubblicazioni sul server è stato riusato o è ripartito: rilanciare il timbro non serve. "
            "Procedura in docs/tecnica/deploy.md, sezione sul timbro del changelog."))
    presenti = timbri(testo)
    if presenti and versione > max(presenti) + 1:
        saltate = ", ".join(str(n) for n in range(max(presenti) + 1, versione))
        avviso(f"nel changelog mancano le versioni {saltate}: deploy di prova o timbri non riusciti")
    if ultima_versione is not None and ultima_versione != versione:
        avviso(f"sul server il contatore vale {ultima_versione}, non {versione}: il prossimo deploy "
               f"potrebbe riusare il numero {versione}")

    raccolti, percorsi = raccogli(worktree, sha)
    ultimo = presenti[max(presenti)] if presenti else None
    for commit in commit_senza_frammento(worktree, ultimo, sha):
        avviso(f"commit senza frammento di changelog: {commit}")

    scrivi(percorso_changelog, inserisci(testo, versione, sezione(versione, sha, istante, raccolti)))
    if percorsi:
        git("rm", "--quiet", "--", *percorsi, cwd=worktree)
    git("add", "--", CHANGELOG, cwd=worktree)
    git("commit", "--quiet", "--no-verify", "-m", f"Changelog: Versione {versione}", cwd=worktree)
    elenco = ", ".join(posixpath.basename(p) for p in percorsi) or "nessun frammento"
    print(f"Versione {versione} scritta in CHANGELOG.md ({elenco}).")
    return True


def _push(worktree: Path) -> ErroreGit | None:
    try:
        git("push", "--quiet", REMOTO, f"HEAD:refs/heads/{RAMO}", cwd=worktree, timeout=TIMEOUT_RETE)
    except ErroreGit as errore:
        return errore
    return None


def timbra(repo: Path, versione: int, sha: str, istante, ultima_versione: int | None) -> int:
    for chiave in ("user.name", "user.email"):
        if not git("config", "--get", chiave, cwd=repo, controlla=False).strip():
            raise Interruzione(ERRORE_GIT, f"git non ha {chiave} configurato: serve per il commit del changelog")
    _pulisci_worktree_orfani(repo)
    prima = _aggiorna_main(repo)
    if not git_riuscito("cat-file", "-e", f"{sha}^{{commit}}", cwd=repo):
        raise Interruzione(ERRORE_GIT, f"il commit {sha} non esiste in questo repository")
    if not git_riuscito("merge-base", "--is-ancestor", sha, f"{REMOTO}/{RAMO}", cwd=repo):
        raise Interruzione(ERRORE_GIT, f"il commit {sha} non è su {REMOTO}/{RAMO}")

    worktree = Path(tempfile.mkdtemp(prefix=PREFISSO_WORKTREE))
    try:
        git("worktree", "add", "--quiet", "--detach", str(worktree), f"{REMOTO}/{RAMO}", cwd=repo)
        if not componi_nel_worktree(worktree, versione, sha, istante, ultima_versione):
            return OK
        errore = _push(worktree)
        if errore is None:
            print(f"Changelog inviato a {REMOTO}/{RAMO}.")
            return OK
        # Un solo nuovo tentativo, e solo se main è andato avanti nel frattempo:
        # si rifà il lavoro sopra il main aggiornato (come un rebase, ma senza
        # conflitti sul CHANGELOG).
        dopo = _aggiorna_main(repo)
        if dopo != prima:
            print(f"{REMOTO}/{RAMO} è avanzato: nuovo tentativo sopra la versione aggiornata.")
            git("reset", "--quiet", "--hard", f"{REMOTO}/{RAMO}", cwd=worktree)
            if not componi_nel_worktree(worktree, versione, sha, istante, ultima_versione):
                return OK
            errore = _push(worktree)
            if errore is None:
                print(f"Changelog inviato a {REMOTO}/{RAMO}.")
                return OK
        dettaglio = errore.errori.strip()
        protetto = any(s in dettaglio.lower() for s in ("protected branch", "gh006", "gh013",
                                                        "pre-receive hook declined", "rule violations"))
        motivo = ("il ramo main rifiuta i push diretti (protezione o regole del repository)"
                  if protetto else "l'invio a main non è riuscito")
        raise Interruzione(PUSH_FALLITO, f"{motivo}: {dettaglio}")
    finally:
        if not git_riuscito("worktree", "remove", "--force", str(worktree), cwd=repo):
            avviso(f"non riesco a rimuovere il worktree temporaneo {worktree}")
            shutil.rmtree(worktree, ignore_errors=True)
        git("worktree", "prune", cwd=repo, controlla=False)


def comando_manuale(versione, sha, aggiornata) -> str:
    return (f"python scripts/documentazione/timbra_changelog.py --ref={REF_PUBBLICATO} "
            f"--versione={versione} --aggiornata={aggiornata} --sha={sha}")


def esegui(argomenti: list[str] | None = None, repo: Path = RADICE) -> int:
    for flusso in (sys.stdout, sys.stderr):
        try:
            flusso.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Timbro del changelog dopo il deploy")
    parser.add_argument("--ref", required=True, help="riferimento pubblicato da deploy.ps1")
    parser.add_argument("--versione", required=True, help="numero di versione assegnato dal server")
    parser.add_argument("--aggiornata", default="", help="istante ISO del deploy, vuoto se non disponibile")
    parser.add_argument("--sha", required=True, help="commit pubblicato, 40 caratteri")
    parser.add_argument("--ultima-versione", default="", help="contatore registrato sul server")
    opzioni = parser.parse_args(argomenti)

    if opzioni.ref != REF_PUBBLICATO:
        print(f"Deploy di prova di {opzioni.ref or 'albero di lavoro'}: il numero di versione è stato "
              "consumato ma non viene scritto in CHANGELOG.md.")
        return OK
    try:
        if not re.fullmatch(r"[1-9][0-9]*", opzioni.versione):
            raise ValueError(f"versione non valida: {opzioni.versione!r}")
        versione = int(opzioni.versione)
        if not _SHA.match(opzioni.sha):
            raise ValueError(f"sha non valido: {opzioni.sha!r}")
        istante = leggi_istante(opzioni.aggiornata)
        ultima = int(opzioni.ultima_versione) if opzioni.ultima_versione else None
    except ValueError as errore:
        print(f"ERRORE: {errore}")
        return USO
    try:
        return timbra(Path(repo), versione, opzioni.sha, istante, ultima)
    except Interruzione as interruzione:
        print(f"ERRORE: {interruzione}")
        if interruzione.codice in (PUSH_FALLITO, ERRORE_GIT):
            print("Il deploy resta valido. Per completare il changelog, da un clone con diritti di "
                  "scrittura su main:")
            print(f"  {comando_manuale(versione, opzioni.sha, opzioni.aggiornata)}")
        return interruzione.codice
    except ErroreGit as errore:
        print(f"ERRORE: {errore}")
        print(f"  {comando_manuale(versione, opzioni.sha, opzioni.aggiornata)}")
        return ERRORE_GIT


if __name__ == "__main__":
    sys.exit(esegui())
