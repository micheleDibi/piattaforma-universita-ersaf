"""La regola di visibilita' contro un riferimento in Python puro.

Il riferimento e' scritto qui da capo, senza riusare nulla del modulo, e segue
alla lettera le decisioni: "me" con l'ordinamento di cliente_principale, radici
= utente piu' colleghi, discendenti = raggiungibili con almeno un passo lungo
utente_padre anche attraverso utenti senza clienti, visibili = "me" piu' tutte
le righe dei discendenti.
"""

from __future__ import annotations

import itertools
import random
from collections import defaultdict

import pytest
from sqlalchemy import event, insert, select, text
from sqlalchemy.exc import CompileError

import src.main  # noqa: F401  registra tutti i mapper
from src.auth import visibilita as v
from src.auth.models import RUOLI_ATTUATORE
from src.auth.servizio_login import cliente_principale
from src.clienti.models import Cliente
from src.database import engine
from src.utenti.models import Utente
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

SEME = 20260917


# =============================================================================
# Riferimento
# =============================================================================
def riferimento(padri: dict[int, int | None], righe: list[tuple], utente_id: int):
    """`righe` = (cliente_id, utente_id, ruolo, azienda_id).

    Restituisce None per il Nazionale, altrimenti l'insieme dei cliente_id.
    """
    proprie = [r for r in righe if r[1] == utente_id]
    me = min(proprie, key=lambda r: (0 if r[2] in RUOLI_ATTUATORE else 1, r[0]), default=None)
    if me is not None and me[2] == f.RUOLO_NAZIONALE:
        return None
    azienda = me[3] if me else None

    radici = {utente_id}
    if azienda is not None:
        radici |= {r[1] for r in righe if r[3] == azienda}

    figli = defaultdict(set)
    for figlio, padre in padri.items():
        if padre is not None:
            figli[padre].add(figlio)

    discendenti: set[int] = set()
    da_visitare = [figlio for radice in radici for figlio in figli[radice]]
    while da_visitare:
        nodo = da_visitare.pop()
        if nodo not in discendenti:
            discendenti.add(nodo)
            da_visitare.extend(figli[nodo])

    visibili = {r[0] for r in righe if r[1] in discendenti}
    if me is not None:
        visibili.add(me[0])
    return visibili


def carica(db, padri, righe):
    db.execute(insert(Utente.__table__), [
        {"utente_id": u, "utente_username": f"u{u}", "utente_password": "",
         "utente_padre": p, "utente_attivoSN": f.ATTIVO}
        for u, p in padri.items()
    ])
    db.execute(insert(Cliente.__table__), [
        {"cliente_id": c, "utente_id": u, "cliente_ruolo": r, "azienda_id": a,
         "cliente_nome": "N", "cliente_cognome": "C"}
        for c, u, r, a in righe
    ])
    db.commit()


def ottenuti(db, utente_id):
    """Lista, non insieme: serve anche a vedere eventuali duplicati."""
    sotto = v.sottoquery_clienti(v.visibilita_di(db, db.get(Utente, utente_id)))
    return None if sotto is None else db.scalars(sotto).all()


def albero_casuale(seme: int):
    rnd = random.Random(seme)
    n = 400
    padri: dict[int, int | None] = {}
    for u in range(1, n + 1):
        scelta = rnd.random()
        if u == 1 or scelta < 0.08:
            padri[u] = None
        elif scelta < 0.10:
            padri[u] = 99_999               # padre che non esiste
        else:
            padri[u] = rnd.randint(max(1, u - 60), u - 1)
    padri[50] = 50                          # auto-ciclo
    padri[60], padri[61] = 61, 60           # ciclo da due
    padri[70], padri[71], padri[72] = 72, 70, 71   # ciclo da tre
    padri[73] = 72                          # un ramo che esce da un ciclo

    righe, cliente = [], itertools.count(1)
    for u in range(1, n + 1):
        caso = rnd.random()
        numero = 0 if caso < 0.20 else (2 if caso < 0.25 else 1)
        for _ in range(numero):
            righe.append((
                next(cliente), u,
                rnd.choice([0, 0, 0, 1, 1, 2, 3, 4, 6, 5]),
                rnd.choice([None, None, None, 1, 2, 3]),
            ))
    # Catena separata di 1200 livelli: oltre il limite di 1000 iterazioni.
    for u in range(1001, 2201):
        padri[u] = 1000 if u == 1001 else u - 1
        righe.append((next(cliente), u, 0, None))
    padri[1000] = None
    righe.append((next(cliente), 1000, 1, None))
    return padri, righe


# =============================================================================
# Equivalenza
# =============================================================================
@pytest.mark.parametrize("seme", [SEME, SEME + 1])
def test_equivalenza_con_il_riferimento(db, seme):
    padri, righe = albero_casuale(seme)
    carica(db, padri, righe)

    campione = list(range(1, 401)) + [1000, 1001, 1600, 2200]
    for utente_id in campione:
        atteso = riferimento(padri, righe, utente_id)
        lista = ottenuti(db, utente_id)
        if atteso is None:
            assert lista is None, f"utente {utente_id} doveva essere Nazionale"
            continue
        assert lista is not None, f"utente {utente_id} non doveva essere Nazionale"
        assert len(lista) == len(set(lista)), f"duplicati per l'utente {utente_id}"
        assert set(lista) == atteso, f"utente {utente_id}"


def test_la_catena_oltre_mille_livelli_e_completa(db):
    padri, righe = albero_casuale(SEME)
    carica(db, padri, righe)
    # 1000 e' la testa: vede se stesso e le 1200 righe sotto di lui.
    assert len(ottenuti(db, 1000)) == 1201


# =============================================================================
# D1 e D2
# =============================================================================
def test_il_nazionale_non_ha_filtro(db):
    nazionale = f.crea_attuatore(db, email="n@example.org", ruolo=f.RUOLO_NAZIONALE)
    vis = v.visibilita_di(db, db.get(Utente, nazionale.utente_id))
    assert vis.nazionale
    assert v.sottoquery_clienti(vis) is None
    assert v.condizione_azienda(vis, Cliente.azienda_id) is None


@pytest.mark.parametrize(("prima", "seconda", "nazionale"), [
    (f.RUOLO_ADERENTE, f.RUOLO_NAZIONALE, False),
    (f.RUOLO_NAZIONALE, f.RUOLO_ADERENTE, True),
    (f.RUOLO_SOTTOSCRITTORE, f.RUOLO_NAZIONALE, True),
])
def test_il_ruolo_viene_dalla_riga_principale(db, prima, seconda, nazionale):
    """Due righe attuatore: vince il cliente_id piu' basso, come in ruolo_di.
    Una riga non attuatore cede il passo a una attuatore."""
    utente = f.crea_utente(db)
    f.crea_cliente(db, utente_id=utente.utente_id, email="a@example.org", ruolo=prima)
    f.crea_cliente(db, utente_id=utente.utente_id, email="b@example.org", ruolo=seconda)
    assert v.visibilita_di(db, utente).nazionale is nazionale


def test_me_coincide_sempre_con_cliente_principale(db):
    ruoli = range(7)
    for prima, seconda in itertools.product(ruoli, ruoli):
        utente = f.crea_utente(db)
        f.crea_cliente(db, utente_id=utente.utente_id, email="x@example.org", ruolo=prima)
        f.crea_cliente(db, utente_id=utente.utente_id, email="y@example.org", ruolo=seconda)
        attesa = cliente_principale(db, utente.utente_id).cliente_id
        assert v.riga_di_me(db, utente.utente_id).cliente_id == attesa, (prima, seconda)


def test_l_azienda_viene_dalla_riga_di_me(db):
    """Riga non attuatore con id basso in X, riga attuatore in Y: vale Y."""
    x, y = f.crea_azienda(db), f.crea_azienda(db)
    utente = f.crea_utente(db)
    f.crea_cliente(db, utente_id=utente.utente_id, email="a@example.org",
                   ruolo=f.RUOLO_SOTTOSCRITTORE, azienda_id=x.azienda_id)
    attuatore = f.crea_cliente(db, utente_id=utente.utente_id, email="b@example.org",
                               ruolo=f.RUOLO_ADERENTE, azienda_id=y.azienda_id)
    vis = v.visibilita_di(db, utente)
    assert (vis.me_cliente_id, vis.azienda_id) == (attuatore.cliente_id, y.azienda_id)


def test_senza_anagrafica_niente_me_ma_i_discendenti_si(db):
    orfano = f.crea_utente(db)
    figlio = f.crea_attuatore(db, email="figlio@example.org", padre=orfano.utente_id)
    vis = v.visibilita_di(db, orfano)
    assert (vis.nazionale, vis.me_cliente_id, vis.azienda_id) == (False, None, None)
    assert set(db.scalars(v.sottoquery_clienti(vis))) == {figlio.cliente_id}


# =============================================================================
# D3, D4, D5
# =============================================================================
def test_il_collega_non_si_vede_suo_figlio_si(db):
    azienda = f.crea_azienda(db)
    io = f.crea_attuatore(db, email="io@example.org", azienda_id=azienda.azienda_id)
    collega = f.crea_attuatore(db, email="c@example.org", azienda_id=azienda.azienda_id)
    figlio = f.crea_attuatore(db, email="fc@example.org", padre=collega.utente_id)

    visibili = set(db.scalars(v.clienti_visibili(db, db.get(Utente, io.utente_id))))
    assert visibili == {io.cliente_id, figlio.cliente_id}


def test_l_azienda_nulla_non_crea_colleghi(db):
    io = f.crea_attuatore(db, email="io@example.org")
    altro = f.crea_attuatore(db, email="altro@example.org")
    figlio = f.crea_attuatore(db, email="fa@example.org", padre=altro.utente_id)
    visibili = set(db.scalars(v.clienti_visibili(db, db.get(Utente, io.utente_id))))
    assert visibili == {io.cliente_id}
    assert figlio.cliente_id not in visibili


def test_la_catena_attraversa_utenti_senza_anagrafica(db):
    io = f.crea_attuatore(db, email="io@example.org")
    intermedio = f.crea_utente(db, padre=io.utente_id)          # nessuna riga clienti
    nipote = f.crea_attuatore(db, email="n@example.org", padre=intermedio.utente_id)
    visibili = set(db.scalars(v.clienti_visibili(db, db.get(Utente, io.utente_id))))
    assert visibili == {io.cliente_id, nipote.cliente_id}


def test_senza_ciclo_la_seconda_riga_del_loggato_non_si_vede(db):
    utente = f.crea_utente(db)
    prima = f.crea_cliente(db, utente_id=utente.utente_id, email="a@example.org")
    f.crea_cliente(db, utente_id=utente.utente_id, email="b@example.org")
    assert set(db.scalars(v.clienti_visibili(db, utente))) == {prima.cliente_id}


def test_un_ciclo_rende_visibili_tutte_le_righe_del_loggato(db):
    utente = f.crea_utente(db)
    prima = f.crea_cliente(db, utente_id=utente.utente_id, email="a@example.org")
    seconda = f.crea_cliente(db, utente_id=utente.utente_id, email="b@example.org")
    altro = f.crea_attuatore(db, email="c@example.org", padre=utente.utente_id)
    riga = db.get(Utente, utente.utente_id)
    riga.utente_padre = altro.utente_id                         # ciclo a due
    db.commit()
    visibili = db.scalars(v.clienti_visibili(db, riga)).all()
    assert sorted(visibili) == sorted({prima.cliente_id, seconda.cliente_id, altro.cliente_id})


def test_il_collega_discendente_non_si_duplica(db):
    """Un collega con due righe che e' anche mio figlio: ogni riga una volta."""
    azienda = f.crea_azienda(db)
    io = f.crea_attuatore(db, email="io@example.org", azienda_id=azienda.azienda_id)
    collega = f.crea_utente(db, padre=io.utente_id)
    righe = {
        f.crea_cliente(db, utente_id=collega.utente_id, email="x@example.org",
                       azienda_id=azienda.azienda_id).cliente_id,
        f.crea_cliente(db, utente_id=collega.utente_id, email="y@example.org").cliente_id,
    }
    visibili = db.scalars(v.clienti_visibili(db, db.get(Utente, io.utente_id))).all()
    assert len(visibili) == len(set(visibili)) == 3
    assert set(visibili) == righe | {io.cliente_id}


# =============================================================================
# Funzioni di servizio
# =============================================================================
def test_cliente_e_utente_visibili(db):
    io = f.crea_attuatore(db, email="io@example.org")
    figlio = f.crea_attuatore(db, email="f@example.org", padre=io.utente_id)
    estraneo = f.crea_attuatore(db, email="e@example.org")
    vis = v.visibilita_di(db, db.get(Utente, io.utente_id))

    assert v.cliente_visibile(db, vis, figlio.cliente_id)
    assert not v.cliente_visibile(db, vis, estraneo.cliente_id)
    assert not v.cliente_visibile(db, vis, 999_999)
    assert v.utente_visibile(db, vis, figlio.utente_id)
    assert not v.utente_visibile(db, vis, estraneo.utente_id)
    assert not v.utente_visibile(db, vis, 999_999)


def test_condizione_azienda(db):
    senza = v.Visibilita(utente_id=1, nazionale=False)
    con = v.Visibilita(utente_id=1, nazionale=False, azienda_id=7)
    assert str(v.condizione_azienda(senza, Cliente.azienda_id).compile(engine)) == "false"
    assert str(v.condizione_azienda(con, Cliente.azienda_id).compile(
        engine, compile_kwargs={"literal_binds": True})) == "clienti.azienda_id = 7"


def test_due_sottoquery_nello_stesso_statement_non_compilano(db):
    """Vincolo documentato in sottoquery_clienti: una sola per statement."""
    vis = v.Visibilita(utente_id=1, nazionale=False)
    doppia = (select(Cliente.cliente_id)
              .where(Cliente.cliente_id.in_(v.sottoquery_clienti(vis)))
              .where(Cliente.utente_id.in_(v.sottoquery_clienti(vis))))
    with pytest.raises(CompileError):
        str(doppia.compile(engine))


# =============================================================================
# Protezione della ricorsione
# =============================================================================
def _catena(db, lunghezza):
    padri = {1: None} | {u: u - 1 for u in range(2, lunghezza + 2)}
    righe = [(u, u, 1 if u == 1 else 0, None) for u in padri]
    carica(db, padri, righe)
    return db.get(Utente, 1)


def test_senza_protezione_il_database_tronca_in_silenzio(db):
    """Il motivo del listener: nessun errore, solo un risultato parziale."""
    testa = _catena(db, 1100)
    event.remove(engine, "before_cursor_execute", v._alza_limite_ricorsione)
    event.remove(engine, "after_cursor_execute", v._verifica_troncamento)
    try:
        visibili = db.scalars(v.clienti_visibili(db, testa)).all()
    finally:
        event.listen(engine, "before_cursor_execute", v._alza_limite_ricorsione, retval=True)
        event.listen(engine, "after_cursor_execute", v._verifica_troncamento)
    assert 1000 <= len(visibili) < 1101


def test_un_troncamento_diventa_un_errore(db, monkeypatch):
    testa = _catena(db, 60)
    monkeypatch.setattr(v, "MAX_ITERAZIONI", 50)
    with pytest.raises(v.RicorsioneTroncata):
        db.scalars(v.clienti_visibili(db, testa)).all()


def test_con_stream_results_si_rifiuta(db):
    testa = _catena(db, 3)
    sotto = v.clienti_visibili(db, testa)
    with pytest.raises(v.RicorsioneNonVerificata):
        db.execute(sotto.execution_options(stream_results=True)).all()


def test_il_limite_resta_sullo_statement(db):
    """SET STATEMENT vale per una sola istruzione: la connessione, che poi
    torna nel pool, conserva il limite predefinito."""
    testa = _catena(db, 5)
    db.scalars(v.clienti_visibili(db, testa)).all()
    assert db.execute(text("SELECT @@session.max_recursive_iterations")).scalar() == 1000
