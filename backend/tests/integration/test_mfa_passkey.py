"""Passkey del Nazionale: registrazione dal profilo, login con la passkey,
risposte estranee, contatore, rimozione."""

from __future__ import annotations

import re
from datetime import timedelta

import pytest
from sqlalchemy import func, select, update

from src.mfa.models import AuthPasskey
from src.notifiche.formato_email import come_testo
from src.otp.models import Limite
from src.security.password import hash_password
from tests.conftest import corpo_html
from tests.support import factories as f
from tests.support.autenticatore_virtuale import AutenticatoreVirtuale, b64url
from tests.support.sessioni import intestazioni_sessione, token_cookie

pytestmark = pytest.mark.mariadb
PASSWORD = "password-di-collaudo-lunga"
ORIGINE = "https://test.example.org"


def _codice_mail(mailer):
    return re.search(r"\b\d{6}\b", come_testo(corpo_html(mailer.inviate[-1]))).group()


def _login(client, persona):
    return client.post("/auth/login", json={"utente_username": persona.username, "utente_password": PASSWORD})


def _nazionale_dentro(client, db, mailer, email="segreteria@example.org"):
    persona = f.crea_attuatore(db, email=email, ruolo=f.RUOLO_NAZIONALE, password_hash=hash_password(PASSWORD))
    f.verifica_email(db, persona.cliente_id)
    sfida = _login(client, persona).json()
    entrata = client.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": _codice_mail(mailer)})
    assert entrata.status_code == 200, entrata.text
    return persona, intestazioni_sessione(token_cookie(entrata))


def _registra(client, headers, telefono: AutenticatoreVirtuale, nome="iPhone di prova"):
    avvio = client.post("/auth/mfa/passkey/opzioni", headers=headers, json={"password": PASSWORD})
    assert avvio.status_code == 200, avvio.text
    opzioni = avvio.json()["opzioni"]
    conferma = client.post("/auth/mfa/passkey/conferma", headers=headers, json={
        "sfida": avvio.json()["sfida"], "credenziale": telefono.registra(opzioni, ORIGINE), "nome": nome,
    })
    assert conferma.status_code == 200, conferma.text
    return opzioni, conferma.json()


def test_registrazione_dal_profilo_e_login_con_la_passkey(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    telefono = AutenticatoreVirtuale()

    assert client.post("/auth/mfa/passkey/opzioni", headers=headers, json={"password": "sbagliata-lunga"}).status_code == 400
    opzioni, stato = _registra(client, headers, telefono)
    assert opzioni["rp"]["id"] == "test.example.org"
    assert opzioni["authenticatorSelection"]["authenticatorAttachment"] == "cross-platform"
    assert opzioni["authenticatorSelection"]["userVerification"] == "required"
    assert opzioni["user"]["name"] == persona.username
    assert [p["nome"] for p in stato["passkey"]] == ["iPhone di prova"]
    assert stato["passkey"][0]["sincronizzata"] is True
    assert stato["proposto"] == "passkey" and stato["metodi"] == ["passkey", "email"]

    # Nuovo accesso: il server propone la passkey e consegna le opzioni al browser.
    client.cookies.clear()
    sfida = _login(client, persona).json()
    assert sfida["metodo"] == "passkey" and sfida["metodi"] == ["passkey", "email"]
    assert [c["id"] for c in sfida["opzioni"]["allowCredentials"]] == [b64url(telefono.credential_id)]
    assert sfida["opzioni"]["rpId"] == "test.example.org"

    entrata = client.post("/auth/mfa/verifica-passkey", json={
        "sfida": sfida["sfida"], "credenziale": telefono.autentica(sfida["opzioni"], ORIGINE),
    })
    assert entrata.status_code == 200, entrata.text
    assert token_cookie(entrata) and entrata.json()["utente_id"] == persona.utente_id
    riga = db.scalar(select(AuthPasskey).where(AuthPasskey.utente_id == persona.utente_id))
    db.refresh(riga)
    assert riga.pk_sign_count == 1 and riga.pk_ultimo_uso is not None


def test_risposte_estranee_respinte(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    telefono, estraneo = AutenticatoreVirtuale(), AutenticatoreVirtuale()
    _registra(client, headers, telefono)
    client.cookies.clear()
    sfida = _login(client, persona).json()

    # Un autenticatore mai registrato.
    assert client.post("/auth/mfa/verifica-passkey", json={
        "sfida": sfida["sfida"], "credenziale": estraneo.autentica(sfida["opzioni"], ORIGINE)}).status_code == 400
    # La passkey giusta ma da un'origine diversa (sito clone).
    assert client.post("/auth/mfa/verifica-passkey", json={
        "sfida": sfida["sfida"], "credenziale": telefono.autentica(sfida["opzioni"], "https://clone.example")}).status_code == 400
    # Una risposta valida, ma la sfida viene consumata: la stessa non si riusa.
    risposta = telefono.autentica(sfida["opzioni"], ORIGINE)
    assert client.post("/auth/mfa/verifica-passkey", json={"sfida": sfida["sfida"], "credenziale": risposta}).status_code == 200
    assert client.post("/auth/mfa/verifica-passkey", json={"sfida": sfida["sfida"], "credenziale": risposta}).status_code == 400


def test_un_contatore_che_torna_indietro_e_un_clone(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    telefono = AutenticatoreVirtuale()
    _registra(client, headers, telefono)
    client.cookies.clear()
    prima = _login(client, persona).json()
    assert client.post("/auth/mfa/verifica-passkey", json={
        "sfida": prima["sfida"], "credenziale": telefono.autentica(prima["opzioni"], ORIGINE, contatore=5)}).status_code == 200
    client.cookies.clear()
    seconda = _login(client, persona).json()
    assert client.post("/auth/mfa/verifica-passkey", json={
        "sfida": seconda["sfida"], "credenziale": telefono.autentica(seconda["opzioni"], ORIGINE, contatore=3)}).status_code == 400


def test_la_sfida_di_registrazione_non_apre_sessioni(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    telefono = AutenticatoreVirtuale()
    avvio = client.post("/auth/mfa/passkey/opzioni", headers=headers, json={"password": PASSWORD}).json()
    client.cookies.clear()
    respinta = client.post("/auth/mfa/verifica-passkey", json={
        "sfida": avvio["sfida"], "credenziale": telefono.registra(avvio["opzioni"], ORIGINE)})
    assert respinta.status_code == 400


def test_le_opzioni_escludono_le_passkey_gia_registrate(client, db, mailer):
    _, headers = _nazionale_dentro(client, db, mailer)
    telefono = AutenticatoreVirtuale()
    _registra(client, headers, telefono)
    seconde = client.post("/auth/mfa/passkey/opzioni", headers=headers, json={"password": PASSWORD}).json()["opzioni"]
    assert [c["id"] for c in seconde["excludeCredentials"]] == [b64url(telefono.credential_id)]


def test_rimozione_riporta_al_metodo_successivo(client, db, mailer):
    persona, headers = _nazionale_dentro(client, db, mailer)
    telefono = AutenticatoreVirtuale()
    _, stato = _registra(client, headers, telefono)
    identificativo = stato["passkey"][0]["id"]
    assert client.post("/auth/mfa/passkey/rimuovi", headers=headers,
                       json={"password": "sbagliata-lunga", "id": identificativo}).status_code == 400
    rimossa = client.post("/auth/mfa/passkey/rimuovi", headers=headers, json={"password": PASSWORD, "id": identificativo})
    assert rimossa.status_code == 200, rimossa.text
    assert rimossa.json()["passkey"] == [] and rimossa.json()["proposto"] == "email"
    assert client.post("/auth/mfa/passkey/rimuovi", headers=headers, json={"password": PASSWORD, "id": identificativo}).status_code == 404
    client.cookies.clear()
    # Un secondo codice via mail entro 60 s prenderebbe 429: si finge passata la pausa.
    db.execute(update(Limite).values(ultimo=db.scalar(select(func.now())) - timedelta(seconds=61)))
    db.commit()
    assert _login(client, persona).json()["metodo"] == "email"
