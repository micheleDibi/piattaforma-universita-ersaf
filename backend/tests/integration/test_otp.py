"""Verifiche complete con recapiti sintetici e provider in memoria."""
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import pytest
from sqlalchemy import select, update, func
from src.otp.models import Sfida, Limite, Attivazione
from src.clienti.models import Cliente
from src.utenti.models import Utente
from src.auth.models import AuthSessione
from src.security.password import hash_password
from tests.support import factories as f
from tests.support.sessioni import token_cookie, intestazioni_sessione
from tests.conftest import corpo_html
from tests.integration.test_clienti import _anagrafica, _operatore

pytestmark = pytest.mark.mariadb
PASSWORD = "password-di-collaudo-lunga"


def nazionale(client, db, mailer):
    persona = f.crea_attuatore(db, email="nazionale@example.org", ruolo=5, password_hash=hash_password(PASSWORD))
    risposta = client.post("/auth/login", json={"utente_username": persona.username, "utente_password": PASSWORD})
    assert risposta.status_code == 200, risposta.text
    codice = re.search(r"\b\d{6}\b", corpo_html(mailer.inviate[-1])).group()
    return persona, risposta.json(), codice


def nuovo(client, db):
    _, headers = _operatore(client, db)
    risposta = client.post("/clienti/con-utente", headers=headers,
        json=_anagrafica(cliente_cellulare="+390000000000"))
    assert risposta.status_code == 201, risposta.text
    return risposta.json(), headers


def invia(client, identita, headers, tipo):
    valore = "mario.rossi@example.org" if tipo == "email" else "+390000000000"
    risposta = client.post(f"/clienti/{identita['cliente_id']}/contatti/{tipo}/genera-otp",
                           headers=headers, json={"valore": valore})
    assert risposta.status_code == 200, risposta.text
    return risposta.json()["sfida"]


def conferma(client, identita, headers, tipo, richiesta):
    return client.post(f"/clienti/{identita['cliente_id']}/contatti/{tipo}/verifica-otp",
                       headers=headers, json=richiesta)


def test_nazionale_cookie_solo_dopo_otp_e_consumo_unico(client, db, mailer):
    persona, sfida, codice = nazionale(client, db, mailer)
    assert db.scalar(select(AuthSessione)) is None
    riga = db.scalar(select(Sfida))
    assert riga.codice != codice and riga.impronta != sfida["sfida"]
    risposta = client.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": codice})
    assert risposta.status_code == 200, risposta.text
    assert token_cookie(risposta)
    assert risposta.json()["utente_id"] == persona.utente_id
    assert "token" not in risposta.json()
    assert client.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": codice}).status_code == 400
    assert client.post("/auth/rigenera-otp", json={"sfida": sfida["sfida"]}).status_code == 400


def test_login_otp_limite_cinque_errori_e_reinvio(client, db, mailer):
    _, sfida, codice = nazionale(client, db, mailer)
    reinvio = client.post("/auth/rigenera-otp", json={"sfida": sfida["sfida"]})
    assert reinvio.status_code == 429 and int(reinvio.headers["Retry-After"]) > 0
    errato = "000000" if codice != "000000" else "111111"
    for _ in range(5):
        assert client.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": errato}).status_code == 400
    assert client.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": codice}).status_code == 400
    db.execute(update(Limite).values(ultimo=db.scalar(select(func.now()))-timedelta(seconds=61)))
    db.commit()
    nuovo_codice = client.post("/auth/rigenera-otp", json={"sfida": sfida["sfida"]})
    assert nuovo_codice.status_code == 200
    assert nuovo_codice.json()["sfida"] != sfida["sfida"]
    assert client.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": codice}).status_code == 400


@pytest.mark.parametrize("mutazione", ["email", "password", "disattivo", "scaduto", "ruolo"])
def test_login_sfida_invalidata_da_cambio_identita(client, db, mailer, mutazione):
    persona, sfida, codice = nazionale(client, db, mailer)
    utente = db.get(Utente, persona.utente_id)
    cliente = db.get(Cliente, persona.cliente_id)
    if mutazione == "email": cliente.cliente_email = "nuova@example.org"
    if mutazione == "password": utente.utente_password_hash = hash_password("altra-password-lunga")
    if mutazione == "disattivo": utente.utente_attivoSN = 0
    if mutazione == "ruolo": cliente.cliente_ruolo = 2
    if mutazione == "scaduto": db.scalar(select(Sfida)).scadenza -= timedelta(hours=1)
    db.commit()
    assert client.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": codice}).status_code == 400
    assert db.scalar(select(AuthSessione)) is None


@pytest.mark.parametrize("primo", ["email", "cellulare"])
def test_attivazione_dopo_entrambi_con_invio_credenziali(client, db, mailer, sms, primo):
    identita, headers = nuovo(client, db)
    for indice, tipo in enumerate([primo, "cellulare" if primo == "email" else "email"]):
        token = invia(client, identita, headers, tipo)
        testo = corpo_html(mailer.inviate[-1]) if tipo == "email" else sms.inviati[-1][1]
        codice = re.search(r"\b\d{6}\b", testo).group()
        risposta = conferma(client, identita, headers, tipo, {"sfida": token, "codice": codice})
        assert risposta.status_code == 200, risposta.text
        assert risposta.json()[tipo]["verificato"]
        db.expire_all()
        assert db.get(Utente, identita["utente_id"]).utente_attivoSN == (-1 if indice else 0)
    assert risposta.json()["credenziali_inviate"] is True
    assert db.get(Attivazione, identita["utente_id"]) is None
    assert "localhost" not in corpo_html(mailer.inviate[-1])
    assert "test.example.org" in corpo_html(mailer.inviate[-1])
    assert "password_generata" not in risposta.json()


def test_contact_scope_modifiche_csrf_e_provider_failure(client, db, mailer, sms):
    identita, headers = nuovo(client, db)
    base = f"/clienti/{identita['cliente_id']}/contatti/cellulare/genera-otp"
    assert client.post(base, json={"valore": "+390000000000"}).status_code == 403
    assert client.post(base, headers=headers, json={"valore": "+390000000001"}).status_code == 409
    sms.errore = True
    risposta = client.post(base, headers=headers, json={"valore": "+390000000000"})
    assert risposta.status_code == 503 and risposta.headers["Retry-After"] == "60"
    assert db.scalar(select(Sfida)).stato == "fallito"
    token = invia(client, identita, headers, "email")
    codice = re.search(r"\b\d{6}\b", corpo_html(mailer.inviate[-1])).group()
    assert conferma(client, identita, headers, "cellulare", {"sfida": token, "codice": codice}).status_code == 400
    assert client.put(f"/clienti/{identita['cliente_id']}", headers=headers,
                      json={"cliente_email": "nuova@example.org"}).status_code == 200
    assert conferma(client, identita, headers, "email", {"sfida": token, "codice": codice}).status_code == 400


def test_concorrenza_login_un_solo_successo(client, client_da, db, mailer):
    _, sfida, codice = nazionale(client, db, mailer)
    altri = [client_da("203.0.113.10"), client_da("203.0.113.11")]
    def verifica_http(istanza):
        return istanza.post("/auth/verifica-otp", json={"sfida": sfida["sfida"], "codice": codice}).status_code
    with ThreadPoolExecutor(2) as pool:
        assert sorted(pool.map(verifica_http, altri)) == [200, 400]


def test_disattivazione_manual_non_viene_annullata(client, db, mailer, sms):
    identita, headers = nuovo(client, db)
    assert client.put(f"/utenti/{identita['utente_id']}", headers=headers, json={"utente_attivoSN": 0}).status_code == 200
    for tipo in ("email", "cellulare"):
        token = invia(client, identita, headers, tipo)
        testo = corpo_html(mailer.inviate[-1]) if tipo == "email" else sms.inviati[-1][1]
        codice = re.search(r"\b\d{6}\b", testo).group()
        assert conferma(client, identita, headers, tipo, {"sfida": token, "codice": codice}).status_code == 200
    db.expire_all()
    assert db.get(Utente, identita["utente_id"]).utente_attivoSN == 0


def test_email_credenziali_fallita_non_dichiara_consegna(client, db, mailer, sms):
    identita, headers = nuovo(client, db)
    token = invia(client, identita, headers, "email")
    codice = re.search(r"\b\d{6}\b", corpo_html(mailer.inviate[-1])).group()
    assert conferma(client, identita, headers, "email", {"sfida": token, "codice": codice}).status_code == 200
    token = invia(client, identita, headers, "cellulare")
    codice = re.search(r"\b\d{6}\b", sms.inviati[-1][1]).group()
    mailer.errore = RuntimeError("Errore SMTP simulato")
    risposta = conferma(client, identita, headers, "cellulare", {"sfida": token, "codice": codice})
    assert risposta.status_code == 200
    assert risposta.json()["credenziali_inviate"] is False
    db.expire_all()
    assert db.get(Utente, identita["utente_id"]).utente_attivoSN == -1
    assert conferma(client, identita, headers, "cellulare", {"sfida": token, "codice": codice}).status_code == 400
