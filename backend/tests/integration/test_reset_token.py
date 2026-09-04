"""GET /validate e POST /confirm: ciclo di vita del token."""

from __future__ import annotations

import pytest
from sqlalchemy import select, update

from src.auth.models import AuthSessione, PasswordResetToken
from src.security.password import hash_password, verify_password
from src.security.tempo import istante_meno_ore
from src.security.tokens import TipoToken, genera_token, impronta
from src.utenti.models import Utente
from tests.conftest import corpo_html
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

NUOVA = "cavallo-batteria-graffetta-nuova"


def _token_per(client, db, email="utente@example.org", **kwargs):
    """Fa una richiesta vera e recupera il token dal link nella mail: e' l'unico
    posto in cui il token in chiaro esiste, ed e' giusto che i test lo prendano
    da li'."""
    from src.notifiche.backend_invio import backend_memoria

    attuatore = f.crea_attuatore(db, email=email, **kwargs)
    client.post("/auth/password-reset/request", json={"email": email})
    html = corpo_html(backend_memoria().inviate[-1])
    token = html.split("token=")[1].split('"')[0].split("<")[0]
    db.commit()
    return attuatore, token


def _valida(client, token):
    return client.get("/auth/password-reset/validate", params={"token": token})


def _conferma(client, token, password=NUOVA, conferma=None):
    return client.post(
        "/auth/password-reset/confirm",
        json={
            "token": token,
            "password": password,
            "password_conferma": conferma if conferma is not None else password,
        },
    )


# --- validate ---------------------------------------------------------------


def test_token_valido(client, db):
    _, token = _token_per(client, db)
    assert _valida(client, token).json() == {"valido": True}


def test_validate_non_consuma_il_token(client, db):
    """Il prefetch di un client di posta o un crawler brucerebbe il token."""
    _, token = _token_per(client, db)
    prima = db.execute(select(PasswordResetToken)).scalar_one()
    istantanea = {c.name: getattr(prima, c.name) for c in PasswordResetToken.__table__.c}

    for _ in range(3):
        assert _valida(client, token).json() == {"valido": True}

    db.commit()
    db.expire_all()
    dopo = db.execute(select(PasswordResetToken)).scalar_one()
    assert {c.name: getattr(dopo, c.name) for c in PasswordResetToken.__table__.c} == istantanea
    # E il token funziona ancora.
    assert _conferma(client, token).status_code == 200


def test_token_scaduto(client, db):
    _, token = _token_per(client, db)
    db.execute(update(PasswordResetToken).values(prt_expires_at=istante_meno_ore(1)))
    db.commit()
    assert _valida(client, token).json() == {"valido": False, "motivo": "scaduto"}


def test_token_gia_consumato(client, db):
    _, token = _token_per(client, db)
    assert _conferma(client, token).status_code == 200
    assert _valida(client, token).json() == {"valido": False, "motivo": "gia_usato"}


def test_token_revocato_risulta_non_valido(client, db):
    """Dire "revocato" confermerebbe che quel token e' esistito."""
    attuatore, primo = _token_per(client, db, email="revocato@example.org")
    client.post("/auth/password-reset/request", json={"email": attuatore.email})
    assert _valida(client, primo).json() == {"valido": False, "motivo": "non_valido"}


@pytest.mark.parametrize(
    "token", ["", "corto", "a" * 43, "<script>", "a" * 44, "-" * 43]
)
def test_token_inesistente_o_malformato(client, db, token):
    assert _valida(client, token).json() == {"valido": False, "motivo": "non_valido"}


def test_token_manomesso_di_un_carattere(client, db):
    _, token = _token_per(client, db)
    alterato = ("b" if token[0] != "b" else "c") + token[1:]
    assert len(alterato) == len(token)
    assert _valida(client, alterato).json() == {"valido": False, "motivo": "non_valido"}


def test_validate_non_rivela_l_utente(client, db):
    _, token = _token_per(client, db)
    assert set(_valida(client, token).json()) == {"valido"}


# --- confirm ----------------------------------------------------------------


def test_conferma_cambia_la_password(client, db):
    attuatore, token = _token_per(client, db, email="cambio@example.org")

    risposta = _conferma(client, token)
    assert risposta.status_code == 200
    # L'utente non viene autenticato: la risposta rimanda al login.
    assert "token" not in risposta.json()
    assert "utente_id" not in risposta.json()

    db.commit()
    db.expire_all()
    utente = db.get(Utente, attuatore.utente_id)
    assert verify_password(NUOVA, utente.utente_password_hash)
    assert utente.utente_password == ""          # NOT NULL: stringa vuota
    assert utente.utente_password_algo == "bcrypt"
    assert utente.utente_password_changed_at is not None
    assert utente.utente_password_changed_via == "reset_email"


def test_dopo_il_cambio_si_accede_con_la_nuova_password(client, db):
    attuatore, token = _token_per(client, db, email="accesso@example.org",
                                  password_hash=hash_password("VecchiaPassword123"))
    assert _conferma(client, token).status_code == 200

    def accedi(password):
        return client.post(
            "/auth/login",
            json={"utente_username": attuatore.username, "utente_password": password},
        ).status_code

    assert accedi(NUOVA) == 200
    assert accedi("VecchiaPassword123") == 401


def test_tutte_le_sessioni_vengono_revocate(client, db):
    """Requisito 14: la query [A] della 004, nella stessa transazione."""
    attuatore, token = _token_per(
        client, db, email="sessioni@example.org", password_hash=hash_password("Password123456")
    )
    sessioni = []
    for _ in range(3):
        risposta = client.post(
            "/auth/login",
            json={"utente_username": attuatore.username, "utente_password": "Password123456"},
        )
        sessioni.append(risposta.json()["token"])

    assert _conferma(client, token).status_code == 200

    db.commit()
    righe = db.execute(select(AuthSessione)).scalars().all()
    assert len(righe) == 3
    assert all(r.sess_revoked_at is not None for r in righe)
    assert all(r.sess_revoked_reason == "password_reset" for r in righe)

    corpo = {"utente_username": "x", "utente_password": "cavallo-batteria-1"}
    for sessione in sessioni:
        assert client.post(
            "/utenti/", json=corpo, headers={"Authorization": f"Bearer {sessione}"}
        ).status_code == 401


def test_gli_altri_token_dell_utente_vengono_revocati(client, db):
    """Query [D] della 002."""
    attuatore, _ = _token_per(client, db, email="altri@example.org")
    # Una seconda richiesta genera un secondo token e revoca il primo.
    client.post("/auth/password-reset/request", json={"email": attuatore.email})
    from src.notifiche.backend_invio import backend_memoria

    html = corpo_html(backend_memoria().inviate[-1])
    secondo = html.split("token=")[1].split('"')[0].split("<")[0]

    assert _conferma(client, secondo).status_code == 200

    db.commit()
    token = db.execute(
        select(PasswordResetToken).order_by(PasswordResetToken.prt_id)
    ).scalars().all()
    assert token[0].prt_revoked_reason == "nuova_richiesta"
    assert token[1].prt_consumed_at is not None


def test_token_consumato_due_volte_cambia_la_password_una_volta_sola(client, db):
    attuatore, token = _token_per(client, db, email="doppio@example.org")

    assert _conferma(client, token).status_code == 200
    db.commit()
    db.expire_all()
    hash_dopo_il_primo = db.get(Utente, attuatore.utente_id).utente_password_hash

    seconda = _conferma(client, token, password="un-altra-password-lunga")
    assert seconda.status_code == 400

    db.commit()
    db.expire_all()
    assert db.get(Utente, attuatore.utente_id).utente_password_hash == hash_dopo_il_primo


@pytest.mark.parametrize(
    "descrizione, password, atteso",
    [
        ("troppo corta", "Corta123", 422),
        ("oltre 72 byte", "a" * 73, 422),
        ("nella blocklist", "Password1234!", 422),
    ],
)
def test_policy_violata_non_consuma_il_token(client, db, descrizione, password, atteso):
    _, token = _token_per(client, db, email=f"policy{atteso}@example.org")
    assert _conferma(client, token, password=password).status_code == atteso
    db.commit()
    assert db.execute(select(PasswordResetToken)).scalar_one().prt_consumed_at is None
    # Il token e' ancora utilizzabile.
    assert _conferma(client, token).status_code == 200


def test_password_non_coincidenti(client, db):
    _, token = _token_per(client, db, email="diverse@example.org")
    risposta = _conferma(client, token, password=NUOVA, conferma="tutt-altra-password")
    assert risposta.status_code == 422
    assert risposta.json()["detail"]["codice"] == "password_non_coincidono"
    db.commit()
    assert db.execute(select(PasswordResetToken)).scalar_one().prt_consumed_at is None


def test_password_uguale_all_email(client, db):
    _, token = _token_per(client, db, email="uguale@example.org")
    risposta = _conferma(client, token, password="uguale@example.org")
    assert risposta.status_code == 422
    assert "uguale_email" in risposta.json()["detail"]["regole_violate"]


def test_password_uguale_allo_username(client, db):
    attuatore, token = _token_per(
        client, db, email="username@example.org", username="mario.rossi.lungo"
    )
    risposta = _conferma(client, token, password="mario.rossi.lungo")
    assert risposta.status_code == 422
    assert "uguale_username" in risposta.json()["detail"]["regole_violate"]


def test_token_scaduto_non_cambia_la_password(client, db):
    attuatore, token = _token_per(client, db, email="scaduto@example.org")
    db.execute(update(PasswordResetToken).values(prt_expires_at=istante_meno_ore(1)))
    db.commit()

    assert _conferma(client, token).status_code == 400
    db.expire_all()
    assert db.get(Utente, attuatore.utente_id).utente_password_hash is None


def test_token_inesistente(client, db):
    assert _conferma(client, genera_token()).status_code == 400


def test_la_mail_di_notifica_non_contiene_token_ne_password(client, db, mailer):
    attuatore, token = _token_per(client, db, email="notifica@example.org")
    mailer.svuota()

    assert _conferma(client, token).status_code == 200

    assert len(mailer.inviate) == 1
    html = corpo_html(mailer.inviate[0])
    assert token not in html
    assert NUOVA not in html
    assert impronta(token, TipoToken.RESET) not in html
    assert "token=" not in html
    assert "{{" not in html
    # Nessuna stringa che somigli a un token: coglie anche il caso in cui
    # qualcuno interpolasse per sbaglio un valore diverso.
    import re
    assert not re.search(r"[A-Za-z0-9_-]{40,}", html)


def test_il_contesto_del_consumo_e_registrato(client, db):
    _, token = _token_per(client, db, email="contesto@example.org")
    assert _conferma(client, token).status_code == 200
    db.commit()
    riga = db.execute(select(PasswordResetToken)).scalar_one()
    assert riga.prt_consumed_at is not None
    assert riga.prt_consumed_ip is not None
