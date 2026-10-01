"""I corsi di una pratica Corsi Singoli nella risposta del dettaglio."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace as N

from src.pratiche.schemi import _corso_pratica, _dettaglio_alla_data


def dettaglio(inizio, fine, cfu):
    return N(listDettaglio_dataInizioValidazione=inizio,
             listDettaglio_dataFineValidazionoe=fine, listDettaglio_CFU=cfu)


VECCHIO = dettaglio(date(2024, 1, 1), date(2025, 6, 30), 6)
NUOVO = dettaglio(date(2025, 7, 1), date(9999, 12, 31), 9)


def test_dettaglio_valido_alla_data_della_pratica():
    assert _dettaglio_alla_data([VECCHIO, NUOVO], date(2025, 3, 1)) is VECCHIO
    assert _dettaglio_alla_data([VECCHIO, NUOVO], date(2026, 3, 1)) is NUOVO
    assert _dettaglio_alla_data([VECCHIO], date(2026, 3, 1)) is None
    assert _dettaglio_alla_data([], date(2026, 3, 1)) is None


def test_corso_con_codice_cfu_corso_di_laurea_e_prezzo_salvato():
    listino = N(listTesta_codice="SECS-P/01", listTesta_descrizione="MACROECONOMIA",
                dettagli=[VECCHIO, NUOVO],
                corso_laurea=N(listino_corsoLaurea_descrizione="Economia aziendale"))
    riga = N(listTesta_id=7, listino=listino, pratica_listini_prezzo=Decimal("360.00"))
    assert _corso_pratica(riga, date(2025, 3, 1)) == {
        "listTesta_id": 7, "codice": "SECS-P/01", "descrizione": "MACROECONOMIA",
        "prezzo": Decimal("360.00"), "cfu": 6, "corso_laurea": "Economia aziendale",
    }


def test_senza_dettaglio_alla_data_si_usa_quello_di_oggi():
    listino = N(listTesta_codice="X", listTesta_descrizione="Y", dettagli=[NUOVO], corso_laurea=None)
    riga = N(listTesta_id=1, listino=listino, pratica_listini_prezzo=None)
    corso = _corso_pratica(riga, date(2020, 1, 1))
    assert corso["cfu"] == 9
    assert corso["corso_laurea"] is None
