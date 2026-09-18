"""Gli avvisi rispettano la visibilita', anche fra pagine diverse dell'elenco."""

from datetime import date, timedelta

import pytest

from src.clienti.models import Cliente
from tests.support import factories as f
from tests.support.scenari import accedi, accedi_nazionale

pytestmark = pytest.mark.mariadb


def test_duplicati_solo_visibili_anche_fuori_pagina(client, db, mailer):
    io, sessione = accedi(client, db)
    primo = f.crea_attuatore(db, email="duplicato@example.org", nome="VisibileUno", padre=io.utente_id)
    f.crea_attuatore(db, email="DUPLICATO@example.org", nome="VisibileDue", padre=io.utente_id)
    estraneo = f.crea_attuatore(db, email="duplicato@example.org", nome="Nascosto")
    dettaglio = client.get(f"/clienti/{primo.cliente_id}", headers=sessione)
    assert dettaglio.status_code == 200
    avvisi = dettaglio.json()["anomalie"]
    assert any("VisibileDue" in a for a in avvisi)
    assert not any("Nascosto" in a for a in avvisi)
    pagina = client.get("/clienti/?search=VisibileUno&limit=1", headers=sessione)
    assert pagina.status_code == 200
    assert pagina.json()[0]["anomalie"] == avvisi
    assert client.get(f"/clienti/{estraneo.cliente_id}", headers=sessione).status_code == 404
    _, nazionale = accedi_nazionale(client, db, mailer)
    tutti = client.get(f"/clienti/{primo.cliente_id}", headers=nazionale).json()["anomalie"]
    assert any("Nascosto" in a for a in tutti)


def test_anomalie_storiche_non_impediscono_la_lettura_o_una_modifica_estranea(client, db):
    io, sessione = accedi(client, db)
    persona = f.crea_attuatore(db, email="email-non-valida", padre=io.utente_id)
    riga = db.get(Cliente, persona.cliente_id)
    riga.cliente_codice_fiscale = "CFERRATO"
    riga.cliente_dataScadenzaDocumento = date.today() - timedelta(days=5)
    db.commit()
    risposta = client.get(f"/clienti/{persona.cliente_id}", headers=sessione)
    assert risposta.status_code == 200
    assert len(risposta.json()["anomalie"]) == 2
    modifica = client.put(f"/clienti/{persona.cliente_id}", headers=sessione, json={
        "cliente_email": "email-non-valida", "cliente_codice_fiscale": "CFERRATO",
        "cliente_dataScadenzaDocumento": riga.cliente_dataScadenzaDocumento.isoformat(), "cliente_citta": "Roma",
    })
    assert modifica.status_code == 200, modifica.text
    assert len(modifica.json()["anomalie"]) == 2
    for campo, valore in (("cliente_email", "altra-email-errata"), ("cliente_codice_fiscale", "ALTROERRATO"),
                          ("cliente_dataScadenzaDocumento", (date.today() - timedelta(days=1)).isoformat())):
        assert client.put(f"/clienti/{persona.cliente_id}", headers=sessione, json={campo: valore}).status_code == 422
