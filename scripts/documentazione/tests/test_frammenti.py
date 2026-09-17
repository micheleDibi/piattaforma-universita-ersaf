from __future__ import annotations

import pytest

import frammenti
from conftest import FRAMMENTO_VALIDO

NOME = "2026-09-17-prova.md"


def errori(testo: str, nome: str = NOME) -> list[str]:
    with pytest.raises(frammenti.FrammentoNonValido) as info:
        frammenti.analizza(nome, testo)
    return info.value.errori


def test_frammento_valido():
    f = frammenti.analizza(NOME, FRAMMENTO_VALIDO)
    assert f.pr == 7 and not f.incompatibile
    assert [(v.parte, v.tipo) for v in f.voci] == [
        (frammenti.NOVITA, "aggiunto"), (frammenti.TECNICO, "modificato")]


def test_crlf_e_bom_accettati():
    frammenti.analizza(NOME, "﻿" + FRAMMENTO_VALIDO.replace("\n", "\r\n"))


@pytest.mark.parametrize("nome", [
    "2026-9-17-prova.md", "2026-02-30-prova.md", "2026-09-17-Prova.md", "2026-09-17-prova.txt",
    "2026-09-17-prova--doppia.md", "2026-09-17-" + "a" * 80 + ".md", "prova.md",
])
def test_nomi_non_validi(nome):
    assert frammenti.errori_nome(nome)


def test_frontmatter_obbligatorio():
    assert any("frontmatter" in e for e in errori("## Dettagli tecnici\n\n- aggiunto: x\n"))


@pytest.mark.parametrize(("riga", "parola"), [
    ("pr: 017", "pr"), ("pr: 1_000", "pr"), ("pr: 0", "pr"), ("pr: sette", "pr"),
    ("incompatibile: no", "incompatibile"), ("incompatibile: yes", "incompatibile"),
    ("autore: io", "non ammessa"),
])
def test_frontmatter_rigoroso(riga, parola):
    testo = FRAMMENTO_VALIDO.replace("pr: 7", riga)
    assert any(parola in e for e in errori(testo))


def test_frontmatter_legge_come_yaml():
    """Sui valori ammessi il parser a libreria standard coincide con YAML."""
    yaml = pytest.importorskip("yaml")
    for blocco, atteso in [("pr: 58  # la PR\nincompatibile: true", (58, True)),
                           ("incompatibile: false", (None, False)), ("", (None, False))]:
        testo = f"---\n{blocco}\n---\n\n## Dettagli tecnici\n\n- aggiunto: x\n"
        f = frammenti.analizza(NOME, testo)
        dati = yaml.safe_load(blocco) or {}
        assert (f.pr, f.incompatibile) == atteso == (dati.get("pr"), dati.get("incompatibile", False))


def test_i_valori_che_yaml_interpreta_male_sono_rifiutati():
    yaml = pytest.importorskip("yaml")
    assert yaml.safe_load("incompatibile: no") == {"incompatibile": False}
    assert yaml.safe_load("pr: 017") == {"pr": 15}
    for riga in ("incompatibile: no", "pr: 017"):
        errori(FRAMMENTO_VALIDO.replace("pr: 7", riga))


@pytest.mark.parametrize(("corpo", "parola"), [
    ("## Novità\n\n- aggiunto: x\n", "titolo non ammesso"),
    ("# Novità e correzioni\n\n- aggiunto: x\n", "titolo non ammesso"),
    ("## Novità e correzioni\n\n- nuovo: x\n", "tipo 'nuovo'"),
    ("## Novità e correzioni\n\n- Aggiunto: x\n", "riga non ammessa"),
    ("## Novità e correzioni\n\ntesto libero\n", "riga non ammessa"),
    ("- aggiunto: x\n", "fuori da una sezione"),
    ("## Novità e correzioni\n\n- aggiunto: x\n\n## Novità e correzioni\n\n- corretto: y\n", "due volte"),
    ("## Dettagli tecnici\n\n", "non ha voci"),
    ("", "nessuna voce"),
    ("## Novità e correzioni\n\n- aggiunto: Nuovo campo `diploma`\n", "apici inversi"),
    ("## Dettagli tecnici\n\n- aggiunto: vedi [guida](../../docs/x.md)\n", "solo link assoluti"),
    ("## Dettagli tecnici\n\n- aggiunto: ![logo](logo.png)\n", "solo link assoluti"),
    ("## Dettagli tecnici\n\n- aggiunto: x\n\n[rif]: docs/x.md\n", "solo link assoluti"),
])
def test_corpo_non_valido(corpo, parola):
    assert any(parola in e for e in errori(f"---\n---\n\n{corpo}")), errori(f"---\n---\n\n{corpo}")


def test_link_assoluti_e_continuazioni():
    testo = ("---\n---\n\n## Dettagli tecnici\n\n- modificato: prima riga\n"
             "  seconda riga con [link](https://example.com/x)\n")
    f = frammenti.analizza(NOME, testo)
    assert f.voci[0].testo == "prima riga seconda riga con [link](https://example.com/x)"


def test_incompatibile_richiede_voce_tecnica():
    testo = "---\nincompatibile: true\n---\n\n## Novità e correzioni\n\n- rimosso: x\n"
    assert any("incompatibile" in e for e in errori(testo))


def test_e_frammento():
    assert frammenti.e_frammento("changelog/non-pubblicato/2026-09-17-x.md")
    assert not frammenti.e_frammento("changelog/non-pubblicato/LEGGIMI.md")
    assert not frammenti.e_frammento("changelog/non-pubblicato/sotto/2026-09-17-x.md")
    assert not frammenti.e_frammento("changelog/MODELLO.md")


def test_componi():
    a = frammenti.analizza("2026-09-18-b.md", FRAMMENTO_VALIDO)
    b = frammenti.analizza("2026-09-17-a.md", "---\nincompatibile: true\n---\n\n"
                           "## Novità e correzioni\n\n- corretto: Errore corretto.\n- aggiunto: Prima.\n\n"
                           "## Dettagli tecnici\n\n- rimosso: Campo tolto.\n")
    assert frammenti.componi([a, b]) == (
        "### Novità e correzioni\n\n"
        "**Aggiunto**\n\n- Prima.\n- Negli elenchi compare lo stato di verifica dei contatti. (PR #7)\n\n"
        "**Corretto**\n\n- Errore corretto.\n\n"
        "### Dettagli tecnici\n\n"
        "**Modificato**\n\n- `GET /clienti/` restituisce un campo in più. (PR #7)\n\n"
        "**Rimosso**\n\n- **Incompatibile.** Campo tolto."
    )


def test_componi_senza_frammenti():
    assert frammenti.componi([]) == "Nessuna modifica documentata."
