import pytest

from src.documenti.dati import dati_pratica
from src.documenti.firma import immagine_firma
from src.pratiche.firma import normalizza_firma
from src.security.browser import nome_cookie, token_csrf
from tests.integration.test_documento_pratica import pratica  # noqa: F401 fixture
from tests.unit.test_firma_acquisizione import disegno

pytestmark = pytest.mark.mariadb


def test_salva_con_versione_e_il_pdf_legge_la_stessa_firma(client, db, pratica):
    url = f"/pratiche/{pratica.pratica_id}/firma"
    prima = client.get(url).json()
    headers = {"X-CSRF-Token": token_csrf(client.cookies.get(nome_cookie()))}
    payload = {"immagine": disegno(), "versione": prima["versione"]}
    assert client.put(url, json=payload).status_code == 403
    risultato = client.put(url, json=payload, headers=headers)
    assert risultato.status_code == 200, risultato.text
    assert risultato.headers["cache-control"] == "no-store"
    assert risultato.json()["versione"] != prima["versione"]
    db.refresh(pratica)
    assert pratica.pratica_firma == normalizza_firma(disegno())
    assert pratica.pratica_missFlag_firma == 0
    # Stesso percorso utilizzato dal generatore: nessuna tabella firma parallela.
    _, immagini = dati_pratica(db, pratica)
    assert immagine_firma(pratica.pratica_firma) in immagini.values()
    assert client.put(url, json=payload, headers=headers).status_code == 409
    assert client.get(url).json() == risultato.json()


def test_firma_fuori_azienda_non_esposta(client, db, pratica):
    pratica.azienda_id = None
    db.commit()
    url = f"/pratiche/{pratica.pratica_id}/firma"
    assert client.get(url).status_code == 404
    headers = {"X-CSRF-Token": token_csrf(client.cookies.get(nome_cookie()))}
    assert client.put(url, json={"immagine": disegno(), "versione": "0" * 64}, headers=headers).status_code == 404
    client.cookies.clear()
    assert client.get(url).status_code == 401
