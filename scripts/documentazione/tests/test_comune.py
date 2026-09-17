from __future__ import annotations

import pytest

from comune import (ancore, corrisponde, elenco_file, normalizza, redigi, risolvi, slug_github,
                    sospetti)


@pytest.mark.parametrize(("percorso", "pattern", "atteso"), [
    ("backend/src/auth/accesso.py", "backend/src/auth/**", True),
    ("backend/src/auth/x/y.py", "backend/src/auth/**", True),
    ("backend/src/authx/y.py", "backend/src/auth/**", False),
    ("backend/src/pratiche_stati/models.py", "backend/src/pratiche_*/**", True),
    ("backend/src/pratiche/models.py", "backend/src/pratiche_*/**", False),
    ("frontend/src/components/SchedaAzienda.jsx", "frontend/src/components/*Azienda*.jsx", True),
    ("frontend/src/components/sub/SchedaAzienda.jsx", "frontend/src/components/*Azienda*.jsx", False),
    ("Dockerfile", "**/Dockerfile", True),
    ("backend/Dockerfile", "**/Dockerfile", True),
    ("backend/dockerfile", "**/Dockerfile", False),
    ("a/b.py", "a/?.py", True),
])
def test_glob(percorso, pattern, atteso):
    assert corrisponde(percorso, pattern) is atteso


@pytest.mark.parametrize("pattern", ["backend/src/{auth,mfa}/**", "a/[ab].py"])
def test_glob_rifiuta_graffe_e_classi(pattern):
    with pytest.raises(ValueError):
        corrisponde("x", pattern)


@pytest.mark.parametrize(("titolo", "slug"), [
    ("Versione 12 — 17/09/2026 18:40", "versione-12--17092026-1840"),
    ("Ruoli 0–6", "ruoli-06"),
    ("Cos'è la piattaforma", "cosè-la-piattaforma"),
    ("Novità e correzioni", "novità-e-correzioni"),
    ("Limiti noti", "limiti-noti"),
    ("Il file `api.md`", "il-file-apimd"),
    ("Vedi [la guida](x.md)", "vedi-la-guida"),
    ("snake_case e trattini-uniti", "snake_case-e-trattini-uniti"),
])
def test_slug_github(titolo, slug):
    assert slug_github(titolo) == slug


def test_slug_normalizza_i_caratteri_scomposti():
    assert slug_github("Novità") == "novità"


def test_ancore_con_duplicati_e_codice():
    testo = "# Titolo\n## Uso\n```\n## Non conta\n```\n## Uso\n<a name=\"manuale\"></a>\n"
    assert ancore(testo) == {"titolo", "uso", "uso-1", "manuale"}


def test_risolvi():
    assert risolvi("docs/tecnica/a.md", "../funzionale/b.md") == "docs/funzionale/b.md"
    assert risolvi("docs/a.md", "../../fuori.md") is None
    assert risolvi("README.md", "docs/") == "docs"


def test_redigi_non_usa_parentesi_angolari():
    """In Markdown [dominio] sarebbe un tag HTML: GitHub lo scarterebbe
    portandosi via proprio il testo redatto."""
    reso = redigi("host collaudo.rete.lan, ip 192.0.2.10, posta a nome@esempio.org, /srv/app/x")
    assert "<" not in reso and ">" not in reso
    assert reso.count("[") == 4


@pytest.mark.parametrize(("testo", "atteso"), [
    ("host collaudo.rete.local", "host [dominio]"),
    ("host server.rete.lan", "host [dominio]"),
    ("copia in /data/app/shared/x", "copia in [percorso-server]"),
    ("copia in /mnt/deploy/x", "copia in [percorso-server]"),
    ("non backend/var/email_dev", "non backend/var/email_dev"),
    ("loopback 127.0.0.1 e altro 127.53.0.9", "loopback 127.0.0.1 e altro [ip]"),
    ("ipv6 fd00:abcd::12", "ipv6 [ip]"),
    ("ora 2026-09-17T18:40:00+02:00", "ora 2026-09-17T18:40:00+02:00"),
    ("mysql://utente:pa/ss@host.interno.it/db", "mysql://[credenziali]@[dominio]/db"),
    ("utente root:Segreta.2026", "utente [credenziali]"),
    ("posta noreply@ersaf", "posta [email]"),
    ("modulo src.config e file api.md", "modulo src.config e file api.md"),
    ("esempio.it e example.org restano", "esempio.it e example.org restano"),
])
def test_redigi_casi(testo, atteso):
    assert redigi(testo) == atteso


@pytest.mark.parametrize(("testo", "categorie"), [
    ("scrivi a nome.cognome@esempio.org", []),
    ("scrivi a nome.cognome@azienda.it", ["indirizzo email"]),
    ("collaudo su esempio.ersaf.it", ["dominio dell'ente"]),
    ("host collaudo.rete.local", ["nome di rete interna"]),
    ("react.dev e github.com nei link", []),
    ("il server risponde su 192.0.2.10", ["indirizzo IP"]),
    ("loopback 127.0.0.1", []),
    ("percorso /srv/app/shared", ["percorso del server"]),
    ("versione 1.2.3 alle 18:40:00", []),
])
def test_sospetti(testo, categorie):
    assert [c for c, _ in sospetti(testo)] == categorie


def test_normalizza():
    assert normalizza("\ufeffa\r\nb\rc\n") == "a\nb\nc\n"


def test_elenco_file_segue_git(repo):
    repo.scrivi("tracciato.md", "x")
    repo.scrivi(".gitignore", "ignorato.md\n")
    repo.commit()
    repo.scrivi("nuovo.md", "x")
    repo.scrivi("ignorato.md", "x")
    repo.cancella("tracciato.md")
    assert elenco_file(repo.percorso) == [".gitignore", "nuovo.md"]
