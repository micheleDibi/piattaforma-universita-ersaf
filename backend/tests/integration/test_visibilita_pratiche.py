"""Le pratiche si vedono per azienda: D10-D13."""

from __future__ import annotations

import pytest

from src.clienti.models import Cliente
from src.pratiche.models import Pratica
from tests.support import factories as f
from tests.support.scenari import accedi, accedi_nazionale, riferimenti_pratiche

pytestmark = pytest.mark.mariadb

NON_TROVATA = {"detail": "Pratica non trovata."}
AZIENDA_MANCANTE = {"detail": "Per creare pratiche l'utente deve avere un'azienda associata."}
SOLO_NAZIONALE = {"detail": "Solo il nazionale può eseguire questa operazione."}


@pytest.fixture
def mondo(client, db, tabella_pratiche):
    """Due aziende, un Regionale nella prima, e pratiche di ogni tipo."""
    percorsi = riferimenti_pratiche(db)
    a, b = f.crea_azienda(db), f.crea_azienda(db)
    io, sessione = accedi(client, db, azienda_id=a.azienda_id)
    mio_studente = f.crea_attuatore(db, email="mio@example.org", padre=io.utente_id,
                                   ruolo=f.RUOLO_SOTTOSCRITTORE, nome="Mio")
    studente_altrui = f.crea_attuatore(db, email="altrui@example.org",
                                      ruolo=f.RUOLO_SOTTOSCRITTORE, nome="Altrui")
    studente_di_b = f.crea_attuatore(db, email="dib@example.org",
                                    ruolo=f.RUOLO_SOTTOSCRITTORE, nome="DiB")
    emittente = f.crea_attuatore(db, email="emittente@example.org", nome="Elena")

    def pratica(numero, studente, azienda, percorso=percorsi[0]):
        riga = Pratica(pratica_numero=numero, cliente_id=studente.cliente_id,
                       cliente_emittente_aderente_id=emittente.cliente_id,
                       listTesta_id=percorso.listTesta_id, pratica_stato_id=900001,
                       nome_universita_id=900001, listino_tipo_corso_id=900001,
                       azienda_id=azienda)
        db.add(riga)
        db.commit()
        return riga.pratica_id

    ids = {
        "a_altrui": pratica("A-1", studente_altrui, a.azienda_id),
        "a_mio": pratica("A-2", mio_studente, a.azienda_id),
        "b": pratica("B-1", studente_di_b, b.azienda_id, percorsi[1]),
        "nulla": pratica("N-1", studente_di_b, None, percorsi[1]),
    }
    yield {
        "a": a.azienda_id, "b": b.azienda_id, "io": io, "sessione": sessione,
        "mio_studente": mio_studente, "studente_altrui": studente_altrui,
        "studente_di_b": studente_di_b, "emittente": emittente,
        "percorsi": percorsi, "ids": ids,
    }
    db.query(Pratica).delete()
    for percorso in percorsi:
        db.delete(percorso)
    db.commit()


def _corpo(m, **extra):
    return {
        "pratica_numero": "NUOVA", "cliente_id": m["studente_altrui"].cliente_id,
        "cliente_emittente_aderente_id": m["emittente"].cliente_id,
        "listTesta_id": m["percorsi"][0].listTesta_id, "pratica_stato_id": 900001,
        "nome_universita_id": 900001, "listino_tipo_corso_id": 900001, **extra,
    }


def _azienda(db, pratica_id):
    db.expire_all()
    return db.get(Pratica, pratica_id).azienda_id


# =============================================================================
# D10: lettura
# =============================================================================
def test_l_elenco_contiene_solo_la_propria_azienda(client, mondo):
    risposta = client.get("/pratiche/?limit=200", headers=mondo["sessione"])
    assert risposta.status_code == 200, risposta.text
    assert {r["pratica_id"] for r in risposta.json()} == {mondo["ids"]["a_altrui"], mondo["ids"]["a_mio"]}


def test_la_scheda_di_un_altra_azienda_come_inesistente(client, mondo):
    sessione, ids = mondo["sessione"], mondo["ids"]
    inesistente = client.get("/pratiche/999999", headers=sessione)
    assert (inesistente.status_code, inesistente.json()) == (404, NON_TROVATA)
    for nascosta in (ids["b"], ids["nulla"]):
        risposta = client.get(f"/pratiche/{nascosta}", headers=sessione)
        assert (risposta.status_code, risposta.json()) == (404, NON_TROVATA)
    assert client.get(f"/pratiche/{ids['a_altrui']}", headers=sessione).status_code == 200


def test_la_modifica_di_un_altra_azienda_non_tocca_nulla(client, db, mondo):
    pratica_id = mondo["ids"]["b"]
    risposta = client.put(f"/pratiche/{pratica_id}", json={"pratica_numero": "RUBATA"},
                          headers=mondo["sessione"])
    assert (risposta.status_code, risposta.json()) == (404, NON_TROVATA)
    db.expire_all()
    assert db.get(Pratica, pratica_id).pratica_numero == "B-1"


def test_i_filtri_propongono_solo_studenti_e_percorsi_visibili(client, mondo):
    sessione = mondo["sessione"]
    studenti = client.get("/pratiche/filtri/studenti?limit=50", headers=sessione).json()
    assert {e["id"] for e in studenti["elementi"]} == {
        mondo["mio_studente"].cliente_id, mondo["studente_altrui"].cliente_id,
    }
    assert studenti["altri"] is False
    prima = client.get("/pratiche/filtri/studenti?limit=1", headers=sessione).json()
    assert prima["altri"] is True

    percorsi = client.get("/pratiche/filtri/percorsi?search=TEST-VIS", headers=sessione).json()
    assert {e["id"] for e in percorsi["elementi"]} == {mondo["percorsi"][0].listTesta_id}


def test_senza_azienda_niente_pratiche(client, db, mondo):
    _, sessione = accedi(client, db)
    assert client.get("/pratiche/", headers=sessione).json() == []
    risposta = client.get(f"/pratiche/{mondo['ids']['a_mio']}", headers=sessione)
    assert (risposta.status_code, risposta.json()) == (404, NON_TROVATA)
    assert client.get("/pratiche/filtri/studenti", headers=sessione).json()["elementi"] == []

    prima = db.query(Pratica).count()
    risposta = client.post("/pratiche/", json=_corpo(mondo), headers=sessione)
    assert (risposta.status_code, risposta.json()) == (403, AZIENDA_MANCANTE)
    assert db.query(Pratica).count() == prima


# =============================================================================
# D11 e D12: scrittura
# =============================================================================
def test_la_creazione_usa_sempre_la_propria_azienda(client, db, mondo):
    sessione = mondo["sessione"]
    altrui = client.post("/pratiche/", json=_corpo(mondo, azienda_id=mondo["b"]), headers=sessione)
    senza = client.post("/pratiche/", json=_corpo(mondo, pratica_numero="NUOVA-2"), headers=sessione)
    assert altrui.status_code == senza.status_code == 201, (altrui.text, senza.text)
    assert _azienda(db, altrui.json()["pratica_id"]) == mondo["a"]
    assert _azienda(db, senza.json()["pratica_id"]) == mondo["a"]


def test_la_modifica_ignora_l_azienda(client, db, mondo):
    pratica_id = mondo["ids"]["a_mio"]
    risposta = client.put(f"/pratiche/{pratica_id}",
                          json={"azienda_id": mondo["b"], "pratica_numero": "A-2-bis"},
                          headers=mondo["sessione"])
    assert risposta.status_code == 200, risposta.text
    assert risposta.json()["pratica_numero"] == "A-2-bis"
    assert _azienda(db, pratica_id) == mondo["a"]


def test_studente_ed_emittente_non_visibili_sono_ammessi(client, mondo):
    """D12: nessun controllo di visibilita' su chi compare nella pratica."""
    corpo = _corpo(mondo, cliente_id=mondo["studente_di_b"].cliente_id)
    risposta = client.post("/pratiche/", json=corpo, headers=mondo["sessione"])
    assert risposta.status_code == 201, risposta.text


def test_il_nazionale_non_ha_limiti(client, db, mailer, mondo):
    _, sessione = accedi_nazionale(client, db, mailer)
    elenco = client.get("/pratiche/?limit=200", headers=sessione).json()
    assert {r["pratica_id"] for r in elenco} == set(mondo["ids"].values())

    in_b = client.post("/pratiche/", json=_corpo(mondo, azienda_id=mondo["b"]), headers=sessione)
    senza = client.post("/pratiche/", json=_corpo(mondo, pratica_numero="N-2"), headers=sessione)
    assert _azienda(db, in_b.json()["pratica_id"]) == mondo["b"]
    assert _azienda(db, senza.json()["pratica_id"]) is None

    spostata = client.put(f"/pratiche/{mondo['ids']['a_mio']}", json={"azienda_id": mondo["b"]}, headers=sessione)
    assert spostata.status_code == 200, spostata.text
    assert _azienda(db, mondo["ids"]["a_mio"]) == mondo["b"]


# =============================================================================
# D13: l'emittente nella risposta
# =============================================================================
def test_l_emittente_arriva_con_la_pratica_anche_se_non_visibile(client, db, mondo):
    from src.clienti.models import Cliente

    sessione, pratica_id = mondo["sessione"], mondo["ids"]["a_altrui"]
    emittente = db.get(Cliente, mondo["emittente"].cliente_id)
    atteso = {"cliente_id": emittente.cliente_id, "cliente_nome": emittente.cliente_nome,
              "cliente_cognome": emittente.cliente_cognome, "cliente_codice": emittente.cliente_codice}
    # L'emittente non e' fra i clienti che il Regionale vede.
    assert client.get(f"/clienti/{emittente.cliente_id}", headers=sessione).status_code == 404

    scheda = client.get(f"/pratiche/{pratica_id}", headers=sessione).json()
    elenco = client.get("/pratiche/", headers=sessione).json()
    creata = client.post("/pratiche/", json=_corpo(mondo), headers=sessione).json()
    modificata = client.put(f"/pratiche/{pratica_id}", json={"pratica_numero": "A-1-bis"}, headers=sessione).json()

    for risposta in [scheda, creata, modificata, *elenco]:
        assert risposta["emittente"] == atteso
    # cliente_id di primo livello resta lo studente.
    assert scheda["cliente_id"] == mondo["studente_altrui"].cliente_id


def test_l_elenco_non_fa_una_query_per_riga(client, db, mondo, spia_sql):
    """Con il joinedload dell'emittente il numero di statement non dipende dal
    numero di pratiche."""
    sessione = mondo["sessione"]
    spia_sql.clear()
    client.get("/pratiche/?limit=40", headers=sessione)
    con_due = len(spia_sql)

    # Un emittente diverso per pratica: con lo stesso, l'identity map
    # servirebbe le righe successive senza query e il test non vedrebbe nulla.
    for n in range(30):
        emittente = f.crea_cliente(db, utente_id=mondo["emittente"].utente_id, email=f"em{n}@example.org")
        db.add(Pratica(pratica_numero=f"A-X{n}", cliente_id=mondo["studente_altrui"].cliente_id,
                       cliente_emittente_aderente_id=emittente.cliente_id,
                       listTesta_id=mondo["percorsi"][0].listTesta_id, pratica_stato_id=900001,
                       nome_universita_id=900001, azienda_id=mondo["a"]))
    db.commit()
    spia_sql.clear()
    assert len(client.get("/pratiche/?limit=40", headers=sessione).json()) == 32
    assert len(spia_sql) == con_due


def test_la_propria_azienda_non_si_riscrive(client, db, mondo):
    """Cambiare `azienda_id` sulla propria riga sposterebbe la visibilita'.

    La riga "me" e' sempre visibile per costruzione, quindi il controllo sulla
    visibilita' la lascia passare: senza un controllo sul campo, un PUT con il
    solo azienda_id dava le pratiche dell'azienda scelta, e con esse nuovi
    colleghi da cui partire per i clienti. E' la stessa scalata che la regola
    sul ruolo chiude, sull'altro campo che la regola legge.
    """
    io, sessione, ids = mondo["io"], mondo["sessione"], mondo["ids"]

    risposta = client.put(f"/clienti/{io.cliente_id}",
                          json={"azienda_id": mondo["b"]}, headers=sessione)
    assert (risposta.status_code, risposta.json()) == (403, SOLO_NAZIONALE)

    db.expire_all()
    assert db.get(Cliente, io.cliente_id).azienda_id == mondo["a"]
    elenco = client.get("/pratiche/?limit=200", headers=sessione)
    assert {r["pratica_id"] for r in elenco.json()} == {ids["a_altrui"], ids["a_mio"]}


def test_la_propria_azienda_si_puo_rimandare_uguale(client, mondo):
    """La scheda rimanda tutti i campi a ogni salvataggio."""
    risposta = client.put(f"/clienti/{mondo['io'].cliente_id}",
                          json={"azienda_id": mondo["a"]}, headers=mondo["sessione"])
    assert risposta.status_code == 200, risposta.text


def test_l_azienda_di_un_altro_visibile_resta_modificabile(client, db, mondo):
    """Il divieto riguarda solo la propria riga: associare un'azienda a un
    attuatore che si vede e' il flusso della scheda Azienda."""
    altro = mondo["mio_studente"]
    risposta = client.put(f"/clienti/{altro.cliente_id}",
                          json={"azienda_id": mondo["b"]}, headers=mondo["sessione"])
    assert risposta.status_code == 200, risposta.text
    db.expire_all()
    assert db.get(Cliente, altro.cliente_id).azienda_id == mondo["b"]
