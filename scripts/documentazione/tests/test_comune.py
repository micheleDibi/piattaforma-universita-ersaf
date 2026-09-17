from __future__ import annotations

import pytest

from comune import ancore, corrisponde, elenco_file, normalizza, redigi, risolvi, slug_github


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


def test_redigi():
    testo = ("scrivi a nome.cognome@esempio.it o vai su https://collaudo.azienda.it, "
             "db mysql://utente:segreta@db/x, ip 192.0.2.10, locale 127.0.0.1, "
             "localhost e example.com restano")
    atteso = ("scrivi a <email> o vai su https://<dominio>, db mysql://<credenziali>@db/x, "
              "ip <ip>, locale 127.0.0.1, localhost e example.com restano")
    assert redigi(testo) == atteso


def test_normalizza():
    assert normalizza("﻿a\r\nb\rc\n") == "a\nb\nc\n"


def test_elenco_file_segue_git(repo):
    repo.scrivi("tracciato.md", "x")
    repo.scrivi(".gitignore", "ignorato.md\n")
    repo.commit()
    repo.scrivi("nuovo.md", "x")
    repo.scrivi("ignorato.md", "x")
    repo.cancella("tracciato.md")
    assert elenco_file(repo.percorso) == [".gitignore", "nuovo.md"]
