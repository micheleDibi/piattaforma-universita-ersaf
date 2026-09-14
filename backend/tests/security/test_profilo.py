"""Profilo personale: identità della sessione, proiezione minima e sola lettura."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import delete, update

from src.auth.models import AuthSessione
from src.aziende.models import Azienda
from src.clienti.models import Cliente
from src.security.password import hash_password
from tests.support import factories as f

pytestmark = pytest.mark.mariadb
PASSWORD = "password-profilo-test"


def accedi(client, attuatore):
    risposta = client.post("/auth/login", json={"utente_username": attuatore.username, "utente_password": PASSWORD})
    assert risposta.status_code == 200, risposta.text
    return risposta.json()


def crea_profilo(db, **kwargs):
    return f.crea_attuatore(db, email="profilo@example.org", password_hash=hash_password(PASSWORD), **kwargs)


def test_profilo_proprio_con_id_distinti_e_parametri_estranei_ignorati(client, db):
    f.crea_utente_orfano(db)
    utente = crea_profilo(db)
    altro = f.crea_attuatore(db, email="altra@example.org", nome="Lucia")
    assert utente.utente_id != utente.cliente_id
    accedi(client, utente)
    risposta = client.get(f"/profilo/me?utente_id={altro.utente_id}&cliente_id={altro.cliente_id}", headers={"x-utente-id": str(altro.utente_id)})
    assert risposta.status_code == 200
    dati = risposta.json()
    assert dati["username"] == utente.username
    assert dati["email"] == utente.email
    assert dati["nome"] == "Mario"
    assert risposta.headers["cache-control"] == "no-store"
    assert set(dati) == {"username", "ruolo", "nome", "cognome", "codice_fiscale", "cittadinanza", "email", "pec", "telefono", "cellulare", "azienda", "residenza", "domicilio"}
    assert client.get(f"/profilo/{altro.utente_id}").status_code == 404


def test_login_bootstrap_profilo_scelgono_la_stessa_anagrafica(client, db):
    utente = crea_profilo(db, ruolo=f.RUOLO_SOTTOSCRITTORE, nome="Scheda storica")
    principale = f.crea_cliente(db, utente_id=utente.utente_id, email="principale@example.org", nome="Elena", cognome="Bianchi", ruolo=f.RUOLO_REGIONALE)
    f.crea_cliente(db, utente_id=utente.utente_id, email="successiva@example.org", nome="Altra scheda", ruolo=f.RUOLO_ADERENTE)
    login = accedi(client, utente)
    bootstrap = client.get("/auth/session").json()
    profilo = client.get("/profilo/me").json()
    for dati in (login, bootstrap, profilo):
        assert (dati["nome"], dati["cognome"]) == ("Elena", "Bianchi")
    assert profilo["email"] == principale.cliente_email
    assert profilo["ruolo"] == login["ruolo_codice"] == bootstrap["ruolo_codice"] == "Regionale"


def test_dati_opzionali_e_indirizzi_indipendenti(client, db):
    utente = crea_profilo(db)
    cliente = db.get(Cliente, utente.cliente_id)
    cliente.cliente_nome = cliente.cliente_cognome = ""
    cliente.cliente_indirizzo = "Via delle Rose"
    cliente.cliente_civico = "12/A"
    cliente.cliente_CAP = "00100"
    cliente.cliente_indirizzoDomicilio = "Viale degli Olmi"
    cliente.cliente_civicoDomicilio = "7"
    cliente.cliente_CAPDomicilio = "20100"
    db.commit()
    accedi(client, utente)
    dati = client.get("/profilo/me").json()
    assert dati["nome"] == dati["cognome"] == ""
    assert dati["azienda"] is None and dati["pec"] is None
    assert dati["residenza"]["cap"] == "00100"
    assert dati["domicilio"]["cap"] == "20100"
    assert dati["residenza"]["civico"] == "12/A"
    assert dati["domicilio"]["indirizzo"] == "Viale degli Olmi"


def test_azienda_espone_solo_la_ragione_sociale(client, db):
    utente = crea_profilo(db)
    azienda = Azienda(azienda_ragione_sociale="Centro Formazione delle Rose", azienda_partitaIVA="00000000000", azienda_via="Via delle Rose", azienda_citta="Roma", azienda_CAP="00100", azienda_provincia="RM", azienda_iban="non-pubblicare")
    db.add(azienda)
    db.flush()
    db.get(Cliente, utente.cliente_id).azienda_id = azienda.azienda_id
    db.commit()
    accedi(client, utente)
    risposta = client.get("/profilo/me")
    assert risposta.json()["azienda"] == azienda.azienda_ragione_sociale
    assert "non-pubblicare" not in risposta.text


@pytest.mark.parametrize("metodo", ["POST", "PUT", "PATCH", "DELETE"])
def test_il_profilo_non_accetta_modifiche_neanche_con_csrf(client, db, metodo):
    utente = crea_profilo(db)
    login = accedi(client, utente)
    risposta = client.request(metodo, "/profilo/me", json={"nome": "Sostituito", "residenza": {"citta": "Milano"}}, headers={"X-CSRF-Token": login["csrf_token"]})
    assert risposta.status_code == 405
    db.expire_all()
    assert db.get(Cliente, utente.cliente_id).cliente_nome == "Mario"


@pytest.mark.parametrize("stato", ["assente", "scaduta", "revocata"])
def test_sessione_non_valida_non_espone_dati(client, db, stato):
    utente = crea_profilo(db)
    if stato != "assente":
        login = accedi(client, utente)
        if stato == "scaduta":
            db.execute(update(AuthSessione).values(sess_expires_at=datetime.now() - timedelta(days=2)))
            db.commit()
        else:
            client.post("/auth/logout", headers={"X-CSRF-Token": login["csrf_token"]})
    risposta = client.get("/profilo/me")
    assert risposta.status_code == 401
    assert utente.email not in risposta.text


def test_anagrafica_rimossa_dopo_login_restituisce_errore_gestito(client, db):
    utente = crea_profilo(db)
    accedi(client, utente)
    db.execute(delete(Cliente).where(Cliente.cliente_id == utente.cliente_id))
    db.commit()
    risposta = client.get("/profilo/me")
    assert risposta.status_code == 404
    assert risposta.headers["cache-control"] == "no-store"
    assert "anagrafica" in risposta.json()["detail"]


def test_impersonificazione_sostituisce_nome_e_profilo(client, db):
    amministratore = crea_profilo(db, ruolo=f.RUOLO_REGIONALE)
    bersaglio = f.crea_attuatore(db, email="elena@example.org", nome="Elena")
    login = accedi(client, amministratore)
    risposta = client.post(f"/auth/login-as/{bersaglio.utente_id}", headers={"X-CSRF-Token": login["csrf_token"]})
    assert risposta.status_code == 200
    assert risposta.json()["nome"] == "Elena"
    assert client.get("/profilo/me").json()["email"] == bersaglio.email
