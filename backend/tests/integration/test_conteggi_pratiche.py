"""I conteggi della pagina Pratiche: gruppi per universita', tipo e stato."""

from __future__ import annotations

import pytest

from src.pratiche.models import Pratica
from tests.support import factories as f
from tests.support.scenari import accedi, accedi_nazionale, riferimenti_pratiche

pytestmark = pytest.mark.mariadb

U1, U2 = 900001, 900002
T1, T2 = 900001, 900002
S1, S2 = 900001, 900002


def _gruppo(universita, tipo_corso, stato, totale):
    return {"nome_universita_id": universita, "listino_tipo_corso_id": tipo_corso,
            "pratica_stato_id": stato, "totale": totale}


@pytest.fixture
def mondo(client, db, tabella_pratiche):
    """Pratiche in due aziende e una senza, con un Regionale nella prima."""
    percorsi = riferimenti_pratiche(db)
    a, b = f.crea_azienda(db), f.crea_azienda(db)
    _, sessione = accedi(client, db, azienda_id=a.azienda_id)
    studente = f.crea_attuatore(db, email="studente@example.org", ruolo=f.RUOLO_SOTTOSCRITTORE)
    emittente = f.crea_attuatore(db, email="emittente@example.org")

    righe = [
        # (azienda, universita', tipo di corso, stato)
        (a.azienda_id, U1, T1, S1), (a.azienda_id, U1, T1, S1), (a.azienda_id, U1, T2, S1),
        (a.azienda_id, U2, None, S2),
        (b.azienda_id, U1, T1, S1), (b.azienda_id, U2, T2, S2),
        (None, U2, T1, S2),
    ]
    for n, (azienda, universita, tipo_corso, stato) in enumerate(righe):
        db.add(Pratica(pratica_numero=f"C-{n}", cliente_id=studente.cliente_id,
                       cliente_emittente_aderente_id=emittente.cliente_id,
                       listTesta_id=percorsi[0].listTesta_id, pratica_stato_id=stato,
                       nome_universita_id=universita, listino_tipo_corso_id=tipo_corso,
                       azienda_id=azienda))
    db.commit()
    yield {"sessione": sessione}
    db.query(Pratica).delete()
    for percorso in percorsi:
        db.delete(percorso)
    db.commit()


def test_il_regionale_conta_solo_la_propria_azienda(client, mondo):
    risposta = client.get("/pratiche/conteggi", headers=mondo["sessione"])
    assert risposta.status_code == 200, risposta.text
    # Il tipo di corso mancante resta un gruppo a se', e viene prima (NULL).
    assert risposta.json() == [
        _gruppo(U1, T1, S1, 2), _gruppo(U1, T2, S1, 1), _gruppo(U2, None, S2, 1),
    ]


def test_i_conteggi_corrispondono_all_elenco(client, mondo):
    sessione = mondo["sessione"]
    for gruppo in client.get("/pratiche/conteggi", headers=sessione).json():
        parametri = {"limit": 200, "nome_universita_id": gruppo["nome_universita_id"],
                     "pratica_stato_id": gruppo["pratica_stato_id"]}
        if gruppo["listino_tipo_corso_id"] is not None:
            parametri["listino_tipo_corso_id"] = gruppo["listino_tipo_corso_id"]
        elenco = client.get("/pratiche/", params=parametri, headers=sessione).json()
        if gruppo["listino_tipo_corso_id"] is None:
            elenco = [p for p in elenco if p["listino_tipo_corso_id"] is None]
        assert len(elenco) == gruppo["totale"], gruppo


def test_senza_azienda_nessun_conteggio(client, db, mondo):
    _, sessione = accedi(client, db)
    risposta = client.get("/pratiche/conteggi", headers=sessione)
    assert (risposta.status_code, risposta.json()) == (200, [])


def test_il_nazionale_conta_tutto(client, db, mailer, mondo):
    _, sessione = accedi_nazionale(client, db, mailer)
    risposta = client.get("/pratiche/conteggi", headers=sessione)
    assert risposta.status_code == 200, risposta.text
    assert risposta.json() == [
        _gruppo(U1, T1, S1, 3), _gruppo(U1, T2, S1, 1),
        _gruppo(U2, None, S2, 1), _gruppo(U2, T1, S2, 1), _gruppo(U2, T2, S2, 1),
    ]


def test_una_sola_query_di_conteggio(client, mondo, spia_sql):
    spia_sql.clear()
    client.get("/pratiche/conteggi", headers=mondo["sessione"])
    sulle_pratiche = [s for s in spia_sql if "FROM pratiche" in s]
    assert len(sulle_pratiche) == 1
    assert "GROUP BY" in sulle_pratiche[0] and "count(" in sulle_pratiche[0]
