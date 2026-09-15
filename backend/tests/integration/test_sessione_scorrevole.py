"""Sessione scorrevole (ADR 0008): finestra, rinnovo del cookie, tetto assoluto."""

from __future__ import annotations

import pytest
from sqlalchemy import select, update

from src.auth.models import AuthSessione
from src.config import get_impostazioni
from src.security.browser import nome_cookie
from src.security.password import hash_password
from src.security.tempo import istante_meno_giorni, istante_meno_ore, istante_piu_giorni
from tests.support import factories as f
from tests.support.sessioni import token_cookie

pytestmark = pytest.mark.mariadb

PASSWORD = "cavallo-batteria-graffetta"
FINESTRA = get_impostazioni().session_inattivita_giorni
TETTO = get_impostazioni().session_durata_massima_giorni


def _accedi(client, db, email="scorrevole@example.org"):
    attuatore = f.crea_attuatore(db, email=email, password_hash=hash_password(PASSWORD))
    risposta = client.post(
        "/auth/login",
        json={"utente_username": attuatore.username, "utente_password": PASSWORD},
    )
    assert risposta.status_code == 200
    return token_cookie(risposta)


def _scade_fra_giorni(db, minimo: int, massimo: int) -> bool:
    """Vero se l'unica sessione scade fra NOW()+minimo e NOW()+massimo giorni,
    sull'orologio del database (src/security/tempo.py)."""
    return bool(db.scalar(select(
        (AuthSessione.sess_expires_at > istante_piu_giorni(minimo))
        & (AuthSessione.sess_expires_at < istante_piu_giorni(massimo))
    )))


def _invecchia(db, **valori):
    db.execute(update(AuthSessione).values(**valori))
    db.commit()


def test_al_login_la_scadenza_e_la_finestra_di_inattivita(client, db):
    _accedi(client, db)
    assert _scade_fra_giorni(db, FINESTRA - 1, FINESTRA + 1)


def test_l_uso_oltre_la_soglia_rinnova_scadenza_e_cookie(client, db):
    token = _accedi(client, db)
    # Ultimo accesso di un'ora fa e scadenza vicina: il rinnovo deve scattare.
    _invecchia(db, sess_last_seen_at=istante_meno_ore(1), sess_expires_at=istante_piu_giorni(1))

    risposta = client.get("/auth/session")
    assert risposta.status_code == 200
    cookie = risposta.headers["set-cookie"]
    assert f"{nome_cookie()}={token}" in cookie, "stesso token: e' un rinnovo, non una rotazione"
    assert f"Max-Age={FINESTRA * 86400}" in cookie
    assert _scade_fra_giorni(db, FINESTRA - 1, FINESTRA + 1)


def test_entro_la_soglia_nessuna_scrittura_e_nessun_cookie(client, db):
    _accedi(client, db)
    primo = client.get("/auth/session")  # sess_last_seen_at era NULL: rinnova
    assert primo.status_code == 200 and "set-cookie" in primo.headers
    secondo = client.get("/auth/session")  # pochi millisecondi dopo: no
    assert secondo.status_code == 200
    assert "set-cookie" not in secondo.headers


@pytest.mark.parametrize("giorni_fa, atteso", [(TETTO - 1, 200), (TETTO + 1, 401)])
def test_il_tetto_assoluto_si_misura_dalla_creazione(client, db, giorni_fa, atteso):
    """Una sessione usata ogni giorno resta valida solo fino al tetto: la data
    di creazione la squalifica anche con la scadenza scorrevole nel futuro."""
    _accedi(client, db)
    _invecchia(
        db,
        sess_created_at=istante_meno_giorni(giorni_fa),
        sess_last_seen_at=istante_meno_ore(1),
        sess_expires_at=istante_piu_giorni(FINESTRA),
    )
    assert client.get("/auth/session").status_code == atteso


def test_la_sessione_respinta_dal_tetto_non_viene_rinnovata(client, db):
    """Il rinnovo avviene dopo la validazione: la richiesta che respinge una
    sessione oltre il tetto non deve spostarne la scadenza."""
    _accedi(client, db)
    _invecchia(db, sess_created_at=istante_meno_giorni(TETTO + 1), sess_expires_at=istante_piu_giorni(1))
    assert client.get("/auth/session").status_code == 401
    assert _scade_fra_giorni(db, 0, 2)
