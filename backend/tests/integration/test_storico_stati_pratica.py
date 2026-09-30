"""Storico dei cambi di stato, le due email di 'prima volta' (vedi
src/pratiche/storico_stati.py e src/pratiche/notifiche.py) e la regola per
cui una pratica nasce sempre in Bozza e solo il Nazionale ne cambia lo
stato: solo su MariaDB reale, come le altre query su pratiche."""
import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, HTTPException

from src.auth.visibilita import Visibilita
from src.database import Base, engine
from src.pratiche.models import Pratica
from src.pratiche.schemi import PraticaUpdate
from src.pratiche.routers import aggiorna_pratica
from src.pratiche.rinnovi import CAMPI_RINNOVO
from src.pratiche_stati_storico.models import PraticaStatoStorico
from src.utenti.models import Utente
from src.listini_testa.models import ListinoTestaDB
from tests.support import factories as f
from tests.support import scenari

pytestmark = pytest.mark.mariadb

STATO_BOZZA = 6
STATO_CARICATA = 1


@pytest.fixture
def scenario(client, db, mailer, tabella_pratiche):
    Base.metadata.create_all(engine)
    db.execute(delete(Pratica))
    azienda = f.crea_azienda(db)
    account, intestazioni_account = scenari.accedi(client, db, ruolo=f.RUOLO_ADERENTE, azienda_id=azienda.azienda_id)
    studente = f.crea_cliente(db, utente_id=account.utente_id, email=scenari.email_nuova("studente-storico"),
                               nome="Dario", cognome="Storico", ruolo=0)
    nazionale, intestazioni_nazionale = scenari.accedi_nazionale(client, db, mailer, azienda_id=azienda.azienda_id)
    for tabella, dati in {
        "listini_tipi": {"listino_tipo_codice": "TEST", "listino_tipo_descrizione": "Test"},
        "nome_universita": {"nome_universita_codice": "TEST", "nome_universita_descrizione": "Test"},
        "listini_tipicorsi": {"listino_tipoCorso_descrizione": "Test"},
    }.items():
        tabella_db = Base.metadata.tables[tabella]
        chiave = list(tabella_db.primary_key)[0]
        db.execute(tabella_db.delete().where(chiave.in_([900001])))
        db.execute(tabella_db.insert().values(**{chiave.name: 900001}, **dati))
    # Bozza (6) e Caricata (1): stessi id di STATI_PANNELLO nel frontend, non
    # gli id sintetici 900001/900002 usati altrove: qui contano proprio quei
    # due per far scattare storico_stati.py.
    stati = Base.metadata.tables["pratiche_stati"]
    chiave_stati = list(stati.primary_key)[0]
    db.execute(stati.delete().where(chiave_stati.in_([STATO_BOZZA, STATO_CARICATA])))
    db.execute(stati.insert().values(pratica_stato_id=STATO_BOZZA,
               pratica_stato_codice="Bozza", pratica_stato_descrizione="Bozza"))
    db.execute(stati.insert().values(pratica_stato_id=STATO_CARICATA,
               pratica_stato_codice="Caricata", pratica_stato_descrizione="Caricata"))
    percorso = ListinoTestaDB(listTesta_codice="TEST-STORICO", listTesta_descrizione="Percorso storico",
                              listino_tipo_id=900001, listino_tipoCorso_id=900001, nome_universita_id=900001)
    db.add(percorso)
    db.flush()
    db.commit()
    yield studente, percorso, intestazioni_account, intestazioni_nazionale
    db.execute(delete(PraticaStatoStorico))
    db.execute(delete(Pratica))
    db.delete(percorso)
    db.commit()


def crea(client, studente, percorso, intestazioni, *, stato_id=None):
    corpo = {"cliente_id": studente.cliente_id, "listTesta_id": percorso.listTesta_id, "nome_universita_id": 900001}
    if stato_id is not None:
        corpo["pratica_stato_id"] = stato_id  # per verificare che il server lo ignori comunque
    return client.post("/pratiche/", json=corpo, headers=intestazioni)


def storico(db, pratica_id):
    return db.query(PraticaStatoStorico).filter(PraticaStatoStorico.pratica_id == pratica_id).all()


def test_rinnovo_parziale_non_puo_aggiungere_un_secondo_anno(client, db, scenario):
    studente, percorso, account, _ = scenario
    pratica_id = crea(client, studente, percorso, account).json()["pratica_id"]
    primo, secondo, terzo = CAMPI_RINNOVO
    url = f"/pratiche/{pratica_id}"
    assert client.put(url, json={primo: True}, headers=account).status_code == 200
    risposta = client.put(url, json={secondo: True, "pratica_note": "Da non salvare"}, headers=account)
    assert risposta.status_code == 422
    db.rollback()
    persistita = db.get(Pratica, pratica_id)
    assert persistita.pratica_note != "Da non salvare"
    assert getattr(persistita, primo) == -1 and not getattr(persistita, secondo)
    risposta = client.put(url, json={primo: 0, secondo: -1, terzo: 0}, headers=account)
    assert risposta.status_code == 200 and risposta.json()[secondo] == -1
    assert client.put(url, json={secondo: None}, headers=account).json()[secondo] == 0


def test_rinnovo_storico_incoerente_consente_lettura_e_modifica_note(client, db, scenario):
    studente, percorso, account, _ = scenario
    pratica_id = crea(client, studente, percorso, account).json()["pratica_id"]
    prima = db.get(Pratica, pratica_id)
    prima.pratica_rinnPrimoAnno = prima.pratica_rinnSecondoAnno = -1
    db.commit()
    assert client.get(f"/pratiche/{pratica_id}", headers=account).status_code == 200
    risposta = client.put(f"/pratiche/{pratica_id}", json={"pratica_note": "Nota aggiornata"}, headers=account)
    assert risposta.status_code == 200 and risposta.json()["pratica_note"] == "Nota aggiornata"


@pytest.mark.parametrize("stati_intermedi", [(STATO_CARICATA,), (STATO_CARICATA, STATO_BOZZA)])
def test_snapshot_precedente_non_duplica_storico_o_email(client, db, mailer, scenario, stati_intermedi):
    studente, percorso, account, nazionale = scenario
    pratica_id = crea(client, studente, percorso, account).json()["pratica_id"]
    with Session(engine) as concorrente:
        assert concorrente.get(Pratica, pratica_id).pratica_stato_id == STATO_BOZZA
        assert len(storico(concorrente, pratica_id)) == 1
        for stato in stati_intermedi:
            risposta = client.put(f"/pratiche/{pratica_id}", json={"pratica_stato_id": stato}, headers=nazionale)
            assert risposta.status_code == 200, risposta.text
        attivita = BackgroundTasks()
        autore = db.get(Utente, studente.utente_id)
        aggiorna_pratica(pratica_id, PraticaUpdate(pratica_stato_id=STATO_CARICATA), attivita,
                        concorrente, Visibilita(autore.utente_id, nazionale=True), autore, mailer)
        assert attivita.tasks == []
    db.rollback()
    attesi = 1 + len(stati_intermedi) + int(stati_intermedi[-1] != STATO_CARICATA)
    assert len(storico(db, pratica_id)) == attesi


def test_spostamento_concorrente_rivaluta_visibilita_sotto_blocco(client, db, mailer, scenario):
    studente, percorso, account, nazionale = scenario
    pratica_id = crea(client, studente, percorso, account).json()["pratica_id"]
    altra_azienda = f.crea_azienda(db)
    autore = db.get(Utente, studente.utente_id)
    with Session(engine) as concorrente:
        prima = concorrente.get(Pratica, pratica_id)
        vis = Visibilita(autore.utente_id, nazionale=False, azienda_id=prima.azienda_id)
        risposta = client.put(f"/pratiche/{pratica_id}", json={"azienda_id": altra_azienda.azienda_id}, headers=nazionale)
        assert risposta.status_code == 200, risposta.text
        with pytest.raises(HTTPException) as errore:
            aggiorna_pratica(pratica_id, PraticaUpdate(pratica_note="Nota non autorizzata"),
                            BackgroundTasks(), concorrente, vis, autore, mailer)
        assert errore.value.status_code == 404
    db.rollback()
    assert db.get(Pratica, pratica_id).pratica_note != "Nota non autorizzata"


def test_pratica_nasce_sempre_in_bozza_anche_se_si_manda_un_altro_stato(client, db, mailer, scenario):
    studente, percorso, intestazioni_account, _ = scenario
    risposta = crea(client, studente, percorso, intestazioni_account, stato_id=STATO_CARICATA)
    assert risposta.status_code == 201, risposta.text
    pratica_id = risposta.json()["pratica_id"]
    assert risposta.json()["pratica_stato_id"] == STATO_BOZZA

    righe = storico(db, pratica_id)
    assert len(righe) == 1
    assert righe[0].pratica_stato_id == STATO_BOZZA

    assert len(mailer.inviate) == 1
    assert mailer.inviate[0]["To"] == studente.cliente_email


def test_chi_non_e_nazionale_non_puo_cambiare_stato(client, db, mailer, scenario):
    studente, percorso, intestazioni_account, _ = scenario
    pratica_id = crea(client, studente, percorso, intestazioni_account).json()["pratica_id"]
    mailer.svuota()

    risposta = client.put(f"/pratiche/{pratica_id}", json={"pratica_stato_id": STATO_CARICATA},
                           headers=intestazioni_account)
    assert risposta.status_code == 200, risposta.text
    assert risposta.json()["pratica_stato_id"] == STATO_BOZZA  # ignorato, non e' Nazionale

    assert mailer.inviate == []
    assert len(storico(db, pratica_id)) == 1  # solo quella della creazione


def test_nazionale_cambia_stato_e_manda_email_a_ersaf_una_sola_volta(client, db, mailer, scenario):
    studente, percorso, intestazioni_account, intestazioni_nazionale = scenario
    pratica_id = crea(client, studente, percorso, intestazioni_account).json()["pratica_id"]
    mailer.svuota()

    prima = client.put(f"/pratiche/{pratica_id}", json={"pratica_stato_id": STATO_CARICATA},
                        headers=intestazioni_nazionale)
    assert prima.status_code == 200, prima.text
    assert prima.json()["pratica_stato_id"] == STATO_CARICATA
    assert len(mailer.inviate) == 1
    assert mailer.inviate[0]["To"] == "info@ersaf.it"
    assert len(storico(db, pratica_id)) == 2

    # Torna in Bozza (gia' raggiunta alla creazione: niente seconda email al
    # cliente) e poi di nuovo in Caricata (gia' raggiunta poco fa: niente
    # seconda email a ERSAF). In entrambi i casi lo storico cresce comunque:
    # ogni cambio di stato lascia una riga, l'email e' solo la prima volta.
    mailer.svuota()
    client.put(f"/pratiche/{pratica_id}", json={"pratica_stato_id": STATO_BOZZA}, headers=intestazioni_nazionale)
    client.put(f"/pratiche/{pratica_id}", json={"pratica_stato_id": STATO_CARICATA}, headers=intestazioni_nazionale)
    assert mailer.inviate == []
    assert len(storico(db, pratica_id)) == 4
