"""Fondamenta del secondo fattore (ADR 0009): priorita', email verificata,
verifica dell'email al primo accesso, altri ruoli invariati."""

from __future__ import annotations

import re

import pytest
from sqlalchemy import select

from src.auth.models import AuthSessione
from src.clienti.models import Cliente
from src.notifiche.formato_email import come_testo
from src.otp.identita import versione
from src.otp.models import ContattoVerificato, Sfida
from src.security.password import hash_password
from src.utenti.models import Utente
from tests.conftest import corpo_html
from tests.integration.test_clienti import _operatore
from tests.support import factories as f
from tests.support.sessioni import token_cookie

pytestmark = pytest.mark.mariadb
PASSWORD = "password-di-collaudo-lunga"


def _nazionale(db, email="direzione@example.org"):
    return f.crea_attuatore(db, email=email, ruolo=f.RUOLO_NAZIONALE, password_hash=hash_password(PASSWORD))


def _login(client, persona):
    return client.post("/auth/login", json={"utente_username": persona.username, "utente_password": PASSWORD})


def _codice(mailer):
    return re.search(r"\b\d{6}\b", come_testo(corpo_html(mailer.inviate[-1]))).group()


def test_senza_email_verificata_il_primo_accesso_verifica_ed_entra(client, db, mailer):
    persona = _nazionale(db)
    primo = _login(client, persona)
    assert primo.status_code == 200, primo.text
    corpo = primo.json()
    assert corpo["requires_2fa"] is True
    assert corpo["metodo"] == "email_accesso" and corpo["metodi"] == []
    assert "utente_id" not in corpo
    assert db.scalar(select(Sfida)).tipo == "email_accesso"
    assert db.scalar(select(AuthSessione)) is None

    conferma = client.post("/auth/verifica-otp", json={"sfida": corpo["sfida"], "codice": _codice(mailer)})
    assert conferma.status_code == 200, conferma.text
    assert token_cookie(conferma)

    db.expire_all()
    riga = db.get(ContattoVerificato, (persona.cliente_id, "email"))
    assert riga is not None, "la conferma deve certificare l'email"
    assert riga.versione == versione(db.get(Cliente, persona.cliente_id), "email")

    # Dal secondo accesso il metodo e' l'OTP di login, come per chi era gia' verificato.
    client.cookies.clear()
    secondo = _login(client, persona).json()
    assert secondo["metodo"] == "email" and secondo["metodi"] == ["email"]
    assert db.scalar(select(Sfida).where(Sfida.tipo == "login")) is not None


def test_con_email_verificata_il_login_manda_l_otp_di_login(client, db, mailer):
    persona = _nazionale(db)
    f.verifica_email(db, persona.cliente_id)
    corpo = _login(client, persona).json()
    assert corpo["metodo"] == "email" and corpo["metodi"] == ["email"]
    assert db.scalar(select(Sfida)).tipo == "login"
    assert client.post("/auth/verifica-otp", json={"sfida": corpo["sfida"], "codice": _codice(mailer)}).status_code == 200


def test_la_verifica_avviata_da_un_operatore_non_apre_una_sessione(client, db, mailer):
    """Una sfida `email` della scheda cliente certifica il contatto, non autentica."""
    persona = _nazionale(db)
    _, headers = _operatore(client, db)
    avvio = client.post(f"/clienti/{persona.cliente_id}/contatti/email/genera-otp",
                        headers=headers, json={"valore": persona.email})
    assert avvio.status_code == 200, avvio.text
    codice = _codice(mailer)
    client.cookies.clear()
    respinta = client.post("/auth/verifica-otp", json={"sfida": avvio.json()["sfida"], "codice": codice})
    assert respinta.status_code == 400
    assert db.scalar(select(AuthSessione).where(AuthSessione.utente_id == persona.utente_id)) is None


def test_il_reinvio_conserva_il_tipo_della_sfida(client, db, mailer):
    persona = _nazionale(db)
    corpo = _login(client, persona).json()
    # La pausa di 60 secondi e' gia' provata in test_otp: qui conta solo il tipo.
    from datetime import timedelta
    from sqlalchemy import func, update
    from src.otp.models import Limite
    db.execute(update(Limite).values(ultimo=db.scalar(select(func.now())) - timedelta(seconds=61)))
    db.commit()
    reinvio = client.post("/auth/rigenera-otp", json={"sfida": corpo["sfida"]})
    assert reinvio.status_code == 200, reinvio.text
    assert reinvio.json()["metodo"] == "email_accesso" and reinvio.json()["metodi"] == []
    assert reinvio.json()["sfida"] != corpo["sfida"]
    tipi = db.scalars(select(Sfida.tipo)).all()
    assert tipi == ["email_accesso", "email_accesso"]


@pytest.mark.parametrize("mutazione", ["email", "password"])
def test_la_verifica_di_accesso_decade_se_cambiano_email_o_password(client, db, mailer, mutazione):
    persona = _nazionale(db)
    corpo = _login(client, persona).json()
    codice = _codice(mailer)
    if mutazione == "email":
        db.get(Cliente, persona.cliente_id).cliente_email = "altra@example.org"
    else:
        db.get(Utente, persona.utente_id).utente_password_hash = hash_password("altra-password-lunga")
    db.commit()
    assert client.post("/auth/verifica-otp", json={"sfida": corpo["sfida"], "codice": codice}).status_code == 400
    assert db.get(ContattoVerificato, (persona.cliente_id, "email")) is None
    assert db.scalar(select(AuthSessione)) is None


def test_nazionale_senza_email_in_anagrafica_riceve_un_messaggio_chiaro(client, db):
    persona = _nazionale(db, email="")
    risposta = _login(client, persona)
    assert risposta.status_code == 409, risposta.text
    assert "anagrafica" in risposta.json()["detail"]
    assert db.scalar(select(Sfida)) is None
    assert db.scalar(select(AuthSessione)) is None


def test_gli_altri_ruoli_entrano_senza_secondo_fattore(client, db):
    persona = f.crea_attuatore(db, email="regionale@example.org", ruolo=f.RUOLO_REGIONALE,
                               password_hash=hash_password(PASSWORD))
    risposta = _login(client, persona)
    assert risposta.status_code == 200, risposta.text
    assert "requires_2fa" not in risposta.json()
    assert token_cookie(risposta)
