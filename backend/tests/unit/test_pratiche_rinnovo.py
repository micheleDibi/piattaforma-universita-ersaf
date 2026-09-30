"""Rinnovo primo/secondo/terzo anno su PraticaUpdate: normalizzazione legacy
(vedi src/comune/flag_legacy.py) e la regola "un solo anno alla volta" (vedi
CAMPI_RINNOVO in src/pratiche/models.py). Solo PraticaUpdate: PraticaBase (e
quindi PraticaResponse) non porta il controllo di mutua esclusione, per non
rischiare di bloccare la lettura di una pratica con un dato storico
incoerente su questi campi."""
import pytest
from pydantic import ValidationError

from src.pratiche.models import PraticaUpdate

CAMPI = ("pratica_rinnPrimoAnno", "pratica_rinnSecondoAnno", "pratica_rinnTerzoAnno")


def test_nessun_anno_selezionato_e_valido():
    aggiornamento = PraticaUpdate(**{campo: 0 for campo in CAMPI})
    assert all(getattr(aggiornamento, campo) == 0 for campo in CAMPI)


@pytest.mark.parametrize("ingresso", [True, 1, -1, "1", "-1", "true"])
def test_un_solo_anno_si_normalizza_a_meno_uno(ingresso):
    aggiornamento = PraticaUpdate(pratica_rinnSecondoAnno=ingresso)
    assert aggiornamento.pratica_rinnSecondoAnno == -1
    assert aggiornamento.pratica_rinnPrimoAnno is None
    assert aggiornamento.pratica_rinnTerzoAnno is None


def test_due_anni_insieme_vengono_rifiutati():
    with pytest.raises(ValidationError):
        PraticaUpdate(pratica_rinnPrimoAnno=-1, pratica_rinnSecondoAnno=-1)


def test_tre_anni_insieme_vengono_rifiutati():
    with pytest.raises(ValidationError):
        PraticaUpdate(pratica_rinnPrimoAnno=1, pratica_rinnSecondoAnno=1, pratica_rinnTerzoAnno=1)
