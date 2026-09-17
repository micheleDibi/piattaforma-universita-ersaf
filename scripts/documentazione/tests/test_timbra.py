from __future__ import annotations

import ast
import datetime as dt
import subprocess
import sys
from pathlib import Path

import pytest

import timbra_changelog as timbro
from conftest import FRAMMENTO_VALIDO, Repo

CARTELLA = Path(__file__).resolve().parents[1]
CHANGELOG = """# Registro delle modifiche

Introduzione.

<!-- nuove-versioni: il timbro inserisce qui sotto; non spostare questa riga -->

## Storico precedente

- Voci vecchie.
"""
FRAMMENTO_A = "changelog/non-pubblicato/2026-09-17-a.md"
FRAMMENTO_B = "changelog/non-pubblicato/2026-09-18-b.md"
ISTANTE = "2026-09-17T18:40:00+02:00"


# --- ora e composizione ------------------------------------------------------
def test_regola_europea_uguale_a_zoneinfo():
    zoneinfo = pytest.importorskip("zoneinfo")
    try:
        roma = zoneinfo.ZoneInfo("Europe/Rome")
    except zoneinfo.ZoneInfoNotFoundError:
        pytest.skip("database dei fusi non disponibile")
    istante = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
    while istante.year < 2031:
        assert timbro.ora_di_roma(istante) == istante.astimezone(roma).replace(tzinfo=None), istante
        istante += dt.timedelta(minutes=30)


@pytest.mark.parametrize(("iso", "atteso"), [
    ("2026-09-17T18:40:00+02:00", "## Versione 3 — 17/09/2026 18:40"),
    ("2026-09-17T16:40:59Z", "## Versione 3 — 17/09/2026 18:40"),
    ("2026-03-29T00:59:00Z", "## Versione 3 — 29/03/2026 01:59"),
    ("2026-03-29T01:00:00Z", "## Versione 3 — 29/03/2026 03:00"),
    ("2026-10-25T00:59:00Z", "## Versione 3 — 25/10/2026 02:59"),
    ("2026-10-25T01:00:00Z", "## Versione 3 — 25/10/2026 02:00"),
    ("2026-12-31T23:30:00-05:00", "## Versione 3 — 01/01/2027 05:30"),
    ("", "## Versione 3"),
])
def test_titolo(iso, atteso):
    assert timbro.titolo(3, timbro.leggi_istante(iso)) == atteso


@pytest.mark.parametrize("iso", ["2026-09-17 18:40", "2026-09-17T18:40:00", "ieri"])
def test_istante_non_valido(iso):
    with pytest.raises(ValueError):
        timbro.leggi_istante(iso)


def test_inserimento_ordinato():
    sha = "a" * 40
    testo = CHANGELOG
    for versione in (5, 8, 7):
        testo = timbro.inserisci(testo, versione, timbro.sezione(versione, sha[:-1] + str(versione), None, []))
    titoli = [r for r in testo.split("\n") if r.startswith("## ")]
    assert titoli == ["## Versione 8", "## Versione 7", "## Versione 5", "## Storico precedente"]
    assert "\n\n\n" not in testo
    assert "-->\n\n## Versione 8\n\n<!-- timbro: versione=8" in testo
    assert "Nessuna modifica documentata.\n\n## Storico precedente" in testo
    assert timbro.stato(testo, 7, sha[:-1] + "7") == "fatto"
    assert timbro.stato(testo, 7, "b" * 40) == "conflitto"
    assert timbro.stato(testo, 9, "b" * 40) == "nuovo"


def test_marcatore_assente():
    with pytest.raises(timbro.Interruzione) as info:
        timbro.inserisci("# Registro\n", 1, ["## Versione 1"])
    assert info.value.codice == timbro.CHANGELOG_ASSENTE


def test_compatibile_con_python_3_10_e_senza_yaml():
    for nome in ("comune.py", "frammenti.py", "timbra_changelog.py"):
        ast.parse((CARTELLA / nome).read_text(encoding="utf-8"), feature_version=(3, 10))
    codice = ("import sys; sys.modules['yaml'] = None; sys.path.insert(0, sys.argv[1]); "
              "import timbra_changelog")
    esito = subprocess.run([sys.executable, "-X", "warn_default_encoding", "-W", "error::EncodingWarning",
                            "-c", codice, str(CARTELLA)], capture_output=True, encoding="utf-8")
    assert esito.returncode == 0, esito.stderr


# --- scenari con un remoto vero ----------------------------------------------
class Ambiente:
    def __init__(self, tmp_path: Path):
        self.remoto = tmp_path / "remoto.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remoto)], check=True)
        self.autore = self._clona(tmp_path / "autore")
        self.autore.scrivi("CHANGELOG.md", CHANGELOG)
        self.autore.scrivi("changelog/non-pubblicato/LEGGIMI.md", "# Frammenti\n")
        self.autore.scrivi("backend/src/app.py", "x = 1\n")
        self.autore.commit("base")
        self.autore.git("push", "-q", "origin", "main")
        self.pubblicatore = self._clona(tmp_path / "pubblicatore")

    def _clona(self, cartella: Path) -> Repo:
        subprocess.run(["git", "clone", "-q", str(self.remoto), str(cartella)], check=True,
                       capture_output=True)
        return Repo(cartella)

    def pubblica(self, **file) -> str:
        """Commit su main dall'autore; restituisce lo SHA."""
        self.autore.git("pull", "-q", "--rebase", "origin", "main")
        for percorso, testo in file.items():
            percorso = percorso.replace("__", "/")
            if testo is None:
                self.autore.cancella(percorso)
            else:
                self.autore.scrivi(percorso, testo)
        sha = self.autore.commit("modifica")
        self.autore.git("push", "-q", "origin", "main")
        return sha

    def changelog_remoto(self) -> str:
        return self.autore.git("--git-dir", str(self.remoto), "show", "main:CHANGELOG.md") + "\n"

    def file_remoti(self) -> list[str]:
        return self.autore.git("--git-dir", str(self.remoto), "ls-tree", "-r", "--name-only", "main").split("\n")

    def timbra(self, versione, sha, aggiornata=ISTANTE, ref="origin/main", **altro):
        argomenti = [f"--ref={ref}", f"--versione={versione}", f"--aggiornata={aggiornata}", f"--sha={sha}"]
        argomenti += [f"--{k.replace('_', '-')}={v}" for k, v in altro.items()]
        return timbro.esegui(argomenti, repo=self.pubblicatore.percorso)


@pytest.fixture
def amb(tmp_path):
    return Ambiente(tmp_path)


def _frammento(testo_novita: str) -> str:
    return FRAMMENTO_VALIDO.replace("Negli elenchi compare lo stato di verifica dei contatti.", testo_novita)


def test_con_frammenti(amb, capsys):
    sha = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): _frammento("Prima novità."),
                          "backend__src__app.py": "x = 2\n"})
    assert amb.timbra(1, sha) == 0
    changelog = amb.changelog_remoto()
    assert "## Versione 1 — 17/09/2026 18:40" in changelog
    assert f"<!-- timbro: versione=1 sha={sha} -->" in changelog
    assert "- Prima novità. (PR #7)" in changelog
    file = amb.file_remoti()
    assert FRAMMENTO_A not in file and "changelog/non-pubblicato/LEGGIMI.md" in file
    ultimo = amb.autore.git("--git-dir", str(amb.remoto), "log", "-1", "--format=%s", "main")
    assert ultimo == "Changelog: Versione 1"
    assert "Changelog inviato" in capsys.readouterr().out


def test_senza_frammenti_e_rilancio_idempotente(amb):
    sha = amb.pubblica(**{"backend__src__app.py": "x = 3\n"})
    assert amb.timbra(1, sha, aggiornata="") == 0
    changelog = amb.changelog_remoto()
    assert "## Versione 1\n\n<!-- timbro: versione=1" in changelog
    assert "Nessuna modifica documentata." in changelog
    commit = amb.autore.git("--git-dir", str(amb.remoto), "rev-parse", "main")
    assert amb.timbra(1, sha, aggiornata="") == 0
    assert amb.autore.git("--git-dir", str(amb.remoto), "rev-parse", "main") == commit


def test_raccoglie_solo_i_frammenti_dello_sha_e_invariati(amb, capsys):
    sha = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): _frammento("Pubblicata."),
                          FRAMMENTO_B.replace("/", "__"): _frammento("Da cambiare.")})
    amb.pubblica(**{FRAMMENTO_B.replace("/", "__"): _frammento("Cambiata dopo."),
                    "changelog__non-pubblicato__2026-09-19-c.md": _frammento("Arrivata dopo.")})
    assert amb.timbra(4, sha) == 0
    changelog = amb.changelog_remoto()
    assert "Pubblicata." in changelog
    assert "Da cambiare." not in changelog and "Cambiata dopo." not in changelog
    assert "Arrivata dopo." not in changelog
    file = amb.file_remoti()
    assert FRAMMENTO_A not in file
    assert FRAMMENTO_B in file and "changelog/non-pubblicato/2026-09-19-c.md" in file
    assert "resta per la prossima versione" in capsys.readouterr().out


def test_frammento_non_valido_lasciato(amb, capsys):
    sha = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): "niente frontmatter\n"})
    assert amb.timbra(2, sha) == 0
    assert FRAMMENTO_A in amb.file_remoti()
    assert "frammento non valido" in capsys.readouterr().out


def test_rilancio_manuale_dopo_la_versione_successiva(amb):
    """Il timbro di 1 è fallito; 2 raccoglie gli stessi frammenti; il rilancio
    di 1 non deve ripeterli."""
    sha1 = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): _frammento("Una volta sola.")})
    sha2 = amb.pubblica(**{"backend__src__app.py": "x = 9\n"})
    assert amb.timbra(2, sha2) == 0
    assert amb.timbra(1, sha1) == 0
    changelog = amb.changelog_remoto()
    assert changelog.count("Una volta sola.") == 1
    titoli = [r for r in changelog.split("\n") if r.startswith("## ")]
    assert titoli[:2] == ["## Versione 2 — 17/09/2026 18:40", "## Versione 1 — 17/09/2026 18:40"]


def test_stesso_sha_pubblicato_due_volte(amb):
    sha = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): _frammento("Doppia.")})
    assert amb.timbra(1, sha) == 0
    assert amb.timbra(2, sha) == 0
    changelog = amb.changelog_remoto()
    assert changelog.count("Doppia.") == 1
    assert "## Versione 2" in changelog


def test_numero_riusato(amb, capsys):
    sha1 = amb.pubblica(**{"backend__src__app.py": "x = 4\n"})
    sha2 = amb.pubblica(**{"backend__src__app.py": "x = 5\n"})
    assert amb.timbra(3, sha1) == 0
    capsys.readouterr()
    assert amb.timbra(3, sha2) == timbro.NUMERO_USATO
    uscita = capsys.readouterr().out
    assert "già la versione 3" in uscita and "timbra_changelog.py --ref" not in uscita


def test_salti_e_contatore(amb, capsys):
    sha = amb.pubblica(**{"backend__src__app.py": "x = 6\n"})
    assert amb.timbra(1, sha) == 0
    sha = amb.pubblica(**{"backend__src__app.py": "x = 7\n"})
    capsys.readouterr()
    assert amb.timbra(4, sha, ultima_versione=3) == 0
    uscita = capsys.readouterr().out
    assert "mancano le versioni 2, 3" in uscita
    assert "il prossimo deploy potrebbe riusare il numero 4" in uscita


def test_changelog_o_marcatore_assenti(amb):
    sha = amb.pubblica(**{"CHANGELOG.md": "# Registro senza marcatore\n"})
    assert amb.timbra(1, sha) == timbro.CHANGELOG_ASSENTE
    sha = amb.pubblica(**{"CHANGELOG.md": None})
    assert amb.timbra(1, sha) == timbro.CHANGELOG_ASSENTE


def test_main_avanzato_durante_il_timbro(amb, monkeypatch):
    sha = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): _frammento("Durante.")})
    originale = timbro._push
    chiamate = []

    def push_con_concorrenza(worktree):
        if not chiamate:
            amb.pubblica(**{"backend__src__app.py": "x = 8\n"})
        chiamate.append(worktree)
        return originale(worktree)

    monkeypatch.setattr(timbro, "_push", push_con_concorrenza)
    assert amb.timbra(1, sha) == 0
    assert len(chiamate) == 2
    assert "Durante." in amb.changelog_remoto()
    assert "x = 8" in amb.autore.git("--git-dir", str(amb.remoto), "show", "main:backend/src/app.py")


def test_main_avanza_sempre(amb, monkeypatch, capsys):
    sha = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): _frammento("Mai.")})
    originale = timbro._push
    contatore = iter(range(100))

    def push_sempre_superato(worktree):
        amb.pubblica(**{"backend__src__app.py": f"x = {100 + next(contatore)}\n"})
        return originale(worktree)

    monkeypatch.setattr(timbro, "_push", push_sempre_superato)
    assert amb.timbra(1, sha) == timbro.PUSH_FALLITO
    uscita = capsys.readouterr().out
    assert "Il deploy resta valido" in uscita
    assert f"--ref=origin/main --versione=1 --aggiornata={ISTANTE} --sha={sha}" in uscita
    monkeypatch.setattr(timbro, "_push", originale)
    assert amb.timbra(1, sha) == 0
    assert amb.changelog_remoto().count("Mai.") == 1


def test_ramo_protetto(amb, capsys):
    sha = amb.pubblica(**{"backend__src__app.py": "x = 10\n"})
    hook = amb.remoto / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho 'GH006: Protected branch update failed' >&2\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)
    assert amb.timbra(1, sha) == timbro.PUSH_FALLITO
    assert "rifiuta i push diretti" in capsys.readouterr().out


def test_ref_di_prova_e_argomenti(amb, capsys):
    sha = amb.pubblica(**{"backend__src__app.py": "x = 11\n"})
    assert amb.timbra(1, sha, ref="origin/prova") == 0
    assert "Deploy di prova di origin/prova" in capsys.readouterr().out
    assert amb.timbra(1, sha, ref="") == 0
    assert "albero di lavoro" in capsys.readouterr().out
    assert "## Versione" not in amb.changelog_remoto()
    assert amb.timbra(0, sha) == timbro.USO
    assert amb.timbra(1, "abc") == timbro.USO
    assert amb.timbra(1, sha, aggiornata="ieri") == timbro.USO
    assert amb.timbra(1, "f" * 40) == timbro.ERRORE_GIT


def test_sha_non_su_main(amb):
    amb.autore.git("switch", "-q", "-c", "ramo")
    amb.autore.scrivi("backend/src/app.py", "x = 12\n")
    sha = amb.autore.commit("sul ramo")
    amb.autore.git("push", "-q", "origin", "ramo")
    amb.autore.git("switch", "-q", "main")
    amb.pubblicatore.git("fetch", "-q", "origin")
    assert amb.timbra(1, sha) == timbro.ERRORE_GIT


def test_checkout_dell_utente_intatto_e_worktree_rimossi(amb, monkeypatch):
    sha = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): _frammento("Pulito.")})
    pubblicatore = amb.pubblicatore
    pubblicatore.scrivi("lavoro-in-corso.txt", "non toccare\n")
    testa = pubblicatore.git("rev-parse", "HEAD")
    stato = pubblicatore.git("status", "--porcelain")

    def esplode(*argomenti, **opzioni):
        raise RuntimeError("guasto simulato")

    originale = timbro.raccogli
    monkeypatch.setattr(timbro, "raccogli", esplode)
    with pytest.raises(RuntimeError):
        amb.timbra(1, sha)
    monkeypatch.setattr(timbro, "raccogli", originale)
    assert timbro.PREFISSO_WORKTREE not in pubblicatore.git("worktree", "list", "--porcelain")
    assert amb.timbra(1, sha) == 0
    assert pubblicatore.git("rev-parse", "HEAD") == testa
    assert pubblicatore.git("status", "--porcelain") == stato
    elenco = pubblicatore.git("worktree", "list", "--porcelain")
    assert timbro.PREFISSO_WORKTREE not in elenco


def test_avviso_per_commit_senza_frammento(amb, capsys):
    sha = amb.pubblica(**{"backend__src__app.py": "x = 13\n"})
    assert amb.timbra(1, sha) == 0
    amb.pubblica(**{"backend__src__app.py": "x = 14\n"})
    sha = amb.pubblica(**{FRAMMENTO_A.replace("/", "__"): _frammento("Con frammento."),
                          "backend__src__app.py": "x = 15\n"})
    capsys.readouterr()
    assert amb.timbra(2, sha) == 0
    uscita = capsys.readouterr().out
    assert uscita.count("commit senza frammento di changelog") == 1
