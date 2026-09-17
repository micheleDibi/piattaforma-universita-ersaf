"""`POST` e `PUT /ruoli`: solo il Nazionale.

Il Nazionale si riconosce confrontando la stringa `ruolo_codice`. Quando le due
rotte chiedevano solo il login, bastava rinominare "Nazionale" e poi dare quel
nome a un altro ruolo perche' tutti i suoi utenti vedessero ogni cliente.
"""

from __future__ import annotations

import pytest

from src.ruolo.models import Ruolo
from tests.support.scenari import accedi, accedi_nazionale

pytestmark = pytest.mark.mariadb

SOLO_NAZIONALE = {"detail": "Solo il nazionale può eseguire questa operazione."}


@pytest.fixture
def ruoli_originali(db):
    """`ruoli` non si svuota fra un test e l'altro: si rimette com'era."""
    prima = {r.ruolo_id: (r.ruolo_codice, r.ruolo_descrizione) for r in db.query(Ruolo)}
    yield
    db.expire_all()
    for ruolo in db.query(Ruolo).all():
        if ruolo.ruolo_id in prima:
            ruolo.ruolo_codice, ruolo.ruolo_descrizione = prima[ruolo.ruolo_id]
        else:
            db.delete(ruolo)
    db.commit()


def test_un_regionale_non_tocca_i_ruoli(client, db, ruoli_originali):
    _, intestazione = accedi(client, db)

    rinomina = client.put("/ruoli/5", json={"ruolo_codice": "Altro"}, headers=intestazione)
    nuovo = client.post("/ruoli/", json={"ruolo_codice": "X", "ruolo_descrizione": "X"}, headers=intestazione)

    assert (rinomina.status_code, rinomina.json()) == (403, SOLO_NAZIONALE)
    assert (nuovo.status_code, nuovo.json()) == (403, SOLO_NAZIONALE)
    db.expire_all()
    assert db.get(Ruolo, 5).ruolo_codice == "Nazionale"
    assert db.query(Ruolo).filter(Ruolo.ruolo_codice == "X").count() == 0


def test_il_nazionale_li_modifica(client, db, mailer, ruoli_originali):
    _, intestazione = accedi_nazionale(client, db, mailer)

    rinomina = client.put("/ruoli/6", json={"ruolo_descrizione": "Operatore di prova"}, headers=intestazione)
    nuovo = client.post("/ruoli/", json={"ruolo_codice": "Prova", "ruolo_descrizione": "P"}, headers=intestazione)

    assert rinomina.status_code == 200, rinomina.text
    assert nuovo.status_code == 201, nuovo.text


def test_la_lettura_resta_a_tutti(client, db):
    _, intestazione = accedi(client, db)
    assert client.get("/ruoli/", headers=intestazione).status_code == 200
