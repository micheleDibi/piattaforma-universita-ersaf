"""Numerazione pratica: concorrenza, rollback e ripartenza dal legacy sintetico."""

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database import engine
from src.errori import CodicePraticaError
from src.pratiche.codice import genera_codici_pratica
from src.pratiche.models import Pratica
from tests.conftest import RADICE
from tests.support import factories as f
from tests.support.scenari import accedi, riferimenti_pratiche
from tests.support.sqlrunner import esegui_file_sql

pytestmark = pytest.mark.mariadb


def codice(db, universita="SSML", tipo=1):
    return genera_codici_pratica(db, nome_universita_codice=universita,
                                 listino_tipo_corso_id=tipo)


def test_prefissi_indipendenti_e_codice_asg(db):
    assert codice(db).numero == "MT000001"
    assert codice(db, tipo=2).codice_asg == "MT000002"
    a4u = codice(db, "A4U", 4)
    assert (a4u.numero, a4u.codice_asg) == ("A4U_CP000001", None)
    assert codice(db, "eCampus") is None
    db.rollback()


def test_rollback_non_consuma_il_progressivo(db):
    assert codice(db).numero == "MT000001"
    db.rollback()
    assert codice(db).numero == "MT000001"
    db.commit()
    assert codice(db).numero == "MT000002"
    db.rollback()


def test_creazioni_concorrenti_non_duplicano_il_codice(db_pulito):
    barriera = Barrier(8)

    def crea(_):
        barriera.wait(timeout=10)
        with Session(engine) as sessione:
            risultato = codice(sessione).numero
            sessione.commit()
            return risultato

    with ThreadPoolExecutor(max_workers=8) as executor:
        risultati = list(executor.map(crea, range(8)))
    assert sorted(risultati) == [f"MT{n:06d}" for n in range(1, 9)]


def test_esaurimento_e_tipo_non_supportato_non_corrompono_contatore(db):
    db.execute(text("INSERT INTO pratiche_contatori VALUES ('MT', 999999)"))
    db.commit()
    with pytest.raises(CodicePraticaError):
        codice(db)
    db.rollback()
    assert db.execute(text("SELECT ultimo_numero FROM pratiche_contatori")).scalar() == 999999
    with pytest.raises(CodicePraticaError):
        codice(db, tipo=5)


@pytest.fixture
def scenario(client, db, tabella_pratiche):
    percorsi = riferimenti_pratiche(db)
    azienda = f.crea_azienda(db)
    persona, sessione = accedi(client, db, azienda_id=azienda.azienda_id)
    dati = dict(cliente_id=persona.cliente_id, cliente_emittente_aderente_id=persona.cliente_id,
                listTesta_id=percorsi[0].listTesta_id, pratica_stato_id=900001,
                nome_universita_id=900001, listino_tipo_corso_id=900001)
    yield dati, sessione
    db.rollback()
    db.query(Pratica).delete()
    for percorso in percorsi:
        db.delete(percorso)
    db.execute(text("UPDATE nome_universita SET nome_universita_codice='TEST' WHERE nome_universita_id=900001"))
    db.commit()


def test_seed_riprende_massimo_per_prefisso_ed_e_idempotente(db, scenario):
    dati, _ = scenario
    for numero in ("MT000040", "MT000042", "A4U_CP000007", "legacy", "---", "MT123"):
        db.add(Pratica(pratica_numero=numero, **dati))
    db.commit()
    migrazione = RADICE / "db/migrations/020_contatori_codice_pratica.sql"
    esegui_file_sql(os.environ["TEST_DATABASE_URL"], migrazione)
    assert codice(db).numero == "MT000043"
    assert codice(db, "A4U", 4).numero == "A4U_CP000008"
    db.commit()
    esegui_file_sql(os.environ["TEST_DATABASE_URL"], migrazione)
    assert codice(db).numero == "MT000044"
    db.rollback()


def test_rifiuto_codice_annulla_anche_inserimento_pratica(client, db, scenario):
    dati, sessione = scenario
    db.execute(text("UPDATE nome_universita SET nome_universita_codice='SSML' WHERE nome_universita_id=900001"))
    db.commit()
    risposta = client.post("/pratiche/", json=dati, headers=sessione)
    assert risposta.status_code == 400, risposta.text
    assert db.query(Pratica).count() == 0
    assert db.execute(text("SELECT COUNT(*) FROM pratiche_contatori")).scalar() == 0
