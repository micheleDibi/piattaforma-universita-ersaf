"""Salvataggio delle percentuali di un'azienda: un valore sopra quello
dell'azienda padre e' un errore (vedi superamenti_padre e PUT
/aziende/{id}/dettagli), non piu' un azzeramento da confermare. Il database
non serve: si sostituiscono le due letture da cui dipende."""
import pytest

from src.aziende_xcod import servizi
from src.aziende_xcod.servizi import CAMPI_PERCENTUALI, superamenti_padre

PADRE = {campo: 10 for campo in CAMPI_PERCENTUALI}


@pytest.fixture
def con_padre(monkeypatch):
    monkeypatch.setattr(servizi, "padre_id_di", lambda db, azienda_id: 7)
    monkeypatch.setattr(servizi, "valori_percentuali_di", lambda db, azienda_id: dict(PADRE))


def test_uguale_al_padre_non_e_un_superamento(con_padre):
    assert superamenti_padre(None, 5, dict(PADRE)) == []


def test_sopra_il_padre_indica_campo_valore_e_limite(con_padre):
    valori = dict(PADRE, universita_ecampus_lauree=11, universita_A4U_master=30)
    assert superamenti_padre(None, 5, valori) == [
        {"campo": "universita_ecampus_lauree", "valore": 11, "limite": 10},
        {"campo": "universita_A4U_master", "valore": 30, "limite": 10},
    ]


def test_azienda_radice_non_ha_limiti(monkeypatch):
    monkeypatch.setattr(servizi, "padre_id_di", lambda db, azienda_id: None)
    assert superamenti_padre(None, 5, {campo: 100 for campo in CAMPI_PERCENTUALI}) == []
