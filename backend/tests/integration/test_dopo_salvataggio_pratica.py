"""Dopo la creazione di una pratica: codice A4U, articolo e partitario (vedi
src/pratiche/dopo_salvataggio.py). Solo su MariaDB reale: lo schema dei
pagamenti e' `ersaf_test` stesso, con le tabelle di tests/support/contabilita.py."""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database import Base, engine
from src.listini_testa.models import ListinoTestaDB
from src.pratiche.codice import prossimo_numero_oltre
from src.pratiche.models import Pratica
from tests.support import factories as f
from tests.support import scenari
from tests.support.pratiche import pulisci_pratiche

pytestmark = pytest.mark.mariadb

UNIVERSITA = {900011: "SSML", 900012: "A4U", 900013: "eCampus"}
TIPI_CORSO = {2: "MASTER AREA SCUOLA", 9: "CORSI SINGOLI"}


@pytest.fixture
def scenario(client, db, tabella_pratiche):
    azienda = f.crea_azienda(db)
    account, intestazioni = scenari.accedi(client, db, ruolo=f.RUOLO_ADERENTE, azienda_id=azienda.azienda_id)
    studente = f.crea_cliente(db, utente_id=account.utente_id, email=scenari.email_nuova("studente-contab"),
                               nome="Mario", cognome="Rossi", ruolo=0)
    tabelle = Base.metadata.tables
    # Residui di un'esecuzione interrotta: i percorsi bloccherebbero le delete sotto.
    db.query(ListinoTestaDB).filter(ListinoTestaDB.nome_universita_id.in_(list(UNIVERSITA))).delete()
    for tabella, righe in {
        "listini_tipi": {900011: {"listino_tipo_codice": "TEST", "listino_tipo_descrizione": "Test"}},
        "nome_universita": {i: {"nome_universita_codice": c, "nome_universita_descrizione": c}
                            for i, c in UNIVERSITA.items()},
        "listini_tipicorsi": {i: {"listino_tipoCorso_descrizione": d} for i, d in TIPI_CORSO.items()},
    }.items():
        chiave = list(tabelle[tabella].primary_key)[0]
        db.execute(tabelle[tabella].delete().where(chiave.in_(list(righe))))
        for numero, valori in righe.items():
            db.execute(tabelle[tabella].insert().values(**{chiave.name: numero}, **valori))
    percorsi = {}
    for universita_id in UNIVERSITA:
        for tipo in TIPI_CORSO:
            percorso = ListinoTestaDB(
                listTesta_codice=f"MED/{tipo}", listTesta_descrizione="IGIENE GENERALE",
                listino_tipo_id=900011, listino_tipoCorso_id=tipo, nome_universita_id=universita_id,
            )
            db.add(percorso)
            percorsi[universita_id, tipo] = percorso
    db.commit()

    def crea(universita_id, tipo=9, **extra):
        corpo = {"cliente_id": studente.cliente_id, "listTesta_id": percorsi[universita_id, tipo].listTesta_id,
                 "nome_universita_id": universita_id, "listino_tipo_corso_id": tipo,
                 "pratica_prezzo": "525.00", **extra}
        return client.post("/pratiche/", json=corpo, headers=intestazioni)

    yield crea, account, studente
    db.rollback()
    pulisci_pratiche(db)
    for percorso in percorsi.values():
        db.delete(percorso)
    db.flush()  # la sessione non fa autoflush: i percorsi vanno tolti prima delle universita'
    for tabella, ids in (("nome_universita", UNIVERSITA), ("listini_tipicorsi", TIPI_CORSO),
                         ("listini_tipi", [900011])):
        chiave = list(tabelle[tabella].primary_key)[0]
        db.execute(tabelle[tabella].delete().where(chiave.in_(list(ids))))
    db.commit()


def righe(db, sql, **valori):
    return db.execute(text(sql), valori).mappings().all()


def contabilita_di(db, pratica_id):
    return righe(db, """
        SELECT a.articolo_codice, a.articolo_descrizione, a.articolo_prezzo, g.articolo_gruppo_codice,
               t.articolo_tipo_codice, d.documento_codice, d.documento_totale, d.cliente_id,
               d.fornitore_id, d.documento_data_creazione, a.articolo_createdBy
          FROM articolo_pratica ap
          JOIN articolo a ON a.articolo_id = ap.articolo_id
          JOIN articolo_gruppo g ON g.articolo_gruppo_id = a.articolo_gruppo_id
          JOIN articolo_tipo t ON t.articolo_tipo_id = a.articolo_tipo_id
          JOIN documento_articolo da ON da.articolo_id = a.articolo_id
          JOIN documento d ON d.documento_id = da.documento_id
         WHERE ap.pratica_id = :p""", p=pratica_id)


def test_ssml_crea_articolo_e_partitario_collegati(db, scenario):
    crea, account, studente = scenario
    risposta = crea(900011)
    assert risposta.status_code == 201, risposta.text
    pratica = risposta.json()

    [riga] = contabilita_di(db, pratica["pratica_id"])
    assert riga["articolo_codice"] == "ARTICOLO_PRATICA_1"
    assert riga["documento_codice"] == "PARTITARIO_PRATICA_1"
    assert riga["articolo_descrizione"] == (
        "Documento di riferimento: PARTITARIO_PRATICA_1 - Pratica per CORSI SINGOLI: "
        "MED/9 - IGIENE GENERALE di Mario Rossi")
    assert riga["articolo_gruppo_codice"] == "PRATICA CORSI SINGOLI"
    assert riga["articolo_tipo_codice"] == "PRATICA"
    assert riga["articolo_prezzo"] == riga["documento_totale"] == Decimal("525")
    assert riga["cliente_id"] == studente.cliente_id
    # Il fornitore e' il primo cliente dell'utente della pratica: l'account.
    assert riga["fornitore_id"] == account.cliente_id
    assert riga["articolo_createdBy"] == account.utente_id
    assert riga["documento_data_creazione"] is not None
    assert righe(db, "SELECT * FROM pratica_codice") == []


def test_a4u_registra_il_codice_e_mappa_il_tipo_corso_per_id(db, scenario):
    crea, account, _ = scenario
    # Master area scuola: nessun gruppo "PRATICA MASTER AREA SCUOLA", va su Master.
    risposta = crea(900012, tipo=2)
    assert risposta.status_code == 201, risposta.text
    pratica = risposta.json()
    assert pratica["pratica_numero"] == "A4U_MT000001"

    [codice] = righe(db, "SELECT * FROM pratica_codice WHERE pratica_id = :p", p=pratica["pratica_id"])
    assert codice["pratica_codice_temporanreo"] == codice["pratica_codice_permanente"] == "A4U_MT000001"
    assert codice["pratica_codice_assigned_by"] == account.utente_id
    assert codice["pratica_codice_assigned_at"] is not None
    [riga] = contabilita_di(db, pratica["pratica_id"])
    assert riga["articolo_gruppo_codice"] == "PRATICA MASTER"
    assert "Pratica per MASTER AREA SCUOLA:" in riga["articolo_descrizione"]


def test_altre_universita_non_toccano_la_contabilita(db, scenario):
    crea, _, _ = scenario
    risposta = crea(900013)
    assert risposta.status_code == 201, risposta.text
    for tabella in ("articolo", "documento", "pratica_codice"):
        assert righe(db, f"SELECT * FROM {tabella}") == []


def test_progressivi_ripartono_dal_massimo_e_seguono_il_gestionale(db, scenario):
    crea, _, _ = scenario
    for codice in ("ARTICOLO_PRATICA_40", "ARTICOLO_PRATICA_7", "ARTICOLO_PRATICA_X", "ALTRO_99"):
        db.execute(text("""INSERT INTO articolo (articolo_codice, articolo_descrizione, articolo_tipo_id,
                           articolo_gruppo_id, articolo_createdBy, articolo_updatedBy)
                           VALUES (:c, 'legacy', 1, 1, 1, 1)"""), {"c": codice})
    db.execute(text("""INSERT INTO documento (documento_codice, cliente_id, fornitore_id, documento_createdBy,
                       documento_updatedBy, documento_data_creazione)
                       VALUES ('PARTITARIO_PRATICA_55', 1, 1, 1, 1, CURDATE())"""))
    db.commit()

    prima = crea(900011).json()
    [riga] = contabilita_di(db, prima["pratica_id"])
    assert (riga["articolo_codice"], riga["documento_codice"]) == ("ARTICOLO_PRATICA_41", "PARTITARIO_PRATICA_56")

    # Il gestionale precedente scrive ancora con MAX + 1: il contatore lo segue.
    db.execute(text("UPDATE articolo SET articolo_codice = 'ARTICOLO_PRATICA_100' WHERE articolo_codice = 'ALTRO_99'"))
    db.commit()
    seconda = crea(900011).json()
    [riga] = contabilita_di(db, seconda["pratica_id"])
    assert (riga["articolo_codice"], riga["documento_codice"]) == ("ARTICOLO_PRATICA_101", "PARTITARIO_PRATICA_57")


def test_dato_mancante_non_salva_nulla(db, scenario):
    crea, _, _ = scenario
    db.execute(text("DELETE FROM articolo_gruppo WHERE articolo_gruppo_codice = 'PRATICA CORSI SINGOLI'"))
    db.commit()
    risposta = crea(900011)
    assert risposta.status_code == 400, risposta.text
    assert "PRATICA CORSI SINGOLI" in risposta.json()["detail"]
    assert db.query(Pratica).count() == 0
    assert db.execute(text("SELECT COUNT(*) FROM pratiche_contatori")).scalar() == 0
    for tabella in ("articolo", "documento", "articolo_pratica", "documento_articolo"):
        assert righe(db, f"SELECT * FROM {tabella}") == []


def test_utente_senza_cliente_non_ha_fornitore(db, scenario):
    crea, _, _ = scenario
    orfano = f.crea_utente_orfano(db, username=scenari.email_nuova("orfano"))
    risposta = crea(900011, utente_id=orfano.utente_id)
    assert risposta.status_code == 400, risposta.text
    assert "fornitore" in risposta.json()["detail"]
    assert db.query(Pratica).count() == 0


def test_contatori_concorrenti_non_duplicano(db_pulito):
    barriera = Barrier(8)

    def numero(_):
        barriera.wait(timeout=10)
        with Session(engine) as sessione:
            risultato = prossimo_numero_oltre(sessione, "PARTITARIO_PRATICA_", 40)
            sessione.commit()
            return risultato

    with ThreadPoolExecutor(max_workers=8) as executor:
        assert sorted(executor.map(numero, range(8))) == list(range(41, 49))
