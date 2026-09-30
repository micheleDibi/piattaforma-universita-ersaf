"""Contratti dei rinnovi: un solo anno e lettura tollerante dei dati legacy."""

import pytest
from pydantic import ValidationError

from src.pratiche.rinnovi import CAMPI_RINNOVO
from src.pratiche.schemi import PraticaCreate, PraticaResponse, PraticaUpdate


@pytest.mark.parametrize("modello", [PraticaCreate, PraticaUpdate])
@pytest.mark.parametrize("valore", [True, 1, -1, "true", "-1"])
def test_flag_veri_normalizzati_e_scelte_multiple_rifiutate(modello, valore):
    scelta = modello(**{CAMPI_RINNOVO[0]: valore})
    assert getattr(scelta, CAMPI_RINNOVO[0]) == -1
    with pytest.raises(ValidationError, match="Solo un anno"):
        modello(**{CAMPI_RINNOVO[0]: valore, CAMPI_RINNOVO[1]: valore})


def test_lettura_storica_non_rifiuta_due_flag_veri():
    risposta = PraticaResponse(pratica_id=1, **{CAMPI_RINNOVO[0]: 1, CAMPI_RINNOVO[1]: -1})
    assert getattr(risposta, CAMPI_RINNOVO[0]) == -1
    assert getattr(risposta, CAMPI_RINNOVO[1]) == -1


def test_update_non_inventa_campi_non_inviati():
    assert PraticaUpdate(pratica_note="Nota").model_dump(exclude_unset=True) == {"pratica_note": "Nota"}
    assert PraticaUpdate(**{CAMPI_RINNOVO[0]: None}).model_dump(exclude_unset=True) == {CAMPI_RINNOVO[0]: 0}
