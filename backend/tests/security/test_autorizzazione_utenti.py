"""`PUT /utenti/{id}`: autenticato non basta.

L'endpoint chiedeva il token e poi non guardava chi fosse: nessun confronto fra
l'id nel percorso e quello della sessione, nessun controllo di ruolo. Qualunque
utente loggato poteva disattivare o rinominare qualunque altro dei 4.771.

    PUT /utenti/1 {"utente_attivoSN": 0}

spegneva l'amministratore.
"""

from __future__ import annotations

import pytest

from src.security.password import hash_password
from src.utenti.models import Utente
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

PASSWORD = "cavallo-batteria-graffetta"
_email = iter(f"a{n}@example.org" for n in range(1, 999))


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


def test_un_utente_qualsiasi_non_puo_spegnere_un_altro(client, db):
    _, intestazione = _sessione(client, db, f.RUOLO_ADERENTE)
    vittima = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_REGIONALE)

    risposta = client.put(
        f"/utenti/{vittima.utente_id}",
        json={"utente_attivoSN": 0},
        headers=intestazione,
    )

    assert risposta.status_code == 403
    db.expire_all()
    assert db.get(Utente, vittima.utente_id).utente_attivoSN == -1


def test_si_puo_sempre_modificare_se_stessi(client, db):
    io, intestazione = _sessione(client, db, f.RUOLO_ADERENTE)

    risposta = client.put(
        f"/utenti/{io.utente_id}",
        json={"utente_username": "nuovo-nome"},
        headers=intestazione,
    )

    assert risposta.status_code == 200, risposta.text
    db.expire_all()
    assert db.get(Utente, io.utente_id).utente_username == "nuovo-nome"


def test_un_ruolo_amministrativo_puo_modificare_gli_altri(client, db):
    _, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)
    altro = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_ADERENTE)

    risposta = client.put(
        f"/utenti/{altro.utente_id}",
        json={"utente_attivoSN": 0},
        headers=intestazione,
    )

    assert risposta.status_code == 200, risposta.text
    db.expire_all()
    assert db.get(Utente, altro.utente_id).utente_attivoSN == 0


def test_un_put_parziale_non_azzera_chi_ha_creato_la_riga(client, db):
    io, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)
    altro = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_ADERENTE)
    db.get(Utente, altro.utente_id).utente_created_by = io.utente_id
    db.commit()

    client.put(
        f"/utenti/{altro.utente_id}",
        json={"utente_attivoSN": 0},
        headers=intestazione,
    )

    db.expire_all()
    assert db.get(Utente, altro.utente_id).utente_created_by == io.utente_id


def test_l_elenco_degli_username_non_e_pubblico(client, db):
    """GET /utenti/ era aperto ed esponeva i 4.771 utente_username, annullando
    il lavoro anti-enumerazione di /auth/login."""
    f.crea_attuatore(db, email=next(_email), username="MarioRossi")

    assert client.get("/utenti/").status_code == 401


def test_padre_e_aggiornato_da_risolvono_contro_utenti(client, db):
    """Le due ForeignKey puntavano a clienti.cliente_id mentre il database
    punta a utenti.utente_id e il codice ci scrive un utente_id: cliente_id e
    utente_id coincidono solo in 377 clienti su 3.906, quindi la scheda
    mostrava un'altra persona."""
    padre, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)
    figlio = f.crea_attuatore(db, email=next(_email), ruolo=f.RUOLO_ADERENTE)
    riga = db.get(Utente, figlio.utente_id)
    riga.utente_padre = padre.utente_id
    db.commit()

    corpo = client.get(f"/utenti/{figlio.utente_id}", headers=intestazione).json()

    assert corpo["padre"]["utente_id"] == padre.utente_id
    assert corpo["padre"]["utente_username"] == padre.username


def test_utente_padre_deve_esistere(client, db):
    """Il database ha la FOREIGN KEY su created_by e updated_by ma NON su
    utente_padre: si poteva scrivere un id qualsiasi, e la scheda mostrava
    "ID: 999999" senza che nessuno potesse risalire a chi fosse."""
    io, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)

    risposta = client.put(
        f"/utenti/{io.utente_id}",
        json={"utente_padre": 999999},
        headers=intestazione,
    )

    assert risposta.status_code == 404
    db.expire_all()
    assert db.get(Utente, io.utente_id).utente_padre != 999999


def test_un_utente_non_e_padre_di_se_stesso(client, db):
    io, intestazione = _sessione(client, db, f.RUOLO_REGIONALE)

    risposta = client.put(
        f"/utenti/{io.utente_id}",
        json={"utente_padre": io.utente_id},
        headers=intestazione,
    )

    assert risposta.status_code == 422
