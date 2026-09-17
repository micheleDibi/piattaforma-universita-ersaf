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
from tests.support.scenari import accedi, accedi_nazionale
from tests.support.sessioni import token_cookie, intestazioni_sessione

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
    return attuatore, intestazioni_sessione(token_cookie(risposta))


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


# =============================================================================
# Padre fra i soli utenti visibili
# =============================================================================
def _cambia_padre(client, intestazione, utente_id, padre):
    return client.put(f"/utenti/{utente_id}", json={"utente_padre": padre}, headers=intestazione)


def _non_esiste(utente_id):
    return {"detail": f"L'utente padre con id {utente_id} non esiste."}


def test_un_padre_non_visibile_come_uno_inesistente(client, db):
    io, intestazione = accedi(client, db, ruolo=f.RUOLO_ADERENTE)
    estraneo = f.crea_attuatore(db, email=next(_email))

    risposta = _cambia_padre(client, intestazione, io.utente_id, estraneo.utente_id)

    assert risposta.status_code == 404
    assert risposta.json() == _non_esiste(estraneo.utente_id)
    db.expire_all()
    assert db.get(Utente, io.utente_id).utente_padre is None


def test_padre_ammessi_e_rifiutati(client, db):
    azienda = f.crea_azienda(db)
    io, intestazione = accedi(client, db, azienda_id=azienda.azienda_id)
    figlio = f.crea_attuatore(db, email=next(_email), padre=io.utente_id)
    nipote = f.crea_attuatore(db, email=next(_email), padre=figlio.utente_id)
    collega = f.crea_attuatore(db, email=next(_email), azienda_id=azienda.azienda_id)
    senza_anagrafica = f.crea_utente(db, padre=io.utente_id)

    # Il chiamante stesso, su un utente che vede.
    assert _cambia_padre(client, intestazione, nipote.utente_id, io.utente_id).status_code == 200
    # Un discendente visibile, anche se crea un ciclo.
    assert _cambia_padre(client, intestazione, io.utente_id, figlio.utente_id).status_code == 200
    # Un collega non e' visibile in quanto collega.
    risposta = _cambia_padre(client, intestazione, figlio.utente_id, collega.utente_id)
    assert (risposta.status_code, risposta.json()) == (404, _non_esiste(collega.utente_id))
    # Serve almeno una riga clienti visibile.
    risposta = _cambia_padre(client, intestazione, figlio.utente_id, senza_anagrafica.utente_id)
    assert (risposta.status_code, risposta.json()) == (404, _non_esiste(senza_anagrafica.utente_id))


def test_il_rifiuto_del_padre_non_cancella_l_attivazione(client, db, spia_sql):
    from src.otp.models import Attivazione

    io, intestazione = accedi(client, db)
    figlio = f.crea_attuatore(db, email=next(_email), padre=io.utente_id)
    estraneo = f.crea_attuatore(db, email=next(_email))
    db.add(Attivazione(utente_id=figlio.utente_id, cliente_id=figlio.cliente_id))
    db.commit()
    spia_sql.clear()

    risposta = client.put(
        f"/utenti/{figlio.utente_id}",
        json={"utente_attivoSN": f.ATTIVO, "utente_padre": estraneo.utente_id},
        headers=intestazione,
    )

    assert risposta.status_code == 404
    # Non basta che la riga ci sia ancora: il rollback annullerebbe comunque
    # la DELETE. La DELETE non deve proprio partire.
    assert not any("otp_attivazioni" in istruzione and istruzione.lstrip().upper().startswith("DELETE")
                   for istruzione in spia_sql)
    db.expire_all()
    assert db.get(Attivazione, figlio.utente_id) is not None


def test_la_creazione_rifiuta_un_padre_non_visibile(client, db):
    _, intestazione = accedi(client, db)
    estraneo = f.crea_attuatore(db, email=next(_email))
    risposta = client.post("/utenti/", headers=intestazione, json={
        "utente_username": "nuovo.utente",
        "utente_password": "una-password-abbastanza-lunga",
        "utente_padre": estraneo.utente_id,
    })
    assert risposta.status_code == 404
    assert risposta.json() == _non_esiste(estraneo.utente_id)


def test_il_nazionale_sceglie_qualunque_padre(client, db, mailer):
    estraneo = f.crea_attuatore(db, email=next(_email))
    altro = f.crea_attuatore(db, email=next(_email))
    _, intestazione = accedi_nazionale(client, db, mailer)
    assert _cambia_padre(client, intestazione, altro.utente_id, estraneo.utente_id).status_code == 200


def test_il_chiamante_e_sempre_un_padre_ammesso(db):
    """La propria riga "me" e' sempre visibile, quindi via HTTP il ramo
    "padre = chiamante" non si distingue. Conta per un chiamante senza
    anagrafica, che non ha righe visibili: lo si prova sulla funzione."""
    from fastapi import HTTPException

    from src.auth.visibilita import Visibilita
    from src.utenti.routers import _verifica_padre

    senza_anagrafica = f.crea_utente(db)
    figlio = f.crea_utente(db, padre=senza_anagrafica.utente_id)
    estraneo = f.crea_attuatore(db, email=next(_email))
    vis = Visibilita(utente_id=senza_anagrafica.utente_id, nazionale=False)

    _verifica_padre(db, senza_anagrafica.utente_id, utente_id=figlio.utente_id, vis=vis)
    with pytest.raises(HTTPException) as rifiuto:
        _verifica_padre(db, estraneo.utente_id, utente_id=figlio.utente_id, vis=vis)
    assert rifiuto.value.status_code == 404

