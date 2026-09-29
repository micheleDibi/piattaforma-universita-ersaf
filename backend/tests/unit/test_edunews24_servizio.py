"""Servizio EduNews24: freschezza, single-flight, semaforo, pausa, budget, cursori.

Fonte e orologio finti; i thread si sincronizzano con Event e con
`_Volo.in_attesa`, mai con sleep.
"""

from __future__ import annotations

import logging
import threading
import time

import pytest

from src.edunews24.client import ErroreEduNews24
from src.edunews24.memoria import FonteMemoria
from src.edunews24.normalizza import ContestoValidazione
from src.edunews24.schemi import FiltriInterpelli, FiltriNotizie, FiltriSelezione
from src.edunews24.servizio import ErroreServizio, ServizioEduNews24
from tests.support.edunews24 import (
    CONTATTO,
    HOST_MEDIA,
    HOST_SITO,
    PROFILO_STANTIO,
    PROFILO_STATICO,
    FonteFinta,
    OrologioFinto,
    articolo,
    categorie,
    elenco,
    guasto,
    link_next,
    opportunita,
    risposta,
)

CONTESTO = ContestoValidazione(host_sito=HOST_SITO, host_media=frozenset({HOST_MEDIA}))
TUTTE = FiltriNotizie()


def _servizio(fonte, orologio=None, *, attesa_volo=1.5, posti=4, richieste=30, pausa=30):
    return ServizioEduNews24(attiva=True, fonte=fonte, contesto=CONTESTO, ttl_ripiego=300,
                             stantio_massimo=86400, pausa_ripiego=pausa, richieste_al_minuto=richieste,
                             orologio=orologio or OrologioFinto(), attesa_volo=attesa_volo, posti=posti)


def _notizie(*ids, next=None, **argomenti):
    return risposta(elenco([articolo(i) for i in ids], next), **argomenti)


def _instrada(**per_risorsa):
    """Esito per risorsa ("articles", "categories"...): un valore o una lista consumata in ordine."""
    code = {nome: (list(valore) if isinstance(valore, list) else [valore]) for nome, valore in per_risorsa.items()}

    def gestore(percorso, parametri, etag):
        coda = code[percorso.lstrip("/")]
        return coda.pop(0) if len(coda) > 1 else coda[0]

    return gestore


def _errore(funzione) -> ErroreServizio:
    with pytest.raises(ErroreServizio) as errore:
        funzione()
    return errore.value


class _Chiamata(threading.Thread):
    def __init__(self, funzione):
        super().__init__(daemon=True)
        self._funzione = funzione
        self.esito = None
        self.errore = None

    def run(self):
        try:
            self.esito = self._funzione()
        except BaseException as errore:  # noqa: BLE001 - lo legge il test
            self.errore = errore


def _aspetta(condizione, secondi=5.0):
    limite = time.monotonic() + secondi
    while not condizione():
        assert time.monotonic() < limite, "condizione non raggiunta"


def _ids(elenco_):
    return [voce.id for voce in elenco_.elementi]


# --- freschezza e rinnovo -----------------------------------------------------

def test_una_voce_fresca_non_chiama_nessuno():
    fonte = FonteFinta(_notizie(1, 2))
    servizio = _servizio(fonte)
    primo = servizio.notizie(TUTTE)
    secondo = servizio.notizie(TUTTE)
    assert _ids(primo) == _ids(secondo) == [1, 2]
    assert len(fonte.chiamate) == 1
    assert primo.meta.stantio is False and primo.meta.aggiornato_il is not None


def test_in_swr_un_solo_rinnovo_e_gli_altri_ricevono_subito_la_copia(caplog):
    caplog.set_level(logging.DEBUG, logger="ersaf.edunews24")
    orologio = OrologioFinto()
    fonte = FonteFinta(_notizie(1), _notizie(2))
    servizio = _servizio(fonte, orologio, posti=1)
    servizio.notizie(TUTTE)
    orologio.avanza(350)                      # oltre s-maxage=300, dentro SWR
    fonte.blocca = threading.Event()
    capo = _Chiamata(lambda: servizio.notizie(TUTTE))
    capo.start()
    assert fonte.entrata.wait(5)
    # Il capo tiene l'unico posto del semaforo: i seguaci non ne chiedono.
    seguaci = [servizio.notizie(TUTTE) for _ in range(3)]
    assert all(_ids(s) == [1] and s.meta.stantio is False for s in seguaci)
    fonte.blocca.set()
    capo.join(5)
    assert capo.errore is None and _ids(capo.esito) == [2]
    assert len(fonte.chiamate) == 2
    assert not any("occupato" in r.getMessage() for r in caplog.records)
    assert _ids(servizio.notizie(TUTTE)) == [2]


# --- single-flight ------------------------------------------------------------

def test_senza_copia_parte_una_sola_chiamata():
    fonte = FonteFinta(_notizie(1), blocca=threading.Event())
    servizio = _servizio(fonte)
    capo = _Chiamata(lambda: servizio.notizie(TUTTE))
    capo.start()
    assert fonte.entrata.wait(5)
    seguace = _Chiamata(lambda: servizio.notizie(TUTTE))
    seguace.start()
    _aspetta(lambda: servizio._voli["/articles"].in_attesa == 1)
    fonte.blocca.set()
    capo.join(5)
    seguace.join(5)
    assert capo.errore is None and seguace.errore is None
    assert _ids(capo.esito) == _ids(seguace.esito) == [1]
    assert len(fonte.chiamate) == 1


def test_il_seguace_riceve_una_copia_nuova_dell_errore_del_capo():
    fonte = FonteFinta(guasto(), blocca=threading.Event())
    servizio = _servizio(fonte)
    capo = _Chiamata(lambda: servizio.notizie(TUTTE))
    capo.start()
    assert fonte.entrata.wait(5)
    seguace = _Chiamata(lambda: servizio.notizie(TUTTE))
    seguace.start()
    _aspetta(lambda: servizio._voli["/articles"].in_attesa == 1)
    fonte.blocca.set()
    capo.join(5)
    seguace.join(5)
    assert isinstance(capo.errore, ErroreServizio) and isinstance(seguace.errore, ErroreServizio)
    assert capo.errore is not seguace.errore
    assert seguace.errore.tipo == "non-disponibile" and seguace.errore.secondi == 30
    assert len(fonte.chiamate) == 1


def test_attesa_scaduta_senza_copia_da_503_breve():
    fonte = FonteFinta(_notizie(1), blocca=threading.Event())
    servizio = _servizio(fonte, attesa_volo=0.2)
    capo = _Chiamata(lambda: servizio.notizie(TUTTE))
    capo.start()
    assert fonte.entrata.wait(5)
    errore = _errore(lambda: servizio.notizie(TUTTE))
    assert (errore.tipo, errore.secondi) == ("non-disponibile", 5)
    fonte.blocca.set()
    capo.join(5)
    assert capo.errore is None


def test_attesa_scaduta_con_copia_sie_la_serve_stantia():
    orologio = OrologioFinto()
    fonte = FonteFinta(_notizie(1), _notizie(2))
    servizio = _servizio(fonte, orologio, attesa_volo=0.2)
    servizio.notizie(TUTTE)
    orologio.avanza(700)                      # oltre SWR, dentro stale-if-error
    fonte.blocca = threading.Event()
    capo = _Chiamata(lambda: servizio.notizie(TUTTE))
    capo.start()
    assert fonte.entrata.wait(5)
    copia = servizio.notizie(TUTTE)
    assert _ids(copia) == [1] and copia.meta.stantio is True
    fonte.blocca.set()
    capo.join(5)
    assert _ids(capo.esito) == [2]


# --- semaforo -----------------------------------------------------------------

def test_semaforo_pieno_da_la_copia_o_503_breve():
    orologio = OrologioFinto()
    fonte = FonteFinta(_instrada(articles=_notizie(1), interpelli=risposta(elenco([opportunita(5, tipo="interpello")]))))
    servizio = _servizio(fonte, orologio, posti=1)
    servizio.interpelli(FiltriInterpelli())
    orologio.avanza(700)                      # interpelli scaduti, ma coperti da stale-if-error
    fonte.blocca = threading.Event()
    capo = _Chiamata(lambda: servizio.notizie(TUTTE))
    capo.start()
    assert fonte.entrata.wait(5)
    copia = servizio.interpelli(FiltriInterpelli())
    assert _ids(copia) == [5] and copia.meta.stantio is True
    errore = _errore(lambda: servizio.selezione(FiltriSelezione()))
    assert (errore.tipo, errore.secondi) == ("non-disponibile", 5)
    fonte.blocca.set()
    capo.join(5)
    assert capo.errore is None
    # Nessun posto rilasciato senza essere acquisito: il semaforo ne ha ancora uno solo.
    assert servizio._semaforo.prova() is True
    assert servizio._semaforo.prova() is False


# --- pausa e budget -----------------------------------------------------------

def test_un_429_con_retry_after_sospende_le_chiamate():
    orologio = OrologioFinto()
    fonte = FonteFinta(guasto("rifiutata", 429, retry_after=7), _notizie(1))
    servizio = _servizio(fonte, orologio)
    errore = _errore(lambda: servizio.notizie(TUTTE))
    assert (errore.tipo, errore.secondi) == ("non-disponibile", 7)
    orologio.avanza(3)
    errore = _errore(lambda: servizio.notizie(TUTTE))
    assert errore.secondi == 4
    assert len(fonte.chiamate) == 1
    orologio.avanza(4)
    assert _ids(servizio.notizie(TUTTE)) == [1]
    assert len(fonte.chiamate) == 2


def test_la_pausa_di_ripiego_raddoppia_e_si_azzera():
    orologio = OrologioFinto()
    fonte = FonteFinta(guasto(), guasto("tempo-scaduto", None), _notizie(1), guasto())
    servizio = _servizio(fonte, orologio)
    assert _errore(lambda: servizio.notizie(TUTTE)).secondi == 30
    orologio.avanza(30)
    assert _errore(lambda: servizio.notizie(TUTTE)).secondi == 60
    orologio.avanza(60)
    servizio.notizie(TUTTE)
    orologio.avanza(400)
    # Dopo il successo si riparte da 30, e la copia SWR copre il guasto.
    copia = servizio.notizie(TUTTE)
    assert _ids(copia) == [1]
    assert servizio._pausa.restante() == 30


def test_dopo_un_guasto_il_capo_serve_la_copia_swr():
    orologio = OrologioFinto()
    fonte = FonteFinta(_notizie(1), guasto("rete", None))
    servizio = _servizio(fonte, orologio)
    servizio.notizie(TUTTE)
    orologio.avanza(350)
    copia = servizio.notizie(TUTTE)
    assert _ids(copia) == [1] and copia.meta.stantio is False
    assert len(fonte.chiamate) == 2


def test_budget_esaurito_da_la_copia_o_503(caplog):
    caplog.set_level(logging.INFO, logger="ersaf.edunews24")
    orologio = OrologioFinto()
    breve = "public, s-maxage=20, stale-while-revalidate=300, stale-if-error=86400"
    fonte = FonteFinta(_instrada(articles=[_notizie(1, cache_control=breve), _notizie(2)],
                                 interpelli=risposta(elenco([opportunita(5, tipo="interpello")]))))
    servizio = _servizio(fonte, orologio, richieste=1)
    servizio.notizie(TUTTE)
    orologio.avanza(10)
    errore = _errore(lambda: servizio.interpelli(FiltriInterpelli()))
    assert (errore.tipo, errore.secondi) == ("non-disponibile", 50)
    orologio.avanza(20)                       # notizie in SWR, budget ancora pieno
    assert _ids(servizio.notizie(TUTTE)) == [1]
    assert len(fonte.chiamate) == 1
    avvisi = [r for r in caplog.records if "budget" in r.getMessage() and r.levelno == logging.WARNING]
    assert len(avvisi) == 1


def test_memoria_non_consuma_budget():
    servizio = _servizio(FonteMemoria(HOST_SITO, OrologioFinto()), richieste=1)
    for area in ("tutte", "lazio", "lombardia", "veneto"):
        assert servizio.interpelli(FiltriInterpelli(area=area)).attiva
    assert servizio.notizie(TUTTE).elementi


# --- guasti e risposte particolari --------------------------------------------

def test_stale_if_error_entro_la_finestra_e_503_oltre():
    orologio = OrologioFinto()
    fonte = FonteFinta(_notizie(1), guasto())
    servizio = _servizio(fonte, orologio)
    servizio.notizie(TUTTE)
    orologio.avanza(700)
    copia = servizio.notizie(TUTTE)
    assert _ids(copia) == [1] and copia.meta.stantio is True
    orologio.avanza(86400)
    assert _errore(lambda: servizio.notizie(TUTTE)).tipo == "non-disponibile"


def test_una_risposta_stale_a_monte():
    fonte = FonteFinta(_notizie(1, cache_control=PROFILO_STANTIO, stantia=True))
    elenco_ = _servizio(fonte).notizie(TUTTE)
    assert elenco_.meta.stantio is True and elenco_.meta.aggiornato_il is None


def test_un_304_rinnova_la_copia():
    orologio = OrologioFinto()
    fonte = FonteFinta(_notizie(1, etag='W/"a"'), risposta(None, stato=304, etag='W/"a"'))
    servizio = _servizio(fonte, orologio)
    primo = servizio.notizie(TUTTE)
    orologio.avanza(400)
    secondo = servizio.notizie(TUTTE)
    assert fonte.chiamate[1][2] == 'W/"a"'
    assert _ids(secondo) == [1] and secondo.meta.stantio is False
    assert secondo.meta.aggiornato_il > primo.meta.aggiornato_il
    servizio.notizie(TUTTE)
    assert len(fonte.chiamate) == 2


def test_un_200_no_store_non_si_salva():
    fonte = FonteFinta(_notizie(1, cache_control="no-store"))
    servizio = _servizio(fonte)
    assert _ids(servizio.notizie(TUTTE)) == [1]
    servizio.notizie(TUTTE)
    assert len(fonte.chiamate) == 2


def test_un_eccezione_inattesa_vale_come_guasto():
    class Ostile(dict):
        def get(self, *argomenti):
            raise RuntimeError("corpo ostile")

    orologio = OrologioFinto()
    fonte = FonteFinta(_notizie(1), risposta(Ostile()))
    servizio = _servizio(fonte, orologio)
    servizio.notizie(TUTTE)
    orologio.avanza(700)
    copia = servizio.notizie(TUTTE)
    assert _ids(copia) == [1] and copia.meta.stantio is True
    assert servizio._pausa.restante() == 30


def test_un_surrogato_isolato_non_e_un_guasto():
    # Mezza emoji in un titolo: JSON valido. Prima guastava la pagina e
    # metteva in pausa tutte le rotte.
    fonte = FonteFinta(risposta(elenco([articolo(1), articolo(2, titolo="Titolo con emoji tagliata \ud83d")])))
    servizio = _servizio(fonte)
    elenco_ = servizio.notizie(TUTTE)
    assert _ids(elenco_) == [1, 2] and elenco_.elementi[1].titolo == "Titolo con emoji tagliata"
    assert servizio._pausa.restante() == 0


def test_richiesta_rifiutata_senza_pausa():
    orologio = OrologioFinto()
    fonte = FonteFinta(guasto("richiesta-rifiutata", 400))
    servizio = _servizio(fonte, orologio, pausa=45)
    errore = _errore(lambda: servizio.interpelli(FiltriInterpelli()))
    assert (errore.tipo, errore.secondi) == ("non-disponibile", 45)
    assert servizio._pausa.restante() == 0
    fonte.programma(_notizie(1), guasto("richiesta-rifiutata", 400))
    servizio.notizie(TUTTE)
    orologio.avanza(700)
    assert _ids(servizio.notizie(TUTTE)) == [1]
    assert servizio._pausa.restante() == 0


# --- cursori ------------------------------------------------------------------

@pytest.mark.parametrize("cursore", ["inventato", "a.b", "", "a" * 301])
def test_cursore_sconosciuto_o_fuori_forma_da_409_senza_chiamate(cursore):
    fonte = FonteFinta(guasto())
    servizio = _servizio(fonte)
    for chiamata in (lambda: servizio.notizie(FiltriNotizie(categoria="scuola", cursore=cursore)),
                     lambda: servizio.interpelli(FiltriInterpelli(cursore=cursore)),
                     lambda: servizio.selezione(FiltriSelezione(area="nazionale", cursore=cursore))):
        assert _errore(chiamata).tipo == "cursore"
    assert fonte.chiamate == []


def test_il_cursore_vale_solo_con_gli_stessi_filtri():
    fonte = FonteFinta(_instrada(articles=[_notizie(1, next=link_next(cursore="c1")), _notizie(2)],
                                 categories=risposta(categorie("scuola"), cache_control=PROFILO_STATICO)))
    servizio = _servizio(fonte)
    primo = servizio.notizie(TUTTE)
    assert primo.meta.cursore_successivo == "c1"
    assert _errore(lambda: servizio.notizie(FiltriNotizie(solo_video="si", cursore="c1"))).tipo == "cursore"
    assert _errore(lambda: servizio.interpelli(FiltriInterpelli(cursore="c1"))).tipo == "cursore"
    secondo = servizio.notizie(FiltriNotizie(cursore="c1"))
    assert _ids(secondo) == [2] and secondo.meta.cursore_successivo is None
    assert fonte.chiamate[-1] == ("/articles", (("cursor", "c1"),), None)


def test_invalid_cursor_a_monte_da_409_e_dimentica_il_cursore():
    orologio = OrologioFinto()
    fonte = FonteFinta(_notizie(1, next=link_next(cursore="c1")), guasto("cursore-rifiutato", 400))
    servizio = _servizio(fonte, orologio)
    servizio.notizie(TUTTE)
    assert _errore(lambda: servizio.notizie(FiltriNotizie(cursore="c1"))).tipo == "cursore"
    assert not servizio._cursori.emesso("/articles", "", "c1")
    assert servizio._pausa.restante() == 0
    # Ne' copia ne' nuova chiamata: il cursore non e' piu' emesso.
    assert _errore(lambda: servizio.notizie(FiltriNotizie(cursore="c1"))).tipo == "cursore"
    assert len(fonte.chiamate) == 2


def test_invalid_cursor_a_monte_fa_rileggere_la_pagina_che_lo_ha_emesso():
    fonte = FonteFinta(_notizie(1, next=link_next(cursore="c1"), etag='W/"a"'),
                       guasto("cursore-rifiutato", 400),
                       _notizie(1, next=link_next(cursore="c2")),
                       _notizie(2))
    servizio = _servizio(fonte)
    servizio.notizie(TUTTE)
    assert _errore(lambda: servizio.notizie(FiltriNotizie(cursore="c1"))).tipo == "cursore"
    # La ripartenza non riceve dalla copia fresca lo stesso cursore rifiutato:
    # la prima pagina si rinnova, con l'ETag salvato.
    ripartita = servizio.notizie(TUTTE)
    assert fonte.chiamate[2] == ("/articles", (), 'W/"a"')
    assert ripartita.meta.cursore_successivo == "c2"
    assert _ids(servizio.notizie(FiltriNotizie(cursore="c2"))) == [2]
    assert len(fonte.chiamate) == 4 and servizio._pausa.restante() == 0


def test_una_pagina_vuota_con_next_porta_il_cursore():
    fonte = FonteFinta(_notizie(next=link_next(cursore="c9")))
    elenco_ = _servizio(fonte).notizie(TUTTE)
    assert elenco_.elementi == [] and elenco_.meta.cursore_successivo == "c9"


# --- categorie ----------------------------------------------------------------

def test_le_categorie_si_caricano_prima_delle_notizie():
    fonte = FonteFinta(_instrada(articles=_notizie(1),
                                 categories=risposta(categorie("scuola"), cache_control=PROFILO_STATICO)))
    servizio = _servizio(fonte)
    assert _ids(servizio.notizie(FiltriNotizie(categoria="scuola"))) == [1]
    assert [c[0] for c in fonte.chiamate] == ["/categories", "/articles"]
    assert fonte.chiamate[1][1] == (("category", "scuola"),)
    servizio.notizie(FiltriNotizie(categoria="scuola"))
    assert len(fonte.chiamate) == 2


def test_categoria_sconosciuta_da_400_senza_chiamare_le_notizie():
    fonte = FonteFinta(_instrada(articles=_notizie(1),
                                 categories=risposta(categorie("scuola"), cache_control=PROFILO_STATICO)))
    servizio = _servizio(fonte)
    assert _errore(lambda: servizio.notizie(FiltriNotizie(categoria="inesistente"))).tipo == "categoria"
    assert [c[0] for c in fonte.chiamate] == ["/categories"]


def test_senza_categorie_disponibili_503():
    fonte = FonteFinta(_instrada(articles=_notizie(1), categories=guasto()))
    servizio = _servizio(fonte)
    errore = _errore(lambda: servizio.notizie(FiltriNotizie(categoria="scuola")))
    assert errore.tipo == "non-disponibile"
    assert [c[0] for c in fonte.chiamate] == ["/categories"]
    assert _errore(lambda: servizio.categorie()).tipo == "non-disponibile"


def test_un_400_di_categoria_a_monte_da_400_e_fa_scadere_le_categorie():
    orologio = OrologioFinto()
    fonte = FonteFinta(_instrada(articles=[guasto("categoria-sconosciuta", 400), _notizie(1)],
                                 categories=risposta(categorie("scuola"), cache_control=PROFILO_STATICO)))
    servizio = _servizio(fonte, orologio)
    assert _errore(lambda: servizio.notizie(FiltriNotizie(categoria="scuola"))).tipo == "categoria"
    assert servizio._pausa.restante() == 0
    servizio.notizie(FiltriNotizie(categoria="scuola"))
    assert [c[0] for c in fonte.chiamate] == ["/categories", "/articles", "/categories", "/articles"]


def test_elenco_delle_categorie():
    fonte = FonteFinta(risposta(categorie("scuola", "concorsi"), cache_control=PROFILO_STATICO))
    elenco_ = _servizio(fonte).categorie()
    assert [c.slug for c in elenco_.elementi] == ["scuola", "concorsi"]
    assert elenco_.meta.cursore_successivo is None


# --- aree ---------------------------------------------------------------------

def test_aree_tradotte_nei_parametri_a_monte():
    fonte = FonteFinta(risposta(elenco([])))
    servizio = _servizio(fonte)
    servizio.interpelli(FiltriInterpelli(area="lazio"))
    servizio.selezione(FiltriSelezione(area="nazionale"))
    servizio.selezione(FiltriSelezione(area="valle-d-aosta"))
    servizio.selezione(FiltriSelezione())
    servizio.notizie(FiltriNotizie(solo_video="si"))
    assert [c[:2] for c in fonte.chiamate] == [
        ("/interpelli", (("region", "lazio"),)),
        ("/selezione-personale", (("national", "true"),)),
        ("/selezione-personale", (("region", "valle-d-aosta"),)),
        ("/selezione-personale", ()),
        ("/articles", (("has_video", "true"),)),
    ]
    assert _errore(lambda: servizio.interpelli(FiltriInterpelli(area="nazionale"))).tipo == "area"
    assert len(fonte.chiamate) == 5


# --- errori verso il browser ------------------------------------------------------

def test_traduzione_degli_errori_in_http():
    assert ErroreServizio("cursore").http().status_code == 409
    assert ErroreServizio("categoria").http().status_code == 400
    assert ErroreServizio("area").http().status_code == 400
    errore = ErroreServizio("non-disponibile", 0).http()
    assert errore.status_code == 503 and errore.headers == {"Retry-After": "1"}
    assert ErroreServizio("non-disponibile", 42).http().headers == {"Retry-After": "42"}


# --- log ----------------------------------------------------------------------

def test_log_senza_host_slug_cursori_ne_contatto(caplog):
    caplog.set_level(logging.DEBUG, logger="ersaf.edunews24")
    orologio = OrologioFinto()
    fonte = FonteFinta(_instrada(
        articles=[_notizie(1, next=link_next(cursore="cursoresegreto")),
                  risposta(elenco([articolo(9, url="https://altrove.example.org/x")],
                                  "https://edunews24.invalid/api/v1/articles?cursor=fuori.forma")),
                  guasto()],
        interpelli=guasto("rifiutata", 503, retry_after=30),
        categories=risposta(categorie("categoriasegreta"), cache_control=PROFILO_STATICO)))
    servizio = _servizio(fonte, orologio)
    servizio.notizie(FiltriNotizie(categoria="categoriasegreta"))
    servizio.notizie(FiltriNotizie(categoria="categoriasegreta", cursore="cursoresegreto"))
    _errore(lambda: servizio.notizie(FiltriNotizie(cursore="inventatosegreto")))
    _errore(lambda: servizio.notizie(FiltriNotizie(categoria="sconosciutasegreta")))
    _errore(lambda: servizio.interpelli(FiltriInterpelli(area="lazio")))
    testo = "\n".join(r.getMessage() for r in caplog.records)
    assert "voci-scartate" in testo and "cursore-fuori-forma" in testo and "guasto" in testo
    for vietato in (HOST_SITO, "example.org", "segret", "fuori.forma", CONTATTO, "lazio", "http"):
        assert vietato not in testo, vietato

    # Durante la pausa i 503 non vanno a WARNING.
    caplog.clear()
    _errore(lambda: servizio.interpelli(FiltriInterpelli(area="lazio")))
    _errore(lambda: servizio.selezione(FiltriSelezione()))
    assert caplog.records and all(r.levelno < logging.WARNING for r in caplog.records)


# --- costruzione ---------------------------------------------------------------

def test_da_impostazioni_per_i_tre_backend():
    from src.config import Impostazioni
    from src.edunews24.client import ClientEduNews24

    base = dict(_env_file=None, edunews24_url_base="https://edunews24.invalid/api/v1",
                edunews24_contatto=CONTATTO, edunews24_host_media="Media.Edunews24.invalid, *.x, ")
    spento = ServizioEduNews24.da_impostazioni(Impostazioni(**base, edunews24_backend="disabilitato"))
    assert spento.attiva is False
    memoria = ServizioEduNews24.da_impostazioni(Impostazioni(**base, edunews24_backend="memoria"))
    assert memoria.attiva is True and isinstance(memoria._fonte, FonteMemoria)
    assert memoria._contesto == CONTESTO
    remoto = ServizioEduNews24.da_impostazioni(Impostazioni(**base, edunews24_backend="http"))
    assert isinstance(remoto._fonte, ClientEduNews24)
    senza_url = ServizioEduNews24.da_impostazioni(
        Impostazioni(_env_file=None, edunews24_backend="memoria", edunews24_url_base="",
                     edunews24_host_media=""))
    assert senza_url._contesto.host_sito == "edunews24.invalid"
    assert senza_url._contesto.host_media == frozenset()


def test_istanza_unica_e_azzeramento():
    from src.edunews24.servizio import azzera_servizio, get_servizio

    primo = get_servizio()
    assert get_servizio() is primo
    azzera_servizio()
    assert get_servizio() is not primo


def test_errori_della_fonte_memoria_risalgono_tradotti():
    fonte = FonteMemoria(HOST_SITO, OrologioFinto())
    servizio = _servizio(fonte)
    assert _errore(lambda: servizio.notizie(FiltriNotizie(categoria="inesistente"))).tipo == "categoria"
    with pytest.raises(ErroreEduNews24):
        fonte.leggi("/articles", [("cursor", "m20-00000000")])
