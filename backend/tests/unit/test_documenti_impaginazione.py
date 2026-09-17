"""Impaginazione dei moduli a campi: valori piatti, campi vuoti, errori di programmazione."""

from __future__ import annotations

import pytest

from src.documenti import impaginazione as campi  # Testo importato da solo sembrerebbe una classe di test
from src.documenti.impaginazione import CENTRO, Casella, Firma, Griglia, Pagina, data, impagina, luogo_data_firma


def test_i_campi_vuoti_non_arrivano_al_modello_e_la_firma_si():
    pagina = Pagina("pagina-01.jpg", (
        campi.Testo("cognome", 48.1, 105.2, 70.8), campi.Testo("nome", 115.2, 176.4, 70.8),
        Casella("sesso.f", 193.2, 68.1, 2.2), Casella("sesso.m", 184.9, 68.1, 2.2),
        Griglia("codice_fiscale", 69.6, 164.25, 88.4, 16), Firma(131.06, 196.09, 265.85),
    ))
    valori = {"cognome": "Della Valle", "nome": "", "sesso.f": True, "sesso.m": False, "codice_fiscale": ""}
    assert impagina((pagina,), valori) == [{"sfondo": "pagina-01.jpg", "campi": [
        {"tipo": "testo", "x0": 48.1, "x1": 105.2, "y": 70.8, "allinea": "left", "testo": "Della Valle"},
        {"tipo": "casella", "x": 193.2, "y": 68.1, "lato": 2.2},
        {"tipo": "firma", "x0": 131.06, "x1": 196.09, "y": 265.85, "altezza": 12.0},
    ]}]


def test_la_griglia_porta_il_numero_di_caselle():
    campo = Griglia("codice_fiscale", 69.6, 164.25, 88.4, 16).campo({"codice_fiscale": "DLLMRA95M52F205Z"})
    assert campo == {"tipo": "griglia", "x0": 69.6, "x1": 164.25, "y": 88.4, "celle": 16, "testo": "DLLMRA95M52F205Z"}


@pytest.mark.parametrize(("campo", "valori", "errore"), [
    (campi.Testo("cognome", 10, 60, 50), {}, KeyError),
    (Casella("sesso.m", 10, 10, 2.2), {"sesso.m": "si"}, TypeError),
    (campi.Testo("voto", 10, 20, 50), {"voto": 28}, TypeError),
])
def test_una_chiave_mancante_o_di_tipo_sbagliato_e_un_errore(campo, valori, errore):
    with pytest.raises(errore):
        impagina((Pagina("pagina-01.jpg", (campo,)),), valori)


def test_date_su_tre_linee_e_riga_delle_firme():
    giorno, mese, anno = data("nascita", 82.13, (165.78, 173.57), (174.41, 182.2), (183.05, 195.07))
    assert (giorno.chiave, mese.chiave, anno.chiave) == ("nascita.gg", "nascita.mm", "nascita.aaaa")
    assert {giorno.allinea, mese.allinea, anno.allinea} == {CENTRO}
    luogo, quando, firma = luogo_data_firma(274.66, (23.88, 82.63), (91.44, 117.69), (131.06, 196.09), altezza=10.0)
    assert (luogo.chiave, quando.chiave, quando.allinea) == ("firma.luogo", "firma.data", CENTRO)
    assert firma == Firma(131.06, 196.09, 274.66, 10.0)
