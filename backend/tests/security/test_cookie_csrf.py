"""Contratto browser: cookie, origine, CSRF, rotazione e nessun bearer."""

import pytest
from sqlalchemy import select

from src.auth.models import AuthSessione
from src.security.browser import nome_cookie
from src.security.password import hash_password
from src.security.sessioni import valida_sessione
from tests.support import factories as f
from tests.support.sessioni import token_cookie, intestazioni_sessione

pytestmark = pytest.mark.mariadb
PASSWORD = "password-sintetica-test"


def accesso(client, db):
    utente = f.crea_attuatore(db, email="cookie@example.org", password_hash=hash_password(PASSWORD))
    dati = {"utente_username": utente.username, "utente_password": PASSWORD}
    risposta = client.post("/auth/login", json=dati)
    assert risposta.status_code == 200
    return dati, risposta


def test_cookie_sicuro_bootstrap_e_nessun_token_nel_json(client, db):
    _, risposta = accesso(client, db)
    cookie = risposta.headers["set-cookie"]
    assert nome_cookie().startswith("__Host-")
    for attributo in ("HttpOnly", "Secure", "SameSite=lax", "Path=/", "Max-Age=1209600"):
        assert attributo in cookie
    assert "Domain=" not in cookie
    assert "token" not in risposta.json() and "token_type" not in risposta.json()
    bootstrap = client.get("/auth/session")
    assert bootstrap.status_code == 200
    assert bootstrap.json()["csrf_token"] == risposta.json()["csrf_token"]
    assert token_cookie(risposta) not in bootstrap.text
    assert bootstrap.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("csrf", [None, "", "a" * 64, "token-di-altra-sessione"])
def test_cookie_senza_csrf_corretto_non_puo_scrivere(client, db, csrf):
    accesso(client, db)
    headers = {} if csrf is None else {"X-CSRF-Token": csrf}
    risposta = client.post("/auth/logout", headers=headers)
    assert risposta.status_code == 403
    assert risposta.json()["detail"]["codice"] == "csrf_non_valido"
    assert db.execute(select(AuthSessione.sess_revoked_at)).scalar_one() is None


@pytest.mark.parametrize("origine", ["https://estraneo.example", "null", "https://test.example.org.evil.test"])
def test_origine_estranea_respinta_anche_con_csrf(client, db, origine):
    dati, risposta = accesso(client, db)
    headers = {**intestazioni_sessione(token_cookie(risposta)), "Origin": origine}
    assert client.post("/auth/logout", headers=headers).status_code == 403
    assert client.post("/auth/login", json=dati, headers=headers).status_code == 403


def test_login_csrf_senza_header_non_emette_sessione(client, db):
    client.headers.pop("X-ERSAF-Request")
    assert client.post("/auth/login", json={"utente_username": "ignoto", "utente_password": "x"}).status_code == 403
    assert db.execute(select(AuthSessione)).first() is None


def test_bearer_valido_non_sostituisce_cookie(client, db):
    _, risposta = accesso(client, db)
    token = token_cookie(risposta)
    client.cookies.clear()
    assert client.get("/auth/session", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_rotazione_invalida_sessione_precedente_e_csrf(client, db):
    dati, prima = accesso(client, db)
    seconda = client.post("/auth/login", json=dati)
    assert token_cookie(prima) != token_cookie(seconda)
    assert valida_sessione(db, token_cookie(prima)) is None
    assert client.post("/auth/logout", headers={"X-CSRF-Token": prima.json()["csrf_token"]}).status_code == 403
    uscita = client.post("/auth/logout", headers={"X-CSRF-Token": seconda.json()["csrf_token"]})
    assert uscita.status_code == 204
    assert "Max-Age=0" in uscita.headers["set-cookie"]
    assert client.get("/auth/session").status_code == 401


def test_preflight_estraneo_non_abilita_credenziali(client):
    risposta = client.options("/auth/login", headers={
        "Origin": "https://estraneo.example", "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "x-ersaf-request,content-type",
    })
    assert risposta.status_code == 400
    assert "access-control-allow-origin" not in risposta.headers


def test_origine_consentita_puo_leggere_attesa_e_usare_csrf(client):
    headers = {"Origin": "https://test.example.org"}
    preflight = client.options("/auth/logout", headers={**headers,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "x-ersaf-request,x-csrf-token,content-type",
    })
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == headers["Origin"]
    for _ in range(5):
        risposta = client.post("/auth/login", headers=headers,
                              json={"utente_username": "inesistente", "utente_password": "x"})
        assert risposta.status_code == 401
    limitata = client.post("/auth/login", headers=headers,
                          json={"utente_username": "inesistente", "utente_password": "x"})
    assert limitata.status_code == 429
    assert "Retry-After" in limitata.headers["access-control-expose-headers"]
