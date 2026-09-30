"""Filtri in ingresso e risposte delle rotte EduNews24 (contratto unico).

Niente union con discriminator e niente allOf: il generatore di api.md non li
accetta. I campi nullabili e i modelli annidati vanno bene.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# "tutte", "nazionale" e i 20 slug di REGIONI (costanti.py), nello stesso
# ordine: un test lo verifica.
Area = Literal[
    "tutte", "nazionale", "abruzzo", "basilicata", "calabria", "campania", "emilia-romagna",
    "friuli-venezia-giulia", "lazio", "liguria", "lombardia", "marche", "molise", "piemonte",
    "puglia", "sardegna", "sicilia", "toscana", "trentino-alto-adige", "umbria", "valle-d-aosta",
    "veneto",
]


class FiltriNotizie(BaseModel):
    categoria: str | None = Field(None, max_length=64, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    solo_video: Literal["no", "si"] = "no"
    # Forma controllata dal servizio: un cursore fuori forma da' 409, non 422.
    cursore: str | None = None


class FiltriInterpelli(BaseModel):
    area: Area = "tutte"
    cursore: str | None = None


class FiltriSelezione(BaseModel):
    area: Area = "tutte"
    cursore: str | None = None


class CategoriaNotizie(BaseModel):
    slug: str
    nome: str


class RegioneOpportunita(BaseModel):
    slug: str
    nome: str


class VideoNotizia(BaseModel):
    url: str
    tipo_mime: Literal["video/mp4", "video/webm"]
    copertina: str | None
    durata_secondi: int | None


class Notizia(BaseModel):
    tipo: Literal["notizia"] = "notizia"
    id: int
    titolo: str
    titolo_breve: str | None
    sintesi: str | None
    url: str
    pubblicato_il: str
    categoria: CategoriaNotizie
    immagine: str | None
    video: VideoNotizia | None
    ha_video: bool


class Opportunita(BaseModel):
    tipo: Literal["interpello", "selezione-personale"]
    id: int
    titolo: str
    sintesi: str | None
    url: str
    # Solo nella selezione; null negli interpelli.
    ente: str | None
    sede: str | None
    regioni: list[RegioneOpportunita]
    nazionale: bool
    pubblicato_il: str
    scadenza: str | None
    stato: Literal["aperto", "chiuso", "altro"] | None
    # Solo negli interpelli; null nella selezione.
    classe_concorso: str | None
    # Solo nella selezione; null negli interpelli.
    figura: str | None
    posti: int | None


class AggiornamentoEduNews24(BaseModel):
    cursore_successivo: str | None
    aggiornato_il: datetime | None
    stantio: bool


class ElencoNotizie(BaseModel):
    attiva: bool
    elementi: list[Notizia]
    meta: AggiornamentoEduNews24 | None


class ElencoOpportunita(BaseModel):
    attiva: bool
    elementi: list[Opportunita]
    meta: AggiornamentoEduNews24 | None


class ElencoCategorie(BaseModel):
    attiva: bool
    elementi: list[CategoriaNotizie]
    meta: AggiornamentoEduNews24 | None
