"""Politica di cache (RFC 9111, cache condivisa) e LRU delle risposte."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.edunews24.cache import (
    CacheRisposte,
    Politica,
    leggi_politica,
    nuova_voce,
    rinnova_voce,
)
from src.edunews24.normalizza import PaginaNormalizzata
from tests.support.edunews24 import (
    PARETE_FISSA,
    PROFILO_ELENCO,
    PROFILO_STANTIO,
    PROFILO_STATICO,
    risposta,
)


def _politica(cache_control, age=None, *, ttl=300, massimo=86400, stantia=False):
    return leggi_politica(cache_control, age, ttl_ripiego=ttl, stantio_massimo=massimo, stantia_a_monte=stantia)


def _pagina(byte=100, cursore=None) -> PaginaNormalizzata:
    return PaginaNormalizzata(elementi=(), cursore_successivo=cursore, cursore_fuori_forma=False,
                              totali=0, scartate=0, byte=byte)


def _voce(cache_control=PROFILO_ELENCO, *, inizio=1000.0, precedente=None, stantia=False, etag=None,
          byte=100, parete=PARETE_FISSA):
    return nuova_voce(_pagina(byte), risposta({}, cache_control=cache_control, stantia=stantia, etag=etag),
                      inizio=inizio, adesso_parete=parete, precedente=precedente, ttl_ripiego=300,
                      stantio_massimo=86400)


def test_profili_del_contratto():
    assert _politica(PROFILO_ELENCO) == Politica(300, 300, 86400)
    assert _politica(PROFILO_STATICO) == Politica(3600, 3600, 86400)
    assert _politica(PROFILO_STANTIO, stantia=True) == Politica(60, 0, 0)


def test_age_si_sottrae_e_max_age_vale_senza_s_maxage():
    assert _politica(PROFILO_ELENCO, "120") == Politica(180, 300, 86400)
    # Scaduta da 600 secondi all'arrivo: le finestre stantie ne hanno gia' speso 600.
    assert _politica(PROFILO_ELENCO, "900") == Politica(0, 0, 85800)
    assert _politica(PROFILO_ELENCO, "450") == Politica(0, 150, 86250)
    assert _politica("public, max-age=90") == Politica(90, 0, 0)
    assert _politica("public, max-age=90", "30") == Politica(60, 0, 0)


def test_ripiego_senza_s_maxage_ne_max_age():
    assert _politica("public", ttl=120) == Politica(120, 0, 0)
    assert _politica(None, ttl=120) == Politica(120, 0, 0)
    # Una copia STALE senza s-maxage resta fresca 60 secondi, non quanto il ripiego.
    assert _politica(None, ttl=600, stantia=True) == Politica(60, 0, 0)
    assert _politica("public, max-age=600", stantia=True) == Politica(60, 0, 0)


def test_no_store_e_private_non_si_salvano():
    assert _politica("no-store") is None
    assert _politica("private, max-age=60") is None
    assert _politica("public, NO-STORE") is None


@pytest.mark.parametrize("direttiva", ["no-cache", "must-revalidate", "proxy-revalidate"])
def test_revalidate_azzera_le_copie_stantie(direttiva):
    politica = _politica(f"{PROFILO_ELENCO}, {direttiva}")
    assert politica.swr == 0 and politica.sie == 0
    assert politica.freschezza == (0 if direttiva == "no-cache" else 300)


def test_valori_non_validi_e_tetti():
    assert _politica('public, s-maxage="120"') == Politica(120, 0, 0)
    assert _politica("public, s-maxage=abc", ttl=45) == Politica(45, 0, 0)
    assert _politica("public, s-maxage=-5, max-age=30") == Politica(30, 0, 0)
    assert _politica("public, s-maxage=99999, stale-while-revalidate=99999, stale-if-error=999999") == \
        Politica(3600, 3600, 86400)
    assert _politica(PROFILO_ELENCO, massimo=600).sie == 600
    assert _politica(PROFILO_ELENCO, massimo=0).sie == 0


def test_nuova_voce_calcola_le_finestre_e_l_istante():
    voce = _voce(etag='W/"a"')
    assert (voce.fresca_fino, voce.swr_fino, voce.sie_fino) == (1300, 1600, 1000 + 300 + 86400)
    assert voce.etag == 'W/"a"'
    assert voce.aggiornato_il == datetime.fromtimestamp(PARETE_FISSA, tz=timezone.utc)
    assert not voce.stantio_a(1599)
    assert voce.stantio_a(1600)
    assert voce.servito(1700).stantio is True
    assert voce.servito(1200).meta().stantio is False


def test_no_store_non_crea_una_voce():
    assert _voce("no-store") is None


def test_una_risposta_stale_non_accorcia_la_finestra_ne_aggiorna_l_istante():
    precedente = _voce(inizio=1000.0, parete=PARETE_FISSA - 3600)
    stantia = _voce(PROFILO_STANTIO, inizio=2000.0, precedente=precedente, stantia=True)
    assert stantia.fresca_fino == 2060
    assert stantia.sie_fino == precedente.sie_fino
    assert stantia.aggiornato_il == precedente.aggiornato_il
    assert stantia.servito(2001).stantio is True
    # Senza una precedente l'istante non si conosce.
    assert _voce(PROFILO_STANTIO, stantia=True).aggiornato_il is None


def test_un_304_rinnova_e_sostituisce_l_etag():
    precedente = _voce(etag='W/"a"', parete=PARETE_FISSA - 600)
    rinnovata = rinnova_voce(precedente, risposta(None, stato=304, etag='W/"b"'), inizio=5000.0,
                             adesso_parete=PARETE_FISSA, ttl_ripiego=300, stantio_massimo=86400)
    assert rinnovata.valore is precedente.valore
    assert rinnovata.etag == 'W/"b"'
    assert rinnovata.fresca_fino == 5300
    assert rinnovata.aggiornato_il == datetime.fromtimestamp(PARETE_FISSA, tz=timezone.utc)
    senza_etag = rinnova_voce(precedente, risposta(None, stato=304), inizio=5000.0, adesso_parete=PARETE_FISSA,
                              ttl_ripiego=300, stantio_massimo=86400)
    assert senza_etag.etag == 'W/"a"'


def test_un_304_senza_cache_control_conserva_le_direttive_salvate():
    precedente = _voce(etag='W/"a"', parete=PARETE_FISSA - 600)
    rinnovata = rinnova_voce(precedente, risposta(None, stato=304, etag='W/"a"', cache_control=None),
                             inizio=5000.0, adesso_parete=PARETE_FISSA, ttl_ripiego=120, stantio_massimo=86400)
    # Non il ripiego di 120 secondi senza finestre: le direttive del 200.
    assert (rinnovata.fresca_fino, rinnovata.swr_fino, rinnovata.sie_fino) == (5300, 5600, 5300 + 86400)
    assert rinnovata.cache_control == PROFILO_ELENCO
    # Un 304 con le sue direttive le usa e le conserva.
    rinnovata = rinnova_voce(precedente, risposta(None, stato=304, cache_control="public, s-maxage=60"),
                             inizio=5000.0, adesso_parete=PARETE_FISSA, ttl_ripiego=120, stantio_massimo=86400)
    assert (rinnovata.fresca_fino, rinnovata.swr_fino, rinnovata.sie_fino) == (5060, 5060, 5060)
    assert rinnovata.cache_control == "public, s-maxage=60"


def test_un_304_stale_non_accorcia_la_finestra():
    precedente = _voce(parete=PARETE_FISSA - 600)
    rinnovata = rinnova_voce(precedente, risposta(None, stato=304, cache_control=PROFILO_STANTIO, stantia=True),
                             inizio=3000.0, adesso_parete=PARETE_FISSA, ttl_ripiego=300, stantio_massimo=86400)
    assert rinnovata.sie_fino == precedente.sie_fino
    assert rinnovata.aggiornato_il == precedente.aggiornato_il
    assert rinnovata.stantia_a_monte is True


def test_lru_per_numero_di_voci():
    cache = CacheRisposte()
    for n in range(97):
        assert cache.salva(f"/articles?n={n}", _voce())
    assert cache.dimensione()[0] == 96
    assert cache.leggi("/articles?n=0") is None
    assert cache.leggi("/articles?n=1") is not None


def test_leggi_sposta_la_voce_in_coda():
    cache = CacheRisposte(voci_massime=2)
    cache.salva("a", _voce())
    cache.salva("b", _voce())
    cache.leggi("a")
    cache.salva("c", _voce())
    assert cache.leggi("a") is not None and cache.leggi("b") is None


def test_lru_per_byte():
    cache = CacheRisposte()
    for n in range(40):
        cache.salva(f"k{n}", _voce(byte=190_000))
    voci, totale = cache.dimensione()
    assert totale <= 6_291_456
    assert voci == 6_291_456 // 190_000


def test_una_voce_troppo_grande_non_si_salva_e_toglie_la_vecchia():
    cache = CacheRisposte()
    cache.salva("k", _voce())
    assert cache.salva("k", _voce(byte=196_609)) is False
    assert cache.leggi("k") is None
    assert cache.dimensione() == (0, 0)


def test_scadi_conserva_la_finestra_stale_if_error():
    cache = CacheRisposte()
    voce = _voce()
    cache.salva("k", voce)
    cache.scadi("k", 1100.0)
    scaduta = cache.leggi("k")
    assert scaduta.fresca_fino == 1100 and scaduta.swr_fino == 1100
    assert scaduta.sie_fino == voce.sie_fino
    cache.rimuovi("k")
    assert cache.leggi("k") is None
    cache.salva("k", voce)
    cache.svuota()
    assert cache.dimensione() == (0, 0)
