"""Motore dei documenti: composizione Typst, allegati, cache dei modelli, errori."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from src.documenti import motore
from tests.support.immagini import png_pieno

MODELLO_PROVA = Path(__file__).parents[1] / "support" / "modelli" / "prova"


@pytest.fixture
def modelli(tmp_path):
    cartella = tmp_path / "modelli"
    shutil.copytree(MODELLO_PROVA, cartella / "prova")
    return cartella


def test_pdf_archiviabile_da_un_modello_con_sfondo(modelli):
    pdf = motore.componi_pdf("prova", {"nome": "Maria Della Valle"}, cartella_modelli=modelli)
    assert pdf.startswith(b"%PDF-")
    assert b"pdfaid" in pdf  # metadati PDF/A


def test_una_png_per_pagina_e_la_firma_cambia_la_resa(modelli):
    senza = motore.componi_png("prova", {"nome": "Maria"}, cartella_modelli=modelli, ppi=40)
    con = motore.componi_png("prova", {"nome": "Maria"}, {"firma": png_pieno()}, cartella_modelli=modelli, ppi=40)
    assert len(senza) == len(con) == 2
    assert con[0] != senza[0] and con[1] == senza[1]


def test_un_binario_che_non_e_un_immagine_non_rompe_il_documento(modelli):
    senza = motore.componi_png("prova", {"nome": "Maria"}, cartella_modelli=modelli, ppi=40)
    illeggibile = motore.componi_png("prova", {"nome": "Maria"}, {"firma": b"non-e-un-immagine"}, cartella_modelli=modelli, ppi=40)
    assert illeggibile == senza


def test_la_cartella_di_lavoro_non_resta_e_la_cache_segue_il_modello(modelli):
    motore.componi_pdf("prova", {"nome": "Maria"}, {"firma": png_pieno()}, cartella_modelli=modelli)
    cache = Path(tempfile.gettempdir()) / "documenti-pratiche"
    radici = [p for p in cache.glob("prova-*") if p.is_dir()]
    assert radici and not any(p.name.startswith("richiesta-") for r in radici for p in r.iterdir())

    prima = motore.componi_png("prova", {"nome": "Maria"}, cartella_modelli=modelli, ppi=40)
    modulo = modelli / "prova" / "modulo.typ"
    modulo.write_text(modulo.read_text(encoding="utf-8").replace("Seconda pagina", "Pagina due, modificata"), encoding="utf-8")
    dopo = motore.componi_png("prova", {"nome": "Maria"}, cartella_modelli=modelli, ppi=40)
    assert dopo[1] != prima[1]  # nessuna cache vecchia


def test_i_file_comuni_si_importano_e_la_cache_li_segue(modelli):
    comune = modelli / motore.CARTELLA_COMUNE
    comune.mkdir()
    (comune / "saluto.typ").write_text('#let saluto = "Buongiorno"', encoding="utf-8")
    modulo = modelli / "prova" / "modulo.typ"
    righe = ['#import "/_comune/saluto.typ": saluto', modulo.read_text(encoding="utf-8"), "#saluto"]
    modulo.write_text("\n".join(righe), encoding="utf-8")
    prima = motore.componi_png("prova", {"nome": "Maria"}, cartella_modelli=modelli, ppi=40)
    (comune / "saluto.typ").write_text('#let saluto = "Buonasera a tutte e a tutti"', encoding="utf-8")
    dopo = motore.componi_png("prova", {"nome": "Maria"}, cartella_modelli=modelli, ppi=40)
    assert dopo[0] == prima[0] and dopo[1] != prima[1]


def test_un_modello_non_si_chiama_come_la_cartella_comune(modelli):
    (modelli / motore.CARTELLA_COMUNE).mkdir()
    (modelli / motore.CARTELLA_COMUNE / motore.FILE_MODULO).write_text("Non sono un modello", encoding="utf-8")
    with pytest.raises(motore.ModelloAssente):
        motore.componi_pdf(motore.CARTELLA_COMUNE, {}, cartella_modelli=modelli)


@pytest.mark.parametrize("nome", ["assente", "../prova", "Prova", "prova/../prova", ""])
def test_modello_assente_o_nome_non_valido(modelli, nome):
    with pytest.raises(motore.ModelloAssente):
        motore.componi_pdf(nome, {}, cartella_modelli=modelli)


def test_un_errore_del_modello_diventa_composizione_fallita(modelli):
    with pytest.raises(motore.ComposizioneFallita):
        motore.componi_pdf("prova", {}, cartella_modelli=modelli)  # manca dati.nome


@pytest.mark.parametrize("errore", [
    subprocess.TimeoutExpired("compilatore", 60, output=b"dato privato"),
    subprocess.CalledProcessError(-9, "compilatore", stderr=b"dato privato"),
])
def test_compilatore_interrotto_non_espone_dati_e_rimuove_gli_allegati(modelli, monkeypatch, errore):
    def fallisce(_):
        raise errore

    monkeypatch.setattr(motore, "compila_pdf", fallisce)
    with pytest.raises(motore.ComposizioneFallita) as esito:
        motore.componi_pdf("prova", {"nome": "dato privato"}, {"firma": png_pieno()}, cartella_modelli=modelli)
    assert "dato privato" not in str(esito.value)
    assert not list(motore._radice("prova", modelli).glob("richiesta-*"))


@pytest.mark.parametrize(("contenuto", "atteso"), [
    (b"\x89PNG\r\n\x1a\nresto", "png"),
    (b"\xff\xd8\xff\xe0resto", "jpg"),
    (b"GIF89aresto", "gif"),
    (b"RIFF\x00\x00\x00\x00WEBPVP8 ", "webp"),
    (b"%PDF-1.7", None),
    (b"", None),
    (None, None),
])
def test_riconoscimento_del_formato_immagine(contenuto, atteso):
    assert motore.estensione_immagine(contenuto) == atteso
