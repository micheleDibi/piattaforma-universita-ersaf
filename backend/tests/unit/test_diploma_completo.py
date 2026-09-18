"""La regola "dati diploma completi", su oggetti in memoria: nessun database."""

from __future__ import annotations

import pytest

import src.main  # noqa: F401  registra tutti i mapper
from src.universita.models import CAMPI_DIPLOMA_NUMERO, CAMPI_DIPLOMA_TESTO, Universita

COMPLETO = {
    "universita_diploma": "Liceo scientifico",
    "universita_anno_scolastico": "2014/2015",
    "universita_istituto": "Liceo Volta",
    "universita_votoRicevuto_diploma": 80,
    "universita_votoMassimo_diploma": 100,
}


def curriculum(**modifiche):
    return Universita(**{**COMPLETO, **modifiche})


def test_con_tutti_i_campi_e_completo():
    assert curriculum().diploma_completo is True


def test_le_costanti_sono_i_cinque_campi_della_regola():
    assert set(CAMPI_DIPLOMA_TESTO) | set(CAMPI_DIPLOMA_NUMERO) == set(COMPLETO)


@pytest.mark.parametrize("campo", list(COMPLETO))
def test_un_campo_mancante_basta(campo):
    assert curriculum(**{campo: None}).diploma_completo is False


@pytest.mark.parametrize("campo", CAMPI_DIPLOMA_TESTO)
@pytest.mark.parametrize("vuoto", ["", "   ", "\t\n"])
def test_un_testo_vuoto_o_di_soli_spazi_basta(campo, vuoto):
    assert curriculum(**{campo: vuoto}).diploma_completo is False


@pytest.mark.parametrize("campo", CAMPI_DIPLOMA_NUMERO)
def test_un_voto_a_zero_conta_come_valorizzato(campo):
    assert curriculum(**{campo: 0}).diploma_completo is True


def test_via_citta_e_provincia_sono_facoltativi():
    riga = curriculum(universita_via_istituto=None, universita_citta_istituto="",
                      universita_provincia_istituto="  ")
    assert riga.diploma_completo is True
