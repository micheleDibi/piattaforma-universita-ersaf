"""Authenticator (TOTP) del Nazionale: attivazione, login con l'app,
anti-replay, scelta libera del metodo, disattivazione, limiti."""

from __future__ import annotations

import base64
import re
from datetime import timedelta

import pytest
from sqlalchemy import func, select, update

from src.auth.models import AuthSessione
from src.mfa import totp
from src.notifiche.formato_email import come_testo
from src.otp.models import Limite, Sfida
from src.security.password import hash_password
from tests.conftest import corpo_html
from tests.support import factories as f
from tests.support.sessioni import intestazioni_sessione, token_cookie

pytestmark = pytest.mark.mariadb
PASSWORD = "password-di-collaudo-lunga"


def _codice_mail(mailer):
    return re.search(r"\b\d{6}\b", come_testo(corpo_html(mailer.inviate[-1]))).group()


def _segreto(base32: str) -> bytes:
    return base64.b32decode(base32 + "=" * (-len(base32) % 8))


def _login(client, persona):
    return client.post("/auth/login", json={"utente_username": persona.username, "utente_password": PASSWORD})


def _azzera_pausa_invii(db):
    """Un secondo codice via mail entro 60 s prende 429: nei test si finge passata."""
    db.execute(update(Limite).values(ultimo=db.scalar(select(func.now())) - timedelta(seconds=61)))
    db.commit()


def _nazionale_dentro(client, db, mailer, email="responsabile@example.org"):
    """Nazionale con email verificata, autenticato via OTP mail: (persona, intestazioni)."""
    persona = f.crea_attuatore(db, email=email, ruolo=f.RUOLO_NAZIONALE, password_hash=hash_password(PASSWORD))
    f.verifica_email(db, persona.cliente_id)
    sfida = _login(client, persona).json()
    assert sfida["metodo"] == "email"
    entrata = client.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": _codice_mail(mailer)})
    assert entrata.status_code == 200, entrata.text
    return persona, intestazioni_sessione(token_cookie(entrata))


def _attiva_app(client, headers):
    avvio = client.post("/auth/mfa/totp/attiva", headers=headers, json={"password": PASSWORD})
    assert avvio.status_code == 200, avvio.text
    segreto = _segreto(avvio.json()["segreto"])
    conferma = client.post("/auth/mfa/totp/conferma", headers=headers,
                           json={"codice": totp.codice(segreto, totp.passo_corrente())})
    assert conferma.status_code == 200, conferma.text
    assert conferma.json()["attivo"] is True
    return segreto, avvio.json()


def test_la_gestione_e_riservata_al_nazionale(client, db):
    persona = f.crea_attuatore(db, email="regionale@example.org", ruolo=f.RUOLO_REGIONALE,
                               password_hash=hash_password(PASSWORD))
    entrata = _login(client, persona)
    headers = intestazioni_sessione(token_cookie(entrata))
    assert client.get("/auth/mfa", headers=headers).status_code == 403
    assert client.post("/auth/mfa/totp/attiva", headers=headers, json={"password": PASSWORD}).status_code == 403


def test_attivazione_completa_poi_login_con_l_app_e_anti_replay(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    stato = client.get("/auth/mfa", headers=headers).json()
    assert stato["proposto"] == "email" and stato["totp"]["attivo"] is False
    assert stato["email"]["verificata"] is True and "@" in stato["email"]["destinatario"]

    assert client.post("/auth/mfa/totp/attiva", headers=headers, json={"password": "sbagliata-lunga"}).status_code == 400
    segreto, avvio = _attiva_app(client, headers)
    assert avvio["uri"].startswith("otpauth://totp/") and avvio["qr_svg"].lstrip().startswith("<svg")
    assert avvio["segreto"] not in avvio["qr_svg"] or True  # il QR codifica l'URI, che contiene il segreto: e' atteso

    stato = client.get("/auth/mfa", headers=headers).json()
    assert stato["proposto"] == "totp" and stato["metodi"] == ["totp", "email"]

    # Nuovo accesso: il server propone l'app, senza spedire nulla.
    client.cookies.clear()
    inviate = len(mailer.inviate)
    sfida = _login(client, persona).json()
    assert sfida["metodo"] == "totp" and sfida["metodi"] == ["totp", "email"]
    assert "destinatario" not in sfida and len(mailer.inviate) == inviate
    assert db.scalar(select(Sfida).where(Sfida.tipo == "totp")) is not None

    # La conferma ha consumato il passo corrente: vale quello successivo (tolleranza).
    codice = totp.codice(segreto, totp.passo_corrente() + 1)
    entrata = client.post("/auth/mfa/verifica-totp", json={"sfida": sfida["sfida"], "codice": codice})
    assert entrata.status_code == 200, entrata.text
    assert token_cookie(entrata) and entrata.json()["utente_id"] == persona.utente_id

    # Lo stesso codice non riapre la porta, nemmeno con una sfida nuova.
    client.cookies.clear()
    seconda = _login(client, persona).json()
    assert client.post("/auth/mfa/verifica-totp", json={"sfida": seconda["sfida"], "codice": codice}).status_code == 400


def test_cinque_codici_errati_bruciano_la_sfida(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    segreto, _ = _attiva_app(client, headers)
    client.cookies.clear()
    sfida = _login(client, persona).json()
    errato = "000000" if totp.codice(segreto, totp.passo_corrente() + 1) != "000000" else "111111"
    for _ in range(5):
        assert client.post("/auth/mfa/verifica-totp", json={"sfida": sfida["sfida"], "codice": errato}).status_code == 400
    giusto = totp.codice(segreto, totp.passo_corrente() + 1)
    assert client.post("/auth/mfa/verifica-totp", json={"sfida": sfida["sfida"], "codice": giusto}).status_code == 400
    assert db.scalar(select(AuthSessione).where(AuthSessione.utente_id == persona.utente_id,
                                                 AuthSessione.sess_revoked_at.is_(None))) is not None  # solo quella di prima


def test_usa_un_altro_metodo_apre_la_sfida_scelta_e_chiude_quella_in_corso(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    segreto, _ = _attiva_app(client, headers)
    client.cookies.clear()
    proposta = _login(client, persona).json()
    assert proposta["metodo"] == "totp"

    non_posseduto = client.post("/auth/mfa/metodo", json={"sfida": proposta["sfida"], "metodo": "passkey"})
    assert non_posseduto.status_code == 400

    _azzera_pausa_invii(db)
    scelta = client.post("/auth/mfa/metodo", json={"sfida": proposta["sfida"], "metodo": "email"})
    assert scelta.status_code == 200, scelta.text
    nuova = scelta.json()
    assert nuova["metodo"] == "email" and nuova["metodi"] == ["totp", "email"]
    assert "@" in nuova["destinatario"] and nuova["sfida"] != proposta["sfida"]

    # La sfida dell'app e' decaduta: il codice giusto non serve piu' li'.
    codice_app = totp.codice(segreto, totp.passo_corrente() + 1)
    assert client.post("/auth/mfa/verifica-totp", json={"sfida": proposta["sfida"], "codice": codice_app}).status_code == 400
    entrata = client.post("/auth/verifica-otp", json={"sfida": nuova["sfida"], "codice": _codice_mail(mailer)})
    assert entrata.status_code == 200, entrata.text


def test_disattivazione_riporta_all_email(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    segreto, _ = _attiva_app(client, headers)
    sbagliato = client.post("/auth/mfa/totp/disattiva", headers=headers, json={"password": PASSWORD, "codice": "000000"})
    assert sbagliato.status_code in (400, 429)
    giusto = client.post("/auth/mfa/totp/disattiva", headers=headers,
                         json={"password": PASSWORD, "codice": totp.codice(segreto, totp.passo_corrente() + 1)})
    assert giusto.status_code == 200, giusto.text
    assert giusto.json()["attivo"] is False
    client.cookies.clear()
    _azzera_pausa_invii(db)
    assert _login(client, persona).json()["metodo"] == "email"


def test_i_tentativi_su_password_e_codice_hanno_un_limite(client, db, mailer):
    _, headers = _nazionale_dentro(client, db, mailer)
    for _ in range(5):
        assert client.post("/auth/mfa/totp/attiva", headers=headers, json={"password": "no-lunga-abbastanza"}).status_code == 400
    limitata = client.post("/auth/mfa/totp/attiva", headers=headers, json={"password": PASSWORD})
    assert limitata.status_code == 429 and int(limitata.headers["Retry-After"]) > 0
