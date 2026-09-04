"""Il login: i due fix obbligatori, il rehash pigro e la sessione."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from src.auth.models import AuthSessione
from src.security.password import hash_password, verify_password
from src.utenti.models import Utente
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

PASSWORD = "cavallo-batteria-graffetta"


def _login(client, username, password):
    return client.post(
        "/auth/login",
        json={"utente_username": username, "utente_password": password},
    )


def test_login_riuscito_restituisce_token_e_utente_id(client, db):
    attuatore = f.crea_attuatore(
        db, email="attuatore@example.org", password_hash=hash_password(PASSWORD)
    )
    risposta = _login(client, attuatore.username, PASSWORD)

    assert risposta.status_code == 200
    corpo = risposta.json()
    assert corpo["token_type"] == "bearer"
    assert len(corpo["token"]) == 43
    # utente_id resta nella risposta: il frontend lo mette nel corpo di
    # POST /clienti/, e toglierlo romperebbe la creazione dei sottoscrittori.
    assert corpo["utente_id"] == attuatore.utente_id
    assert corpo["ruolo_codice"] == "Aderente"

    # Nel database c'e' solo l'impronta, mai il token.
    sessione = db.execute(select(AuthSessione)).scalar_one()
    assert sessione.sess_token_hash != corpo["token"]
    assert len(sessione.sess_token_hash) == 64


def test_password_errata(client, db):
    attuatore = f.crea_attuatore(
        db, email="a@example.org", password_hash=hash_password(PASSWORD)
    )
    risposta = _login(client, attuatore.username, "password-sbagliata-lunga")
    assert risposta.status_code == 401
    assert db.execute(select(AuthSessione)).first() is None


def test_utente_orfano_riceve_401_e_non_500(client, db):
    """Fix 1: gli 869 utenti senza riga `clienti` producevano un 500, e il 500
    distingueva "password sbagliata" da "utente esistente ma orfano"."""
    utente = f.crea_utente_orfano(db, password_hash=hash_password(PASSWORD))
    risposta = _login(client, utente.utente_username, PASSWORD)
    assert risposta.status_code == 401


def test_utente_disattivato_riceve_401(client, db):
    """Fix 2: utente_attivoSN non veniva controllato e i 21 utenti disattivati
    accedevano regolarmente."""
    attuatore = f.crea_attuatore(
        db,
        email="spento@example.org",
        attivo=f.DISATTIVO,
        password_hash=hash_password(PASSWORD),
    )
    risposta = _login(client, attuatore.username, PASSWORD)
    assert risposta.status_code == 401


def test_username_duplicato_non_autentica(client, db):
    """Il database non ha la UNIQUE su utente_username e contiene sei gruppi di
    duplicati: un'identita' ambigua non deve mai autenticare."""
    f.crea_attuatore(
        db,
        username="omonimo",
        email="uno@example.org",
        password_hash=hash_password(PASSWORD),
    )
    f.crea_attuatore(
        db,
        username="omonimo",
        email="due@example.org",
        password_hash=hash_password(PASSWORD),
    )
    assert _login(client, "omonimo", PASSWORD).status_code == 401


def test_i_quattro_rifiuti_sono_indistinguibili(client, db):
    """Password errata, utente inesistente, disattivato e orfano devono
    produrre la stessa identica risposta."""
    valido = f.crea_attuatore(
        db, email="ok@example.org", password_hash=hash_password(PASSWORD)
    )
    spento = f.crea_attuatore(
        db,
        email="spento@example.org",
        attivo=f.DISATTIVO,
        password_hash=hash_password(PASSWORD),
    )
    orfano = f.crea_utente_orfano(db, password_hash=hash_password(PASSWORD))

    risposte = [
        _login(client, valido.username, "password-sbagliata-lunga"),
        _login(client, "utente-che-non-esiste", PASSWORD),
        _login(client, spento.username, PASSWORD),
        _login(client, orfano.utente_username, PASSWORD),
    ]
    assert {r.status_code for r in risposte} == {401}
    assert len({r.content for r in risposte}) == 1


def test_ruolo_nazionale_richiede_2fa_e_non_emette_sessione(client, db):
    """Il 2FA vero e' fuori perimetro: il ramo non deve restituire ne' token ne'
    utente_id, cosi' il frontend si ferma invece di scrivere "undefined"."""
    attuatore = f.crea_attuatore(
        db,
        email="nazionale@example.org",
        ruolo=f.RUOLO_NAZIONALE,
        password_hash=hash_password(PASSWORD),
    )
    risposta = _login(client, attuatore.username, PASSWORD)

    assert risposta.status_code == 200
    corpo = risposta.json()
    assert corpo["requires_2fa"] is True
    assert "token" not in corpo
    assert "utente_id" not in corpo
    assert db.execute(select(AuthSessione)).first() is None


# --- rehash pigro -----------------------------------------------------------


def test_rehash_pigro_converte_una_riga_al_login(client, db):
    """La password legacy in chiaro diventa un hash bcrypt al primo accesso
    riuscito, e il chiaro viene svuotato."""
    attuatore = f.crea_attuatore(
        db, email="legacy@example.org", password_chiaro=PASSWORD
    )
    prima = db.get(Utente, attuatore.utente_id)
    assert prima.utente_password == PASSWORD
    assert prima.utente_password_hash is None
    assert prima.utente_password_algo == "legacy_plaintext"

    assert _login(client, attuatore.username, PASSWORD).status_code == 200

    db.expire_all()
    dopo = db.get(Utente, attuatore.utente_id)
    assert dopo.utente_password_hash.startswith("$2b$")
    assert verify_password(PASSWORD, dopo.utente_password_hash)
    # NOT NULL nel database: stringa vuota, non NULL.
    assert dopo.utente_password == ""
    assert dopo.utente_password_algo == "bcrypt"


def test_rehash_non_valorizza_changed_at(client, db):
    """Il punto piu' insidioso: utente_password_changed_at e' il cut-off della
    query [B] della migrazione 004. Valorizzarlo al login invaliderebbe la
    sessione appena creata e tutte quelle sugli altri dispositivi."""
    attuatore = f.crea_attuatore(
        db, email="legacy2@example.org", password_chiaro=PASSWORD
    )
    risposta = _login(client, attuatore.username, PASSWORD)
    assert risposta.status_code == 200

    db.expire_all()
    utente = db.get(Utente, attuatore.utente_id)
    assert utente.utente_password_changed_at is None
    assert utente.utente_password_changed_via is None

    # E la sessione emessa deve essere utilizzabile subito.
    token = risposta.json()["token"]
    assert (
        client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"}).status_code
        == 204
    )


def test_secondo_login_passa_dal_ramo_bcrypt(client, db, monkeypatch):
    attuatore = f.crea_attuatore(
        db, email="legacy3@example.org", password_chiaro=PASSWORD
    )
    assert _login(client, attuatore.username, PASSWORD).status_code == 200

    import src.auth.servizio_login as servizio

    chiamate = []
    originale = servizio.secrets.compare_digest

    def spia(a, b):
        chiamate.append(True)
        return originale(a, b)

    monkeypatch.setattr(servizio.secrets, "compare_digest", spia)
    assert _login(client, attuatore.username, PASSWORD).status_code == 200
    assert chiamate == [], "il secondo login non deve toccare il ramo legacy"


def test_password_legacy_errata_non_converte(client, db):
    """Un bug qui migrerebbe l'utente sull'hash della password sbagliata,
    chiudendolo fuori per sempre."""
    attuatore = f.crea_attuatore(
        db, email="legacy4@example.org", password_chiaro=PASSWORD
    )
    assert _login(client, attuatore.username, "un-altra-password").status_code == 401

    db.expire_all()
    utente = db.get(Utente, attuatore.utente_id)
    assert utente.utente_password == PASSWORD
    assert utente.utente_password_hash is None


def test_rehash_non_tocca_le_altre_righe(client, db):
    """Traduzione in test del divieto: nessuna operazione massiva, mai."""
    chi_accede = f.crea_attuatore(
        db, email="accede@example.org", password_chiaro=PASSWORD
    )
    fermo = f.crea_attuatore(db, email="fermo@example.org", password_chiaro="AltraPass123")

    prima = db.get(Utente, fermo.utente_id)
    istantanea = {c.name: getattr(prima, c.name) for c in Utente.__table__.c}

    assert _login(client, chi_accede.username, PASSWORD).status_code == 200

    db.expire_all()
    dopo = db.get(Utente, fermo.utente_id)
    assert {c.name: getattr(dopo, c.name) for c in Utente.__table__.c} == istantanea
