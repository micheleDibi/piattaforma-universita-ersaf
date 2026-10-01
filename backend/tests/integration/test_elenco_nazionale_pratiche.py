"""Elenco pratiche del Nazionale (senza Bozze, raggruppato per stato) e codice ASG."""

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import text

from src.pratiche.models import Pratica
from tests.support import factories as f
from tests.support.pratiche import pulisci_pratiche
from tests.support.scenari import accedi, accedi_nazionale, riferimenti_pratiche

pytestmark = pytest.mark.mariadb

ECAMPUS = 1
VISTA_NAZIONALE = {"escludi_bozze": "true", "ordine": "stato", "limit": 200}


@pytest.fixture
def mondo(client, db, mailer, tabella_pratiche):
    percorsi = riferimenti_pratiche(db)
    # Gli stati veri (id 1-6) e l'universita' eCampus (id 1): l'ordine dei
    # gruppi e il codice ASG dipendono proprio da questi id.
    for stato in range(1, 7):
        db.execute(text("""
            INSERT INTO pratiche_stati (pratica_stato_id, pratica_stato_codice, pratica_stato_descrizione)
            VALUES (:id, :nome, :nome) ON DUPLICATE KEY UPDATE pratica_stato_id = pratica_stato_id
        """), {"id": stato, "nome": f"Stato {stato}"})
    db.execute(text("""
        INSERT INTO nome_universita (nome_universita_id, nome_universita_codice, nome_universita_descrizione)
        VALUES (1, 'ECAMPUS', 'eCampus') ON DUPLICATE KEY UPDATE nome_universita_id = nome_universita_id
    """))
    db.commit()

    azienda = f.crea_azienda(db)
    _, sessione = accedi(client, db, azienda_id=azienda.azienda_id)
    _, sessione_nazionale = accedi_nazionale(client, db, mailer)
    studente = f.crea_attuatore(db, email="studente@example.org", ruolo=f.RUOLO_SOTTOSCRITTORE)

    def pratica(numero, stato, modificata, universita=900001, asg=None):
        riga = Pratica(pratica_numero=numero, cliente_id=studente.cliente_id,
                       cliente_emittente_aderente_id=studente.cliente_id,
                       listTesta_id=percorsi[0].listTesta_id, pratica_stato_id=stato,
                       nome_universita_id=universita, listino_tipo_corso_id=900001,
                       azienda_id=azienda.azienda_id, pratica_codiceASG=asg,
                       pratica_created_at=datetime(2026, 2, 1), pratica_updated_at=modificata)
        db.add(riga)
        db.commit()
        return riga.pratica_id

    ids = {
        "bozza": pratica("P-BOZZA", 6, datetime(2026, 9, 1)),
        "rifiutata": pratica("P-RIF", 5, datetime(2026, 9, 1)),
        "conclusa": pratica("P-CON", 3, datetime(2026, 9, 1)),
        "attesa": pratica("P-ATT", 2, datetime(2026, 9, 1)),
        "lavorazione": pratica("P-LAV", 4, datetime(2026, 9, 1)),
        "caricata_vecchia": pratica("P-CAR-VECCHIA", 1, datetime(2026, 1, 1)),
        "caricata_nuova": pratica("P-CAR-NUOVA", 1, datetime(2026, 3, 1)),
        "ecampus": pratica("P-ECAMPUS", 3, datetime(2025, 1, 1), universita=ECAMPUS, asg="ASG-1"),
        "ssml": pratica("P-ALTRA", 3, datetime(2024, 1, 1), asg="ASG-AUTO"),
    }
    yield {"sessione": sessione, "nazionale": sessione_nazionale, "ids": ids,
           "percorsi": percorsi, "studente": studente}
    pulisci_pratiche(db)
    for percorso in percorsi:
        db.delete(percorso)
    db.commit()


def _numeri(client, sessione, params):
    risposta = client.get("/pratiche/", params=params, headers=sessione)
    assert risposta.status_code == 200, risposta.text
    return [r["pratica_numero"] for r in risposta.json()]


def _asg(db, pratica_id):
    db.expire_all()
    return db.get(Pratica, pratica_id).pratica_codiceASG


def test_senza_bozze_e_raggruppato_per_stato(client, mondo):
    assert _numeri(client, mondo["nazionale"], VISTA_NAZIONALE) == [
        # Ogni stato dalla modifica piu' recente. Il ripiego sulla data di
        # creazione (pratica_updated_at vuoto nel database reale) qui non si
        # prova: create_all fa la colonna NOT NULL.
        "P-CAR-NUOVA", "P-CAR-VECCHIA",
        "P-LAV", "P-ATT",
        "P-CON", "P-ECAMPUS", "P-ALTRA",
        "P-RIF",
    ]


def test_le_pagine_continuano_il_gruppo(client, mondo):
    pagina = {**VISTA_NAZIONALE, "limit": 2, "skip": 2}
    assert _numeri(client, mondo["nazionale"], pagina) == ["P-LAV", "P-ATT"]


def test_senza_parametri_l_elenco_resta_com_era(client, mondo):
    numeri = _numeri(client, mondo["nazionale"], {"limit": 200})
    assert "P-BOZZA" in numeri
    assert _numeri(client, mondo["sessione"], {"limit": 200}) == numeri


def test_conteggi_per_stato_con_i_filtri_dell_elenco(client, mondo):
    def conteggi(params):
        risposta = client.get("/pratiche/conteggi/stati", params=params, headers=mondo["nazionale"])
        assert risposta.status_code == 200, risposta.text
        return {r["pratica_stato_id"]: r["totale"] for r in risposta.json()}

    assert conteggi(VISTA_NAZIONALE) == {1: 2, 2: 1, 3: 3, 4: 1, 5: 1}
    assert conteggi({"escludi_bozze": "false"})[6] == 1
    assert conteggi({**VISTA_NAZIONALE, "numero_pratica": "P-CAR"}) == {1: 2}
    assert conteggi({**VISTA_NAZIONALE, "nome_universita_id": ECAMPUS}) == {3: 1}


def test_conteggi_protetti(client):
    assert client.get("/pratiche/conteggi/stati").status_code == 401


def test_il_codice_asg_lo_vede_solo_il_nazionale(client, mondo):
    pratica_id = mondo["ids"]["ecampus"]
    for sessione, atteso in ((mondo["sessione"], None), (mondo["nazionale"], "ASG-1")):
        scheda = client.get(f"/pratiche/{pratica_id}", headers=sessione)
        assert scheda.status_code == 200, scheda.text
        assert scheda.json()["pratica_codiceASG"] == atteso
    elenco = client.get("/pratiche/?limit=200", headers=mondo["sessione"]).json()
    assert all(r["pratica_codiceASG"] is None for r in elenco)
    modificata = client.put(f"/pratiche/{pratica_id}", json={"pratica_note": "nota"},
                            headers=mondo["sessione"])
    assert modificata.json()["pratica_codiceASG"] is None


def test_il_codice_asg_lo_modifica_solo_il_nazionale_e_solo_su_ecampus(client, db, mondo):
    ecampus, altra = mondo["ids"]["ecampus"], mondo["ids"]["ssml"]

    ignorato = client.put(f"/pratiche/{ecampus}", json={"pratica_codiceASG": "RUBATO"},
                          headers=mondo["sessione"])
    assert ignorato.status_code == 200, ignorato.text
    assert _asg(db, ecampus) == "ASG-1"

    scritto = client.put(f"/pratiche/{ecampus}", json={"pratica_codiceASG": "  ASG-2  "},
                         headers=mondo["nazionale"])
    assert scritto.status_code == 200, scritto.text
    assert scritto.json()["pratica_codiceASG"] == "ASG-2"
    assert _asg(db, ecampus) == "ASG-2"

    client.put(f"/pratiche/{ecampus}", json={"pratica_codiceASG": ""}, headers=mondo["nazionale"])
    assert _asg(db, ecampus) is None

    client.put(f"/pratiche/{altra}", json={"pratica_codiceASG": "ALTRO"}, headers=mondo["nazionale"])
    assert _asg(db, altra) == "ASG-AUTO"


def test_il_codice_asg_non_si_sceglie_in_creazione(client, db, mondo):
    corpo = {"cliente_id": mondo["studente"].cliente_id, "listTesta_id": mondo["percorsi"][0].listTesta_id,
             "nome_universita_id": 900001, "listino_tipo_corso_id": 900001,
             "pratica_codiceASG": "SCELTO"}
    creata = client.post("/pratiche/", json=corpo, headers=mondo["sessione"])
    assert creata.status_code == 201, creata.text
    assert _asg(db, creata.json()["pratica_id"]) is None
