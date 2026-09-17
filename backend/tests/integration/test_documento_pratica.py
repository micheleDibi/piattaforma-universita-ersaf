"""PDF di una pratica: disponibilita', download, pratica o modello assenti, errore di composizione."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import delete

from src.database import Base, engine
from src.documenti import modelli as registro
from src.documenti import motore
from src.documenti.dati import dati_pratica
from src.aziende.models import Azienda
from src.esami.models import Esame
from src.listini_testa.models import ListinoTestaDB
from src.pratiche.models import Pratica
from src.security.password import hash_password
from tests.support import factories as f
from tests.support.immagini import png_pieno

pytestmark = pytest.mark.mariadb
MODELLI_DI_PROVA = Path(__file__).parents[1] / "support" / "modelli"
ID = 900101  # righe di decodifica proprie: non si scontrano con altri scenari
ENTE, TIPO_CORSO = "Università di Prova", "Laurea di prova"
# Intestazione con cui il gestionale salvava la firma: "BLOBpng" e zeri fino a 16 byte.
INTESTAZIONE_FIRMA = b"BLOBpng" + bytes(9)
FIRMA_PNG = bytes([0x89]) + b"PNG"


@pytest.fixture
def pratica(client, db):
    Base.metadata.create_all(engine)
    account = f.crea_attuatore(db, email="documenti@example.org", password_hash=hash_password("documenti-prova"))
    studente = f.crea_cliente(db, utente_id=account.utente_id, email="studentessa@example.org",
                              nome="Maria", cognome="Della Valle", ruolo=0)
    for tabella, dati in {
        "listini_tipi": {"listino_tipo_codice": "PROVA", "listino_tipo_descrizione": "Prova"},
        "nome_universita": {"nome_universita_codice": "PROVA", "nome_universita_descrizione": ENTE},
        "listini_tipicorsi": {"listino_tipoCorso_descrizione": TIPO_CORSO},
        "pratiche_stati": {"pratica_stato_codice": "PROVA", "pratica_stato_descrizione": "Prova"},
    }.items():
        tabella_db = Base.metadata.tables[tabella]
        chiave = list(tabella_db.primary_key)[0]
        db.execute(tabella_db.delete().where(chiave == ID))
        db.execute(tabella_db.insert().values(**{chiave.name: ID}, **dati))
    listino = ListinoTestaDB(listTesta_codice="PROVA-DOC", listTesta_descrizione="Laurea in Scienze della prova",
                             listino_tipo_id=ID, listino_tipoCorso_id=ID, nome_universita_id=ID)
    db.add(listino)
    db.flush()
    riga = Pratica(pratica_numero="000045", cliente_id=studente.cliente_id, cliente_emittente_aderente_id=account.cliente_id,
                   pratica_stato_id=ID, listTesta_id=listino.listTesta_id, nome_universita_id=ID,
                   listino_tipo_corso_id=ID, pratica_firma=png_pieno())
    db.add(riga)
    db.commit()
    assert client.post("/auth/login", json={"utente_username": account.username, "utente_password": "documenti-prova"}).status_code == 200
    yield riga
    db.execute(delete(Pratica).where(Pratica.pratica_id == riga.pratica_id))
    db.delete(listino)
    db.commit()


@pytest.fixture
def con_modello(monkeypatch):
    """Registra il modello di prova per l'ente e il tipo di corso dello scenario."""
    def registra(arricchisci=lambda dati: {**dati, "nome": dati["cliente"]["cognome"]}):
        monkeypatch.setattr(motore, "CARTELLA_MODELLI", MODELLI_DI_PROVA)
        # Descrizioni scritte diversamente dal database: il confronto e' normalizzato.
        monkeypatch.setattr(registro, "MODELLI", (registro.Modello("prova", "UNIVERSITÀ DI PROVA", "laurea-di-prova", arricchisci),))
    return registra


def _rinomina(db, tabella: str, **valori):
    """Cambia la descrizione di una riga di decodifica dello scenario."""
    tabella_db = Base.metadata.tables[tabella]
    db.execute(tabella_db.update().where(list(tabella_db.primary_key)[0] == ID).values(**valori))
    db.commit()


def test_senza_modello_il_documento_non_e_disponibile(client, pratica):
    assert client.get(f"/pratiche/{pratica.pratica_id}/documento/disponibile").json() == {"disponibile": False, "nome_file": None}
    risposta = client.get(f"/pratiche/{pratica.pratica_id}/documento")
    assert risposta.status_code == 404
    assert "non è ancora disponibile" in risposta.json()["detail"]


def test_con_il_modello_si_scarica_il_pdf(client, pratica, con_modello):
    con_modello()
    assert client.get(f"/pratiche/{pratica.pratica_id}/documento/disponibile").json() == {
        "disponibile": True, "nome_file": "pratica-000045.pdf"}
    risposta = client.get(f"/pratiche/{pratica.pratica_id}/documento")
    assert risposta.status_code == 200, risposta.text
    assert risposta.headers["content-type"] == "application/pdf"
    assert risposta.headers["content-disposition"] == 'attachment; filename="pratica-000045.pdf"'
    assert risposta.headers["cache-control"] == "no-store"
    assert risposta.content.startswith(b"%PDF-") and b"pdfaid" in risposta.content


def test_pratica_inesistente(client, pratica, con_modello):
    con_modello()
    for percorso in ("documento", "documento/disponibile"):
        assert client.get(f"/pratiche/999999999/{percorso}").status_code == 404


def test_un_errore_di_composizione_non_espone_dettagli(client, pratica, con_modello, caplog):
    con_modello(arricchisci=lambda dati: dati)  # manca "nome": Typst si ferma
    risposta = client.get(f"/pratiche/{pratica.pratica_id}/documento")
    assert risposta.status_code == 500
    assert risposta.json()["detail"].startswith("Non è stato possibile comporre il documento")
    assert "Della Valle" not in risposta.text
    assert any("composizione del documento fallita" in r.getMessage() for r in caplog.records)
    assert not any("Della Valle" in r.getMessage() for r in caplog.records)


def test_il_luogo_delle_firme_e_la_citta_dell_azienda_della_pratica(db, pratica):
    assert dati_pratica(db, pratica)[0]["azienda"] == {"citta": ""}
    azienda = Azienda(azienda_ragione_sociale="Centro Studi Aurora", azienda_partitaIVA="01234567890",
                      azienda_via="Via Roma", azienda_citta="Santa Maria Capua Vetere", azienda_CAP="81055",
                      azienda_provincia="CE")
    db.add(azienda)
    db.flush()
    pratica.azienda_id = azienda.azienda_id
    db.commit()
    db.refresh(pratica)
    assert dati_pratica(db, pratica)[0]["azienda"] == {"citta": "Santa Maria Capua Vetere"}


def test_i_dati_comuni_hanno_gli_esami_in_ordine_e_la_firma_senza_intestazione(db, pratica):
    for insegnamento, giorno in (("Psicologia generale", date(2017, 6, 20)), ("Pedagogia generale", date(2017, 6, 11))):
        db.add(Esame(esame_insegnamento=insegnamento, esame_cfu=8, esame_voto=28, esame_data=giorno, esame_ssd="M-PED/01",
                     esame_corsoDiLaurea="Scienze dell'educazione", esame_ordinamento="DM 270/04",
                     esame_universita="Università degli Studi di Pavia", cliente_id=pratica.cliente_id))
    pratica.pratica_firma = INTESTAZIONE_FIRMA + png_pieno()
    db.commit()
    try:
        dati, allegati = dati_pratica(db, pratica)
        assert [(e["insegnamento"], e["data"], e["voto"]) for e in dati["esami"]] == [
            ("Pedagogia generale", "11/06/2017", "28"), ("Psicologia generale", "20/06/2017", "28")]
        assert allegati["firma"].startswith(FIRMA_PNG)
    finally:
        db.execute(delete(Esame).where(Esame.cliente_id == pratica.cliente_id))
        db.commit()


def test_una_pratica_ecampus_lauree_scarica_il_modulo_completo(client, db, pratica):
    _rinomina(db, "nome_universita", nome_universita_descrizione="Università Telematica eCampus")
    _rinomina(db, "listini_tipicorsi", listino_tipoCorso_descrizione="LAUREE")
    assert client.get(f"/pratiche/{pratica.pratica_id}/documento/disponibile").json()["disponibile"] is True
    risposta = client.get(f"/pratiche/{pratica.pratica_id}/documento")
    assert risposta.status_code == 200, risposta.text
    assert b"/Count 10" in risposta.content and b"pdfaid" in risposta.content
