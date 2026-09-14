"""Query e lookup reali su MariaDB locale, esclusivamente con dati sintetici."""
import pytest
from sqlalchemy import delete

from src.database import Base, engine
from src.pratiche.models import Pratica
from src.listini_testa.models import ListinoTestaDB
from src.security.password import hash_password
from tests.support import factories as f

pytestmark = pytest.mark.mariadb


@pytest.fixture
def scenario(client, db):
    Base.metadata.create_all(engine)
    db.execute(delete(Pratica))
    account = f.crea_attuatore(db, email="filtri@example.org", password_hash=hash_password("test-filtri"))
    studenti = [f.crea_cliente(db, utente_id=account.utente_id, email=f"s{n}@example.org",
                nome=nome, cognome="Ricerca", ruolo=0) for n, nome in enumerate(["Anna", "Bruno", "Carlo"])]
    for tabella, dati in {
        "listini_tipi": {"listino_tipo_codice": "TEST", "listino_tipo_descrizione": "Test"},
        "nome_universita": {"nome_universita_codice": "TEST", "nome_universita_descrizione": "Test"},
        "listini_tipicorsi": {"listino_tipoCorso_descrizione": "Test"},
        "pratiche_stati": {"pratica_stato_codice": "TEST", "pratica_stato_descrizione": "Test"},
    }.items():
        table = Base.metadata.tables[tabella]
        pk = list(table.primary_key)[0]
        db.execute(table.delete().where(pk.in_([900001, 900002])))
        for numero in (900001, 900002):
            db.execute(table.insert().values(**{pk.name: numero}, **dati))
    percorsi = [ListinoTestaDB(listTesta_codice=f"TEST-FILTRI-{n}", listTesta_descrizione=f"Percorso prova {n}",
                listino_tipo_id=900001, listino_tipoCorso_id=900001, nome_universita_id=900001) for n in range(3)]
    db.add_all(percorsi)
    db.flush()
    for n, (studente, stato, percorso) in enumerate([(0, 900001, 0), (1, 900001, 0), (0, 900002, 1), (1, 900002, 0)]):
        db.add(Pratica(pratica_numero=f"FILTRO-{n}", cliente_id=studenti[studente].cliente_id,
            cliente_emittente_aderente_id=account.cliente_id, pratica_stato_id=stato,
            listTesta_id=percorsi[percorso].listTesta_id, nome_universita_id=900001))
    db.commit()
    assert client.post("/auth/login", json={"utente_username": account.username, "utente_password": "test-filtri"}).status_code == 200
    yield studenti, percorsi
    db.execute(delete(Pratica))
    for percorso in percorsi:
        db.delete(percorso)
    db.commit()


def numeri(client, params):
    response = client.get("/pratiche/", params=params)
    assert response.status_code == 200, response.text
    return [r["pratica_numero"] for r in response.json()]


def test_filtri_combinati_or_studenti_and_stato_percorso_numero(client, scenario):
    studenti, percorsi = scenario
    params = [("studenti", s.cliente_id) for s in studenti[:2]] + [
        ("pratica_stato_id", 900001), ("percorso_id", percorsi[0].listTesta_id), ("search", "FILTRO")]
    assert numeri(client, params) == ["FILTRO-1", "FILTRO-0"]
    assert numeri(client, params + [("skip", 1), ("limit", 1)]) == ["FILTRO-0"]
    assert numeri(client, [("studenti", studenti[0].cliente_id)] * 2) == ["FILTRO-2", "FILTRO-0"]
    assert numeri(client, {"cliente_id": studenti[0].cliente_id}) == ["FILTRO-2", "FILTRO-0"]
    assert numeri(client, {"percorso_id": percorsi[2].listTesta_id}) == []


def test_lookup_ricerca_paginata_solo_anagrafiche_associate(client, scenario):
    studenti, percorsi = scenario
    prima = client.get("/pratiche/filtri/studenti", params={"search": "Ricerca", "limit": 1}).json()
    seconda = client.get("/pratiche/filtri/studenti", params={"search": "Ricerca", "limit": 1, "skip": 1}).json()
    assert prima["altri"] is True and seconda["altri"] is False
    assert [prima["elementi"][0]["id"], seconda["elementi"][0]["id"]] == [s.cliente_id for s in studenti[:2]]
    assert client.get("/pratiche/filtri/studenti?search=Ricerca Anna").json()["elementi"][0]["id"] == studenti[0].cliente_id
    assert client.get("/pratiche/filtri/studenti?search=Carlo").json()["elementi"] == []
    risultati = client.get("/pratiche/filtri/percorsi?search=TEST-FILTRI").json()["elementi"]
    assert {r["id"] for r in risultati} == {p.listTesta_id for p in percorsi[:2]}
    assert all(set(r) == {"id", "label", "dettaglio"} for r in risultati + prima["elementi"])
    assert client.get("/pratiche/filtri/stati").status_code == 200


@pytest.mark.parametrize("path", ["/pratiche/filtri/stati", "/pratiche/filtri/studenti", "/pratiche/filtri/percorsi"])
def test_lookup_protetti(client, path):
    assert client.get(path).status_code == 401


@pytest.mark.parametrize("query", ["studenti=-1", "percorso_id=0", "limit=201", "skip=-1", "pratica_stato_id=0"])
def test_parametri_invalidi(client, scenario, query):
    assert client.get(f"/pratiche/?{query}").status_code == 422
