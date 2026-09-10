"""Consumo del token monouso sotto concorrenza.

QUATTRO LIVELLI, e servono tutti e quattro.

Un test a due thread che chiama l'endpoint quasi sempre si serializza da solo:
il primo finisce prima che il secondo arrivi alla UPDATE. Passerebbe anche con
un'implementazione SELECT -> if -> UPDATE, che e' esattamente il difetto da
trovare. Un test che non puo' fallire non e' un test.

  1. deterministico, senza concorrenza: verifica cio' che l'applicazione
     possiede davvero, cioe' che il valore di ritorno venga controllato;
  2. atomicita' della SQL, con due connessioni in sequenza fissata;
  3. CONTROLLO NEGATIVO: con un'implementazione non atomica il doppio consumo
     deve avvenire. Se non avviene, l'apparato non e' realmente concorrente e
     il livello 4 non dimostra nulla;
  4. end-to-end sull'endpoint, con una barriera.
"""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import func, select, update

from src.auth.models import AuthSessione, PasswordResetToken
from src.database import SessionLocal, engine
from src.security.tokens import TipoToken, impronta
from src.utenti.models import Utente
from tests.conftest import corpo_html
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

NUOVA = "cavallo-batteria-graffetta-nuova"


def _token_per(client, db, email):
    from src.notifiche.backend_invio import backend_memoria

    attuatore = f.crea_attuatore(db, email=email)
    client.post("/auth/password-reset/request", json={"email": email})
    html = corpo_html(backend_memoria().inviate[-1])
    token = html.split("token=")[1].split('"')[0].split("<")[0]
    db.commit()
    return attuatore, token


def _corpo(token, password=NUOVA):
    return {"token": token, "password": password, "password_conferma": password}


# --- livello 1: deterministico ----------------------------------------------


def test_rowcount_zero_non_cambia_nulla(client, db, monkeypatch, mailer):
    """Il test piu' prezioso dei quattro, ed e' deterministico: verifica che il
    valore di ritorno del consumo venga controllato davvero."""
    attuatore, token = _token_per(client, db, "livello1@example.org")
    hash_prima = db.get(Utente, attuatore.utente_id).utente_password_hash
    mailer.svuota()

    import src.auth.routers as rotte

    monkeypatch.setattr(rotte, "consuma_token", lambda *a, **k: 0)
    risposta = client.post("/auth/password-reset/confirm", json=_corpo(token))

    assert risposta.status_code == 400
    db.commit()
    db.expire_all()
    utente = db.get(Utente, attuatore.utente_id)
    assert utente.utente_password_hash == hash_prima
    assert utente.utente_password_changed_at is None
    assert db.execute(select(AuthSessione)).first() is None
    assert mailer.inviate == []


# --- livello 2: atomicita' della SQL ----------------------------------------


def _update_condizionale(connessione, impronta_token: str) -> int:
    esito = connessione.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.prt_token_hash == impronta_token,
            PasswordResetToken.prt_consumed_at.is_(None),
            PasswordResetToken.prt_revoked_at.is_(None),
            PasswordResetToken.prt_expires_at > func.now(),
        )
        .values(prt_consumed_at=func.now())
    )
    return esito.rowcount


def test_la_update_condizionale_e_atomica(client, db):
    """Due connessioni, sequenza fissata: A blocca la riga, B attende, A
    committa, B trova zero righe.

    Sotto REPEATABLE READ questo NON e' un falso positivo, e vale la pena
    saperlo: in InnoDB un UPDATE esegue una lettura con blocco, che vede la
    versione piu' recente committata e non lo snapshot della transazione. Un
    SELECT non bloccante prima dell'UPDATE leggerebbe invece lo snapshot e
    vedrebbe il token ancora valido — ed e' precisamente il motivo per cui la
    migrazione 002 impone la UPDATE condizionale.
    """
    _, token = _token_per(client, db, "livello2@example.org")
    impronta_token = impronta(token, TipoToken.RESET)

    risultati: dict[str, int] = {}
    b_ha_iniziato = threading.Event()

    connessione_a = engine.connect()
    transazione_a = connessione_a.begin()
    risultati["a"] = _update_condizionale(connessione_a, impronta_token)

    def secondo():
        with engine.connect() as connessione_b:
            with connessione_b.begin():
                b_ha_iniziato.set()
                risultati["b"] = _update_condizionale(connessione_b, impronta_token)

    thread = threading.Thread(target=secondo)
    thread.start()
    b_ha_iniziato.wait(timeout=5)
    transazione_a.commit()
    connessione_a.close()
    thread.join(timeout=15)

    assert risultati["a"] == 1
    assert risultati["b"] == 0, "il secondo consumo doveva trovare zero righe"


def test_controllo_negativo_una_update_incondizionata_consuma_due_volte(client, db):
    """Se questo test NON producesse il doppio consumo, l'apparato non sarebbe
    realmente concorrente e il test precedente non dimostrerebbe nulla."""
    _, token = _token_per(client, db, "negativo@example.org")
    impronta_token = impronta(token, TipoToken.RESET)

    def incondizionata(connessione) -> int:
        # Senza le tre guardie nella WHERE. Con CLIENT.FOUND_ROWS, che
        # SQLAlchemy attiva sempre sui dialetti MySQL, rowcount conta le righe
        # TROVATE: la riga viene trovata anche al replay.
        return connessione.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.prt_token_hash == impronta_token)
            .values(prt_consumed_at=func.now())
        ).rowcount

    with engine.begin() as connessione:
        primo = incondizionata(connessione)
    with engine.begin() as connessione:
        secondo = incondizionata(connessione)

    assert primo == 1
    assert secondo == 1, (
        "la versione senza guardie deve consumare due volte: se qui uscisse 0, "
        "le guardie nella WHERE non sarebbero portanti e il test di atomicita' "
        "sarebbe vacuo"
    )


# --- livello 4: end-to-end --------------------------------------------------


@pytest.mark.lento
def test_due_conferme_simultanee_una_sola_vince(client, db, mailer):
    """Barriera su una seam legittima — la funzione di repository — cosi' i due
    thread arrivano insieme alla UPDATE. Nessun hook di sincronizzazione viene
    aggiunto al codice di produzione."""
    from fastapi.testclient import TestClient

    import src.auth.routers as rotte
    from src.main import app

    attuatore, token = _token_per(client, db, "concorrenza@example.org")
    mailer.svuota()

    reale = rotte.consuma_token
    barriera = threading.Barrier(2, timeout=15)
    conteggio_hash = []

    def con_barriera(*args, **kwargs):
        barriera.wait()
        return reale(*args, **kwargs)

    hash_reale = rotte.hash_password

    def conta_hash(password):
        conteggio_hash.append(password)
        return hash_reale(password)

    rotte.consuma_token = con_barriera
    rotte.hash_password = conta_hash
    try:
        def invia():
            # Due client distinti: non si condivide il portal di anyio.
            with TestClient(
                app, client=("203.0.113.7", 44444), raise_server_exceptions=False
            ) as istanza:
                return istanza.post(
                    "/auth/password-reset/confirm", json=_corpo(token)
                ).status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            codici = sorted(f.result() for f in [pool.submit(invia), pool.submit(invia)])
    finally:
        rotte.consuma_token = reale
        rotte.hash_password = hash_reale

    assert codici == [200, 400], f"attesi un successo e un rifiuto, ottenuti {codici}"

    db.commit()
    riga = db.execute(select(PasswordResetToken)).scalar_one()
    assert riga.prt_consumed_at is not None
    # La password e' stata scritta una volta sola: due bcrypt darebbero salt
    # diversi e la differenza sarebbe invisibile senza contare le chiamate.
    assert len(conteggio_hash) == 2, "entrambe le richieste calcolano l'hash..."
    utente = db.get(Utente, attuatore.utente_id)
    assert utente.utente_password_changed_at is not None
    # ...ma una sola lo scrive.
    assert len(mailer.inviate) == 1
