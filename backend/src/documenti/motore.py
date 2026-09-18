"""Composizione dei documenti delle pratiche con Typst.

Un modello e' una cartella in `modelli/`: `modulo.typ` piu' le immagini delle
pagine. Il modulo riceve i dati come JSON in `sys.inputs.dati`; i binari (per
ora la firma) arrivano come file e il loro percorso sta in `dati.allegati`.
I file comuni a tutti i modelli stanno in `modelli/_comune/`: la composizione li
copia accanto al modulo, che li importa con `#import "/_comune/..."`.

Typst legge solo file sotto la radice indicata e il container dell'API e' in
sola lettura tranne /tmp: gli asset del modello si copiano una volta in una
cache sotto la cartella temporanea, e ogni composizione scrive i propri allegati
in una sottocartella che cancella alla fine. I font vengono solo da `font/`,
mai dal sistema: lo stesso PDF su Windows e nel container.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import threading
import uuid
from pathlib import Path

import typst

from src.documenti.esecuzione import compila_pdf

CARTELLA_MODELLI = Path(__file__).parent / "modelli"
CARTELLA_FONT = Path(__file__).parent / "font"
FILE_MODULO = "modulo.typ"
CARTELLA_COMUNE = "_comune"
# PDF/A-2b: archiviabile, font incorporati, ammette la trasparenza della firma.
STANDARD_PDF = ["a-2b"]
_NOME_VALIDO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_FIRME_IMMAGINE = (
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
)
_blocco_cache = threading.Lock()


class ModelloAssente(LookupError):
    """Il modello richiesto non esiste o non ha `modulo.typ`."""


class ComposizioneFallita(RuntimeError):
    """Typst ha rifiutato il modello o i dati."""


def estensione_immagine(contenuto: bytes | None) -> str | None:
    """Il formato di un'immagine dai primi byte; None se non e' un formato che Typst legge."""
    if not contenuto:
        return None
    for firma, estensione in _FIRME_IMMAGINE:
        if contenuto.startswith(firma):
            return estensione
    if contenuto[:4] == b"RIFF" and contenuto[8:12] == b"WEBP":
        return "webp"
    return None


def _impronta(*cartelle: Path) -> str:
    """Cambia quando cambia un file del modello o dei comuni: la cache non resta mai vecchia."""
    impronta = hashlib.sha256()
    for cartella in cartelle:
        for file in sorted(p for p in cartella.rglob("*") if p.is_file()):
            stato = file.stat()
            nome = f"{cartella.name}/{file.relative_to(cartella).as_posix()}"
            impronta.update(f"{nome}:{stato.st_size}:{stato.st_mtime_ns}\n".encode())
    return impronta.hexdigest()[:16]


def _radice(modello: str, cartella_modelli: Path | None) -> Path:
    if not _NOME_VALIDO.match(modello):
        raise ModelloAssente(modello)
    # Letta a ogni chiamata, non fissata come default: i test la sostituiscono.
    base = cartella_modelli or CARTELLA_MODELLI
    sorgente, comune = base / modello, base / CARTELLA_COMUNE
    if not (sorgente / FILE_MODULO).is_file():
        raise ModelloAssente(modello)
    cartelle = (sorgente, comune) if comune.is_dir() else (sorgente,)
    radice = Path(tempfile.gettempdir()) / "documenti-pratiche" / f"{modello}-{_impronta(*cartelle)}"
    with _blocco_cache:
        if not (radice / FILE_MODULO).is_file():
            parziale = radice.with_name(f"{radice.name}.{uuid.uuid4().hex}")
            shutil.copytree(sorgente, parziale)
            if comune.is_dir():
                shutil.copytree(comune, parziale / CARTELLA_COMUNE)
            try:
                parziale.rename(radice)
            except OSError:  # un altro processo l'ha creata nel frattempo
                shutil.rmtree(parziale, ignore_errors=True)
    return radice


def _componi(modello: str, dati: dict, allegati: dict[str, bytes] | None, cartella_modelli: Path | None, **uscita):
    radice = _radice(modello, cartella_modelli)
    lavoro = radice / f"richiesta-{uuid.uuid4().hex}"
    lavoro.mkdir()
    try:
        percorsi = {}
        for nome, contenuto in (allegati or {}).items():
            estensione = estensione_immagine(contenuto)
            if estensione is None:
                continue  # binario illeggibile: il modello mostra il riquadro vuoto
            (lavoro / f"{nome}.{estensione}").write_bytes(contenuto)
            percorsi[nome] = f"{lavoro.name}/{nome}.{estensione}"
        ingressi = {"dati": json.dumps({**dati, "allegati": percorsi}, ensure_ascii=False, default=str)}
        font = [str(CARTELLA_FONT)] if CARTELLA_FONT.is_dir() else []
        try:
            opzioni = dict(input=str(radice / FILE_MODULO), root=str(radice), font_paths=font,
                           ignore_system_fonts=True, sys_inputs=ingressi, **uscita)
            if uscita.get("format") == "pdf":
                return compila_pdf(opzioni)
            return typst.compile(**opzioni)
        except typst.TypstError as errore:
            raise ComposizioneFallita(str(errore)) from errore
        except (subprocess.SubprocessError, OSError, ValueError):
            raise ComposizioneFallita("Il compilatore PDF non ha completato la richiesta.") from None
    finally:
        shutil.rmtree(lavoro, ignore_errors=True)


def componi_pdf(modello: str, dati: dict, allegati: dict[str, bytes] | None = None,
                *, cartella_modelli: Path | None = None) -> bytes:
    """Il documento compilato, in PDF/A-2b."""
    return _componi(modello, dati, allegati, cartella_modelli, format="pdf", pdf_standards=STANDARD_PDF)


def componi_png(modello: str, dati: dict, allegati: dict[str, bytes] | None = None,
                *, ppi: int = 72, cartella_modelli: Path | None = None) -> list[bytes]:
    """Una PNG per pagina: serve a controllare a occhio la posizione dei campi."""
    pagine = _componi(modello, dati, allegati, cartella_modelli, format="png", ppi=ppi)
    return pagine if isinstance(pagine, list) else [pagine]
