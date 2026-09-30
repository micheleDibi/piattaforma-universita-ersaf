"""Generazione del codice pratica: solo la parte senza database (vedi
tests/integration per prossimo_numero/genera_codici_pratica con MariaDB)."""

from __future__ import annotations

import pytest

from src.errori import CodicePraticaError
from src.pratiche.codice import (
    formatta_codice,
    genera_codici_pratica,
    prefisso_pratica,
    prefisso_tipo_corso,
)


def test_prefisso_per_tipo_corso_noto():
    assert prefisso_tipo_corso(1) == "MT"  # Master
    assert prefisso_tipo_corso(2) == "MT"  # Master area scuola
    assert prefisso_tipo_corso(3) == "MT"  # Master classi di concorso
    assert prefisso_tipo_corso(4) == "CP"  # Corsi di perfezionamento
    assert prefisso_tipo_corso(10) == "CP"  # Corsi speciali
    assert prefisso_tipo_corso(6) == "AF"  # Corsi di formazione
    assert prefisso_tipo_corso(7) == "AF"  # Corsi di alta formazione
    assert prefisso_tipo_corso(8) == "CL"  # Lauree
    assert prefisso_tipo_corso(9) == "CS"  # Corsi singoli


def test_prefisso_tipo_corso_sconosciuto_o_mancante_blocca():
    # 5 = Percorso docenti: nessun prefisso previsto, come nell'originale.
    for valore in (5, None, 999):
        with pytest.raises(CodicePraticaError):
            prefisso_tipo_corso(valore)


def test_prefisso_pratica_aggiunge_a4u_solo_per_quell_universita():
    assert prefisso_pratica("A4U", 1) == "A4U_MT"
    assert prefisso_pratica("SSML", 1) == "MT"


def test_formatta_codice_a_sei_cifre_zero_padded():
    assert formatta_codice("MT", 42) == "MT000042"
    assert formatta_codice("A4U_CP", 7) == "A4U_CP000007"


def test_formatta_codice_fuori_range_blocca():
    for numero in (0, -1, 1_000_000):
        with pytest.raises(CodicePraticaError):
            formatta_codice("MT", numero)


def test_genera_codici_pratica_nessuna_codifica_per_altre_universita():
    # Nessuna query al database: deve uscire prima di usare la Session.
    assert genera_codici_pratica(
        None, nome_universita_codice="ECAMPUS", listino_tipo_corso_id=1
    ) is None
    assert genera_codici_pratica(
        None, nome_universita_codice=None, listino_tipo_corso_id=1
    ) is None
