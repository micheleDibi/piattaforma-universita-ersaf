"""Accordo eCampus: inclusione per ente, capienza e conservazione di tutte le rate."""

import pytest

from src.documenti.ecampus.rateizzazione import pagine_rateizzazione
from src.documenti.modelli import ECAMPUS, MODELLI
from src.documenti.motore import componi_pdf
from tests.unit.test_documenti_ecampus import dati_pratica


def con_rate(numero):
    dati = dati_pratica()
    dati["rateizzazione"] = [
        {"importo": f"{100 + i},25", "data": f"{i % 28 + 1:02d}/10/2026"} for i in range(numero)
    ]
    return dati


@pytest.mark.parametrize("modello", {m.nome: m for m in MODELLI}.values(), ids=lambda m: m.nome)
def test_accordo_solo_per_ecampus_con_rate(modello):
    senza = modello.compila(dati_pratica())
    con = modello.compila(con_rate(12))
    assert len(con["pagine"]) == len(senza["pagine"]) + (modello.ente == ECAMPUS)
    if modello.ente == ECAMPUS:
        assert con["pagine"][-1]["sfondo"].endswith("ecampus-rateizzazione.jpg")
        assert b"pdfaid" in componi_pdf(modello.nome, con)


@pytest.mark.parametrize("numero,pagine", [(0, 0), (1, 1), (12, 1), (13, 2), (28, 2), (37, 3), (61, 4)])
def test_nessuna_rata_tagliata_oltre_la_capienza(numero, pagine):
    dati = con_rate(numero)
    compilate = pagine_rateizzazione(dati)
    assert len(compilate) == pagine
    testi = [campo["testo"] for p in compilate for campo in p["campi"] if campo["tipo"] == "testo"]
    for rata in dati["rateizzazione"]:
        assert testi.count(rata["importo"]) == 1
    for pagina in compilate:
        for campo in pagina["campi"]:
            assert 0 < campo["x0"] < campo["x1"] < 210 and 0 < campo["y"] < 297


def test_colonne_dispari_e_pari_e_dati_mancanti_senza_valori_inventati():
    dati = con_rate(3)
    dati["rateizzazione"][2] = {"importo": "0,00", "data": ""}
    campi = pagine_rateizzazione(dati)[0]["campi"]
    sinistra = next(c for c in campi if c.get("testo") == "100,25")
    destra = next(c for c in campi if c.get("testo") == "101,25")
    terza = next(c for c in campi if c.get("testo") == "0,00")
    assert sinistra["y"] == destra["y"] and sinistra["x0"] < destra["x0"]
    assert terza["x0"] == sinistra["x0"] and terza["y"] > sinistra["y"]
    assert not any(c.get("testo") == "03/10/2026" for c in campi)
