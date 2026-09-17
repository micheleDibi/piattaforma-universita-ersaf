from __future__ import annotations

import pytest

pytest.importorskip("yaml")

import controlla  # noqa: E402
from conftest import FRAMMENTO_VALIDO  # noqa: E402

MAPPA = """regole:
  - nome: Accesso
    percorsi:
      - "backend/src/auth/**"
    documenti:
      - docs/tecnica/sicurezza.md
      - docs/funzionale/accesso.md
"""
FRAMMENTO = "changelog/non-pubblicato/2026-09-17-prova.md"


def base(repo):
    repo.scrivi("docs/mappa-documentazione.yml", MAPPA)
    repo.scrivi("docs/tecnica/sicurezza.md", "# Sicurezza\n\n## Limiti noti\n")
    repo.scrivi("docs/funzionale/accesso.md", "# Accesso\n")
    repo.scrivi("backend/src/auth/accesso.py", "x = 1\n")
    repo.scrivi("backend/src/altro/modulo.py", "y = 1\n")
    repo.scrivi("db/README.md", "# DB\n")
    repo.scrivi("changelog/non-pubblicato/LEGGIMI.md", "# Frammenti\n")
    repo.scrivi("changelog/non-pubblicato/2026-09-01-vecchio.md", FRAMMENTO_VALIDO)
    repo.scrivi("CHANGELOG.md", "# Registro\n")
    return repo.commit("base")


def pr(repo, sha, etichette=""):
    errori = controlla.controlla_pr(repo.percorso, sha, "HEAD", controlla._etichette(etichette))
    return [e.titolo for e in errori]


@pytest.fixture
def ramo(repo):
    sha = base(repo)
    repo.git("switch", "-q", "-c", "pr")
    return sha


# --- i quattro scenari e le etichette ----------------------------------------
def test_codice_con_frammento_e_documento(repo, ramo):
    repo.scrivi("backend/src/auth/accesso.py", "x = 2\n")
    repo.scrivi(FRAMMENTO, FRAMMENTO_VALIDO)
    repo.scrivi("docs/funzionale/accesso.md", "# Accesso\n\nAggiornato.\n")
    repo.commit()
    assert pr(repo, ramo) == []


def test_codice_con_frammento_senza_documento(repo, ramo):
    repo.scrivi("backend/src/auth/accesso.py", "x = 2\n")
    repo.scrivi(FRAMMENTO, FRAMMENTO_VALIDO)
    repo.commit()
    assert pr(repo, ramo) == ["Documentazione da controllare"]
    assert pr(repo, ramo, "documentazione-invariata") == []
    [errore] = controlla.controlla_pr(repo.percorso, ramo, "HEAD", set())
    assert "docs/tecnica/sicurezza.md, docs/funzionale/accesso.md" in errore.messaggio
    assert "backend/src/auth/accesso.py" in errore.messaggio


def test_codice_senza_frammento_con_documento(repo, ramo):
    repo.scrivi("backend/src/auth/accesso.py", "x = 2\n")
    repo.scrivi("docs/tecnica/sicurezza.md", "# Sicurezza\n\n## Limiti noti\n\nAltro.\n")
    repo.commit()
    assert pr(repo, ramo) == ["Frammento di changelog mancante"]
    assert pr(repo, ramo, "senza-changelog") == []


def test_codice_senza_frammento_senza_documento(repo, ramo):
    repo.scrivi("backend/src/auth/accesso.py", "x = 2\n")
    repo.commit()
    assert pr(repo, ramo) == ["Frammento di changelog mancante", "Documentazione da controllare"]
    assert pr(repo, ramo, "senza-changelog, documentazione-invariata") == []


# --- casi particolari --------------------------------------------------------
def test_codice_non_mappato_richiede_solo_il_frammento(repo, ramo):
    repo.scrivi("backend/src/altro/modulo.py", "y = 2\n")
    repo.commit()
    assert pr(repo, ramo) == ["Frammento di changelog mancante"]


@pytest.mark.parametrize("percorso", ["docs/tecnica/sicurezza.md", "db/README.md", "README.md",
                                      "scripts/qualcosa.ps1"])
def test_file_che_non_richiedono_nulla(repo, ramo, percorso):
    repo.scrivi(percorso, "# Cambiato\n")
    repo.commit()
    assert pr(repo, ramo) == []


def test_frammento_non_valido_non_basta(repo, ramo):
    repo.scrivi("backend/src/altro/modulo.py", "y = 2\n")
    repo.scrivi(FRAMMENTO, "---\n---\n\ntesto libero\n")
    repo.commit()
    assert pr(repo, ramo) == ["Frammento di changelog mancante"]


def test_modificare_un_frammento_esistente_basta(repo, ramo):
    repo.scrivi("backend/src/altro/modulo.py", "y = 2\n")
    repo.scrivi("changelog/non-pubblicato/2026-09-01-vecchio.md",
                FRAMMENTO_VALIDO.replace("un campo in più", "due campi in più"))
    repo.commit()
    assert pr(repo, ramo) == []


def test_changelog_protetto(repo, ramo):
    repo.scrivi("CHANGELOG.md", "# Registro\n\nA mano.\n")
    repo.commit()
    assert pr(repo, ramo) == ["CHANGELOG modificato"]


def test_changelog_nuovo_ammesso_se_manca_sulla_base(repo):
    repo.scrivi("README.md", "x\n")
    sha = repo.commit("senza changelog")
    repo.scrivi("CHANGELOG.md", "# Registro\n")
    repo.commit()
    assert controlla.controlla_pr(repo.percorso, sha, "HEAD", set()) == []


def test_cancellare_o_rinominare_un_frammento(repo, ramo):
    repo.cancella("changelog/non-pubblicato/2026-09-01-vecchio.md")
    repo.commit()
    assert pr(repo, ramo) == ["Frammento cancellato"]
    repo.scrivi("changelog/non-pubblicato/2026-09-02-rinominato.md", FRAMMENTO_VALIDO)
    repo.commit()
    assert pr(repo, ramo) == ["Frammento cancellato"]


def test_rinomina_di_codice_attiva_la_regola_anche_dal_percorso_vecchio(repo, ramo):
    (repo.percorso / "backend/src/nuovo").mkdir(parents=True)
    repo.git("mv", "backend/src/auth/accesso.py", "backend/src/nuovo/accesso.py")
    repo.scrivi(FRAMMENTO, FRAMMENTO_VALIDO)
    repo.commit()
    assert pr(repo, ramo) == ["Documentazione da controllare"]


def test_main_avanzato_dopo_la_base(repo, ramo):
    """Come in GitHub Actions: HEAD è il merge del ramo su un main avanzato."""
    repo.scrivi("backend/src/altro/modulo.py", "y = 2\n")
    repo.commit("PR senza frammento")
    repo.git("switch", "-q", "main")
    repo.scrivi("changelog/non-pubblicato/2026-09-18-altra.md", FRAMMENTO_VALIDO)
    repo.scrivi("backend/src/auth/accesso.py", "x = 3\n")
    repo.commit("altra PR gia' unita")
    repo.git("switch", "-q", "--detach", "main")
    repo.git("merge", "-q", "--no-ff", "-m", "merge", "pr")
    # Con la base dell'evento il frammento dell'altra PR nasconderebbe l'errore
    # e la sua modifica al codice produrrebbe un errore non suo.
    assert pr(repo, ramo) == ["Documentazione da controllare"]
    effettiva = controlla.base_effettiva(repo.percorso, ramo, "HEAD")
    assert effettiva == repo.git("rev-parse", "HEAD^1")
    assert pr(repo, effettiva) == ["Frammento di changelog mancante"]


def test_base_effettiva_senza_merge(repo, ramo):
    assert controlla.base_effettiva(repo.percorso, ramo, "HEAD") == ramo


# --- frammenti e link --------------------------------------------------------
def test_controllo_frammenti(repo):
    repo.scrivi("changelog/non-pubblicato/LEGGIMI.md", "# x\n")
    repo.scrivi("changelog/non-pubblicato/2026-09-17-buono.md", FRAMMENTO_VALIDO)
    repo.scrivi("changelog/non-pubblicato/2026-09-17-cattivo.md", "niente\n")
    repo.scrivi("changelog/non-pubblicato/note.txt", "x\n")
    file = sorted(p.relative_to(repo.percorso).as_posix() for p in repo.percorso.rglob("*") if p.is_file())
    errori = controlla.controlla_frammenti(repo.percorso, file)
    assert {e.file for e in errori} == {"changelog/non-pubblicato/2026-09-17-cattivo.md",
                                        "changelog/non-pubblicato/note.txt"}


def test_controllo_link(repo):
    repo.scrivi("docs/a.md", "# Titolo A\n\n## Limiti noti\n")
    repo.scrivi("docs/codice.py", "x\n")
    repo.scrivi("README.md", "\n".join([
        "# Radice",
        "[ok](docs/a.md) [ancora](docs/a.md#limiti-noti) [cartella](docs/) [interna](#radice)",
        "[esterno](https://example.com/x) [posta](mailto:x@example.invalid) [riga](docs/codice.py#L3)",
        "`[nel codice](manca.md)`",
        "```",
        "[nel blocco](manca.md)",
        "```",
        "[rotto](docs/b.md)",
        "[ancora rotta](docs/a.md#assente)",
        "[fuori](../fuori.md)",
        "[maiuscole](docs/A.md)",
        "[rif]: docs/manca.md",
        "[ancora su codice](docs/codice.py#funzione)",
    ]) + "\n")
    file = ["README.md", "docs/a.md", "docs/codice.py"]
    errori = controlla.controlla_link(repo.percorso, file)
    assert [(e.riga, e.titolo) for e in errori] == [
        (8, "Link rotto"), (9, "Ancora rotta"), (10, "Link rotto"), (11, "Link rotto"),
        (12, "Link rotto"), (13, "Link rotto")]


# --- riga di comando ---------------------------------------------------------
def test_riga_di_comando(repo, ramo, capsys, monkeypatch):
    repo.scrivi("backend/src/auth/accesso.py", "x = 2\n")
    repo.commit()
    argomenti = ["pr", "--base", ramo, "--etichette", "senza-changelog"]
    assert controlla.esegui(argomenti, radice=repo.percorso) == 1
    assert "ERRORE" in capsys.readouterr().out
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    assert controlla.esegui(argomenti, radice=repo.percorso) == 1
    assert capsys.readouterr().out.startswith("::error title=Documentazione da controllare::")
    assert controlla.esegui(argomenti + ["--merge"], radice=repo.percorso) == 1
    capsys.readouterr()
    assert controlla.esegui(["pr", "--base", "inesistente"], radice=repo.percorso) == 2
