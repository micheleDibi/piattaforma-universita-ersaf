"""`POST /auth/login-as/{utente_id}`: autenticazione e autorizzazione.

Era un bypass completo. Nessuna dipendenza di autenticazione, nessuna password:
si passava un id e si riceveva un token di sessione valido.

    curl -X POST http://host/auth/login-as/1

era l'exploit intero, e apriva l'accesso ai 168 attuatori. Annullava il lavoro
su hashing, sessioni revocabili e recupero password, perche' per entrare non
serviva piu' conoscere una password.
"""

from __future__ import annotations

import pytest

from src.security.password import hash_password
from src.security.sessioni import valida_sessione
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

PASSWORD = "cavallo-batteria-graffetta"
_email = iter(f"p{n}@example.org" for n in range(1, 999))


def _sessione(client, db, ruolo):
    attuatore = f.crea_attuatore(
        db, email=next(_email), ruolo=ruolo, password_hash=hash_password(PASSWORD)
    )
    risposta = client.post(
        "/auth/login",
        json={"utente_username": attuatore.username, "utente_password": PASSWORD},
    )
    assert risposta.status_code == 200, risposta.text
    return attuatore, {"Authorization": f"Bearer {risposta.json()['token']}"}


def test_senza_token_non_si_impersona_nessuno(client, db):
    """L'exploit originale, in una riga."""
    bersaglio = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_ADERENTE)

    risposta = client.post(f"/auth/login-as/{bersaglio.utente_id}")

    assert risposta.status_code == 401
    assert "token" not in risposta.json()


def test_un_ruolo_non_amministrativo_non_puo_impersonare(client, db):
    _, intestazione = _sessione(client, db, f.RUOLO_ADERENTE)
    bersaglio = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_PROVINCIALE)

    risposta = client.post(
        f"/auth/login-as/{bersaglio.utente_id}", headers=intestazione
    )

    assert risposta.status_code == 403


def test_un_regionale_puo_impersonare_e_riceve_una_sessione_valida(client, db):
    _, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)
    bersaglio = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_ADERENTE)

    risposta = client.post(
        f"/auth/login-as/{bersaglio.utente_id}", headers=intestazione
    )

    assert risposta.status_code == 200, risposta.text
    corpo = risposta.json()
    assert corpo["utente_id"] == bersaglio.utente_id
    # Il token emesso e' davvero una sessione del bersaglio, non del chiamante.
    esito = valida_sessione(db, corpo["token"])
    assert esito is not None
    assert esito[1] == bersaglio.utente_id


def test_non_si_impersona_un_utente_disattivato(client, db):
    """Il login normale passa da verifica_credenziali, che rifiuta gli utenti
    spenti. Qui non c'e' password da verificare: il controllo va ripetuto."""
    _, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)
    bersaglio = f.crea_attuatore(
        db, email=next(_email), ruolo=f.RUOLO_ADERENTE, attivo=f.DISATTIVO
    )

    risposta = client.post(
        f"/auth/login-as/{bersaglio.utente_id}", headers=intestazione
    )

    assert risposta.status_code == 404


@pytest.mark.parametrize(
    "ruolo", [f.RUOLO_SOTTOSCRITTORE, f.RUOLO_CONSULENTE, f.RUOLO_OPERATORE]
)
def test_non_si_impersona_chi_non_potrebbe_accedere(client, db, ruolo):
    _, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)
    bersaglio = f.crea_attuatore(db, email=next(_email), ruolo=ruolo)

    risposta = client.post(
        f"/auth/login-as/{bersaglio.utente_id}", headers=intestazione
    )

    assert risposta.status_code == 404


def test_non_si_ottiene_una_sessione_nazionale_scavalcando_il_2fa(client, db):
    """login-as non aveva il ramo requires_2fa che il login ha: era la strada
    per ottenere proprio la sessione che il login nega."""
    _, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)
    bersaglio = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_NAZIONALE)

    risposta = client.post(
        f"/auth/login-as/{bersaglio.utente_id}", headers=intestazione
    )

    assert risposta.status_code == 403
    assert "token" not in risposta.json()


def test_un_utente_inesistente_non_distingue_dagli_altri_rifiuti(client, db):
    _, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)

    risposta = client.post("/auth/login-as/999999", headers=intestazione)

    assert risposta.status_code == 404


def test_l_impersonificazione_lascia_una_traccia(client, db, caplog):
    chiamante, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)
    bersaglio = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_ADERENTE)

    with caplog.at_level("WARNING", logger="ersaf.auth"):
        client.post(f"/auth/login-as/{bersaglio.utente_id}", headers=intestazione)

    tracce = [r.getMessage() for r in caplog.records if "impersonificazione" in r.getMessage()]
    assert tracce, "l'operazione deve essere tracciata"
    assert str(chiamante.utente_id) in tracce[-1]
    assert str(bersaglio.utente_id) in tracce[-1]
