"""Aiuti dei test EduNews24: orologio finto, JSON a monte inventati, fonte finta.

Solo host inventati: `.invalid` (RFC 6761) ed example.org.
"""

from __future__ import annotations

import threading
from collections.abc import Sequence

import httpx

from src.edunews24.client import ErroreEduNews24, RispostaEduNews24

HOST_SITO = "edunews24.invalid"
HOST_MEDIA = "media.edunews24.invalid"
URL_BASE = f"https://{HOST_SITO}/api/v1"
CONTATTO = "https://example.org/contatti"
PROFILO_ELENCO = "public, max-age=60, s-maxage=300, stale-while-revalidate=300, stale-if-error=86400"
PROFILO_STATICO = "public, max-age=900, s-maxage=3600, stale-while-revalidate=3600, stale-if-error=86400"
PROFILO_STANTIO = "public, max-age=30, s-maxage=60"
# 28/09/2026 08:00 UTC.
PARETE_FISSA = 1_790_582_400.0


class OrologioFinto:
    """Orologio che avanza solo quando lo dice il test."""

    def __init__(self, monotono: float = 1000.0, parete: float = PARETE_FISSA) -> None:
        self._monotono = monotono
        self._parete = parete
        self._lock = threading.Lock()

    def monotono(self) -> float:
        with self._lock:
            return self._monotono

    def parete(self) -> float:
        with self._lock:
            return self._parete

    def avanza(self, secondi: float) -> None:
        with self._lock:
            self._monotono += secondi
            self._parete += secondi


def articolo(id: int = 1, *, titolo: str = "Titolo inventato", categoria: str = "scuola",
             immagine: str | None = f"https://{HOST_MEDIA}/a.jpg", video: dict | None = None,
             **altri) -> dict:
    voce = {
        "type": "article",
        "id": id,
        "slug": f"notizia-{id}",
        "url": f"https://{HOST_SITO}/{categoria}/notizia-{id}",
        "title": titolo,
        "title_summary": None,
        "excerpt": "Sintesi inventata",
        "summary": None,
        "category": {"slug": categoria, "name": categoria.capitalize(), "color": "#000000",
                     "url": f"https://{HOST_SITO}/{categoria}"},
        "secondary_categories": [],
        "image_url": immagine,
        "thumbnail_url": None,
        "video": video,
        "published_at": "2026-09-28T10:00:00+02:00",
        "tags": [],
        "author": {"name": "Redazione di prova"},
    }
    voce.update(altri)
    return voce


def video(url: str = f"https://{HOST_MEDIA}/v.mp4", *, mime: str | None = "video/mp4",
          copertina: str | None = f"https://{HOST_MEDIA}/c.jpg", durata: object = 125) -> dict:
    return {"url": url, "mime_type": mime, "thumbnail_url": copertina, "duration_seconds": durata}


def opportunita(id: int = 1, *, tipo: str = "selezione-personale", titolo: str = "Annuncio inventato",
                dettagli: dict | None = None, **altri) -> dict:
    sezione = "interpelli" if tipo == "interpello" else tipo
    voce = {
        "type": tipo,
        "id": id,
        "slug": f"voce-{id}",
        "url": f"https://{HOST_SITO}/{sezione}/voce-{id}",
        "title": titolo,
        "summary": "Descrizione inventata",
        "section": {"slug": sezione, "name": "Sezione", "color": "#000000", "url": f"https://{HOST_SITO}/{sezione}"},
        "published_at": "2026-09-27T10:00:00+02:00",
        "updated_at": None,
        "deadline_on": None if tipo == "interpello" else "2026-10-05",
        "deadline_at": None,
        "status": None if tipo == "interpello" else "open",
        "regions": [{"slug": "lombardia", "name": "Lombardia"}],
        "national": False,
        "details": dettagli if dettagli is not None else (
            {"official_title": "Avviso di interpello di prova", "competition_class": "A022", "province": "Provincia di prova",
             "city": "Città di prova"} if tipo == "interpello" else
            {"official_title": "Avviso di prova", "code": None, "position": "Figura di prova",
             "positions_count": 3, "procedure_type": None, "categories": [], "sectors": [],
             "organizations": ["Ente di prova"], "locations": ["Lombardia", "Città di prova"],
             "salary_min": None, "salary_max": None}),
    }
    voce.update(altri)
    return voce


def elenco(dati: list, next: str | None = None) -> dict:
    return {"data": dati, "meta": {"count": len(dati)},
            "links": {"self": f"{URL_BASE}/x", "first": None, "next": next}}


def link_next(percorso: str = "/articles", cursore: str = "c1", **filtri) -> str:
    query = "&".join([f"{k}={v}" for k, v in filtri.items()] + [f"cursor={cursore}"])
    return f"{URL_BASE}{percorso}?{query}"


def categorie(*slug: str) -> dict:
    slug = slug or ("scuola", "universita")
    return {"data": [{"slug": s, "name": s.capitalize(), "color": "#000000", "position": n,
                      "url": f"https://{HOST_SITO}/{s}", "secondary_categories": [], "links": {}}
                     for n, s in enumerate(slug, start=1)],
            "meta": {}, "links": {"self": f"{URL_BASE}/categories"}}


def problema(code: str, parametri: Sequence[str] = ()) -> dict:
    corpo = {"type": "https://example.org/errori", "title": "Errore", "status": 400,
             "detail": "Dettaglio a monte da non inoltrare", "code": code}
    if parametri:
        corpo["errors"] = [{"parameter": p, "detail": "non valido"} for p in parametri]
    return corpo


def risposta(corpo: dict | None = None, *, stato: int = 200, cache_control: str | None = PROFILO_ELENCO,
             etag: str | None = None, age: str | None = None, stantia: bool = False) -> RispostaEduNews24:
    return RispostaEduNews24(stato, corpo, etag, cache_control, age, stantia)


def risposta_http(stato: int = 200, corpo: bytes = b"", **intestazioni: str) -> httpx.Response:
    """Risposta httpx non ancora letta, come quella di una rete vera.

    Con `content=` httpx leggerebbe (e decomprimerebbe) il corpo subito: il
    client legge invece i byte grezzi in streaming.
    """
    headers = {nome.replace("_", "-"): valore for nome, valore in intestazioni.items()}
    return httpx.Response(stato, headers=headers, stream=httpx.ByteStream(corpo))


class FonteFinta:
    """Fonte programmabile: restituisce o solleva, nell'ordine, e registra le chiamate.

    Un elemento di `risposte` puo' essere una RispostaEduNews24, un
    ErroreEduNews24 (sollevato), un'altra eccezione (sollevata) o una funzione
    `(percorso, parametri, etag) -> esito`. L'ultimo elemento si ripete.
    Con `blocca` impostato, ogni chiamata aspetta l'evento prima di rispondere
    e segnala `entrata`.
    """

    remota = True

    def __init__(self, *risposte, blocca: threading.Event | None = None) -> None:
        self._risposte = list(risposte)
        self.chiamate: list[tuple[str, tuple[tuple[str, str], ...], str | None]] = []
        self.blocca = blocca
        self.entrata = threading.Event()
        self._lock = threading.Lock()

    def programma(self, *risposte) -> None:
        with self._lock:
            self._risposte = list(risposte)

    def leggi(self, percorso, parametri, etag=None):
        with self._lock:
            self.chiamate.append((percorso, tuple(parametri), etag))
            esito = self._risposte.pop(0) if len(self._risposte) > 1 else self._risposte[0]
        if self.blocca is not None:
            self.entrata.set()
            self.blocca.wait(5)
        if callable(esito) and not isinstance(esito, (RispostaEduNews24, BaseException)):
            esito = esito(percorso, parametri, etag)
        if isinstance(esito, BaseException):
            raise esito
        return esito


def guasto(motivo: str = "errore-server", stato: int | None = 500, retry_after: int | None = None) -> ErroreEduNews24:
    return ErroreEduNews24(motivo, stato_http=stato, retry_after=retry_after)
