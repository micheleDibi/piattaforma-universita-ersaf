"""Sessioni: validazione, revoca e sostituzione dell'header x-utente-id."""

from __future__ import annotations

import pytest
from sqlalchemy import select, text, update

from src.auth.models import AuthSessione, MotivoRevoca
from src.security.password import hash_password
from src.security.sessioni import revoca_sessioni_utente
from src.security.tempo import istante_meno_ore, istante_piu_minuti
from src.utenti.models import Utente
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

PASSWORD = "cavallo-batteria-graffetta"


def _accedi(client, db, email="utente@example.org", **kwargs):
    attuatore = f.crea_attuatore(
        db, email=email, password_hash=hash_password(PASSWORD), **kwargs
    )
    risposta = client.post(
        "/auth/login",
        json={"utente_username": attuatore.username, "utente_password": PASSWORD},
    )
    assert risposta.status_code == 200
    return attuatore, risposta.json()["token"]


def _intestazione(token):
    return {"Authorization": f"Bearer {token}"}


def test_una_rotta_protetta_richiede_il_bearer(client, db):
    """POST /utenti/ era l'unico endpoint autenticato, e si fidava di un intero
    non firmato passato in un header."""
    corpo = {"utente_username": "nuovo", "utente_password": "cavallo-batteria-1"}
    assert client.post("/utenti/", json=corpo).status_code == 401
    # L'header legacy non vale piu' nulla.
    assert client.post("/utenti/", json=corpo, headers={"x-utente-id": "1"}).status_code == 401


def test_token_valido_autentica(client, db):
    _, token = _accedi(client, db)
    risposta = client.post(
        "/utenti/",
        json={"utente_username": "creato-da-test", "utente_password": "cavallo-batteria-1"},
        headers=_intestazione(token),
    )
    assert risposta.status_code == 201


@pytest.mark.parametrize(
    "intestazioni",
    [
        {},
        {"Authorization": "Bearer non-un-token"},
        {"Authorization": "Bearer " + "a" * 43},
        {"Authorization": "Basic YWJjOmRlZg=="},
    ],
)
def test_token_assente_o_non_valido(client, db, intestazioni):
    risposta = client.post(
        "/utenti/",
        json={"utente_username": "x", "utente_password": "cavallo-batteria-1"},
        headers=intestazioni,
    )
    assert risposta.status_code == 401


def test_sessione_revocata_non_vale_piu(client, db):
    attuatore, token = _accedi(client, db)
    revoca_sessioni_utente(db, attuatore.utente_id, MotivoRevoca.PASSWORD_RESET)
    db.commit()
    risposta = client.post(
        "/utenti/",
        json={"utente_username": "x", "utente_password": "cavallo-batteria-1"},
        headers=_intestazione(token),
    )
    assert risposta.status_code == 401


def test_sessione_scaduta_non_vale_piu(client, db):
    attuatore, token = _accedi(client, db)
    db.execute(
        update(AuthSessione)
        .where(AuthSessione.utente_id == attuatore.utente_id)
        .values(sess_expires_at=istante_meno_ore(1))
    )
    db.commit()
    assert client.post("/auth/logout", headers=_intestazione(token)).status_code == 204
    risposta = client.post(
        "/utenti/",
        json={"utente_username": "x", "utente_password": "cavallo-batteria-1"},
        headers=_intestazione(token),
    )
    assert risposta.status_code == 401


def test_utente_disattivato_dopo_il_login_perde_la_sessione(client, db):
    """La query [B] della 004 controlla utente_attivoSN a ogni richiesta."""
    attuatore, token = _accedi(client, db)
    db.execute(
        update(Utente)
        .where(Utente.utente_id == attuatore.utente_id)
        .values(utente_attivoSN=f.DISATTIVO)
    )
    db.commit()
    risposta = client.post(
        "/utenti/",
        json={"utente_username": "x", "utente_password": "cavallo-batteria-1"},
        headers=_intestazione(token),
    )
    assert risposta.status_code == 401


def test_sessione_anteriore_al_cambio_password_viene_scartata(client, db):
    """Difesa in profondita' della query [B]: anche se la revoca massiva
    fallisse, una sessione nata prima dell'ultimo cambio password non vale."""
    attuatore, token = _accedi(client, db)
    db.execute(
        update(Utente)
        .where(Utente.utente_id == attuatore.utente_id)
        .values(utente_password_changed_at=istante_piu_minuti(1))
    )
    db.commit()
    # La sessione NON e' marcata revocata: e' la sola data a squalificarla.
    sessione = db.execute(select(AuthSessione)).scalar_one()
    assert sessione.sess_revoked_at is None

    risposta = client.post(
        "/utenti/",
        json={"utente_username": "x", "utente_password": "cavallo-batteria-1"},
        headers=_intestazione(token),
    )
    assert risposta.status_code == 401


def test_logout_revoca_solo_la_propria_sessione(client, db):
    attuatore, token_uno = _accedi(client, db, email="uno@example.org")
    risposta = client.post(
        "/auth/login",
        json={"utente_username": attuatore.username, "utente_password": PASSWORD},
    )
    token_due = risposta.json()["token"]

    assert client.post("/auth/logout", headers=_intestazione(token_uno)).status_code == 204

    db.commit()
    sessioni = db.execute(select(AuthSessione).order_by(AuthSessione.sess_id)).scalars().all()
    assert sessioni[0].sess_revoked_at is not None
    assert sessioni[0].sess_revoked_reason == "logout"
    assert sessioni[1].sess_revoked_at is None

    corpo = {"utente_username": "x", "utente_password": "cavallo-batteria-1"}
    assert client.post("/utenti/", json=corpo, headers=_intestazione(token_uno)).status_code == 401
    assert client.post("/utenti/", json=corpo, headers=_intestazione(token_due)).status_code == 201


def test_logout_e_sempre_204(client, db):
    """Un codice diverso direbbe al chiamante se quel token e' mai esistito."""
    assert client.post("/auth/logout").status_code == 204
    assert client.post("/auth/logout", headers=_intestazione("a" * 43)).status_code == 204
    _, token = _accedi(client, db)
    assert client.post("/auth/logout", headers=_intestazione(token)).status_code == 204
    assert client.post("/auth/logout", headers=_intestazione(token)).status_code == 204


def test_le_sessioni_di_altri_utenti_non_sono_toccate(client, db):
    primo, token_primo = _accedi(client, db, email="primo@example.org")
    secondo, token_secondo = _accedi(client, db, email="secondo@example.org")

    revoca_sessioni_utente(db, primo.utente_id, MotivoRevoca.PASSWORD_RESET)
    db.commit()

    corpo = {"utente_username": "x", "utente_password": "cavallo-batteria-1"}
    assert client.post("/utenti/", json=corpo, headers=_intestazione(token_primo)).status_code == 401
    assert client.post("/utenti/", json=corpo, headers=_intestazione(token_secondo)).status_code == 201


def test_piu_richieste_con_lo_stesso_token(client, db):
    """Regressione: il difetto si vedeva solo dalla SECONDA richiesta in poi.

    segna_ultimo_accesso confrontava `sess_last_seen_at < func.now() - timedelta(...)`.
    SQLAlchemy legava il timedelta come parametro DATETIME, quindi MariaDB
    riceveva `NOW() - '00:05:00'` e faceva una sottrazione NUMERICA. Con
    sql_mode STRICT_TRANS_TABLES — un default diffuso — l'UPDATE falliva con
    1292 "Truncated incorrect DOUBLE value", e ogni chiamata autenticata dava
    500.

    Alla prima richiesta non si vedeva: `sess_last_seen_at` era NULL, il primo
    ramo dell'OR bastava e MariaDB non valutava nemmeno il secondo. Serve
    quindi almeno una seconda richiesta con lo STESSO token.
    """
    attuatore, token = _accedi(client, db, email="ripetute@example.org")
    corpo = {"utente_username": "x", "utente_password": "cavallo-batteria-1"}

    prima = client.post("/utenti/", json=corpo, headers=_intestazione(token))
    assert prima.status_code == 201

    db.commit()
    sessione = db.execute(select(AuthSessione)).scalar_one()
    assert sessione.sess_last_seen_at is not None, "la prima richiesta deve segnare l'accesso"

    for numero in range(3):
        successiva = client.post(
            "/utenti/",
            json={"utente_username": f"y{numero}", "utente_password": "cavallo-batteria-1"},
            headers=_intestazione(token),
        )
        assert successiva.status_code == 201, (
            f"richiesta {numero + 2} fallita con {successiva.status_code}: "
            "sess_last_seen_at non e' piu' NULL e il confronto della soglia "
            "viene finalmente valutato"
        )


def test_la_soglia_dell_ultimo_accesso_e_un_intervallo_vero(client, db):
    """Il confronto deve usare INTERVAL, non una sottrazione numerica.

    Con la sottrazione numerica la condizione era sempre falsa e la soglia non
    funzionava: o l'UPDATE falliva, o non aggiornava mai piu' dopo la prima
    volta.
    """
    attuatore, token = _accedi(client, db, email="soglia@example.org")
    corpo = {"utente_username": "z", "utente_password": "cavallo-batteria-1"}
    client.post("/utenti/", json=corpo, headers=_intestazione(token))

    db.commit()
    # Si finge che l'ultimo accesso sia di un'ora fa: la soglia deve scattare.
    db.execute(update(AuthSessione).values(sess_last_seen_at=istante_meno_ore(1)))
    db.commit()
    vecchio = db.execute(select(AuthSessione.sess_last_seen_at)).scalar_one()

    client.post(
        "/utenti/",
        json={"utente_username": "z2", "utente_password": "cavallo-batteria-1"},
        headers=_intestazione(token),
    )
    db.commit()
    db.expire_all()
    nuovo = db.execute(select(AuthSessione.sess_last_seen_at)).scalar_one()
    assert nuovo > vecchio, "oltre la soglia l'ultimo accesso deve essere aggiornato"
