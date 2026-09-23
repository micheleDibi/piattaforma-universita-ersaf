"""Copertura dei moduli originali e conservazione dei dati nella composizione."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from src.documenti import motore
from src.documenti.impaginazione import Casella
from src.documenti.modelli import ECAMPUS, LINK, MODELLI, SSML, modello_per
from src.documenti.moduli import compila, pagine_modulo
from src.documenti.valori_moduli import valori_modulo
from tests.support.immagini import png_pieno
from tests.unit.test_documenti_ecampus import dati_pratica

PAGINE = {
    "ecampus-laurea": 10, "ecampus-master": 5, "ecampus-perfezionamento": 4,
    "ecampus-formazione": 4, "ecampus-singoli": 4, "ssml-laurea": 10,
    "ssml-master": 5, "ssml-perfezionamento": 4, "ssml-formazione": 4,
    "ssml-singoli": 4, "link-perfezionamento": 3, "link-singoli": 3, "a4u-perfezionamento": 3,
}
MODULI = {m.nome: m for m in MODELLI}


def pratica_catalogo(ente, tipo):
    return SimpleNamespace(listino_testa=SimpleNamespace(
        universita=SimpleNamespace(nome_universita_descrizione=ente),
        tipo_corso=SimpleNamespace(listino_tipoCorso_descrizione=tipo)))


def test_registro_univoco_e_copertura_fonti():
    assert set(MODULI) == set(PAGINE)
    for modello in MODELLI:
        corrispondenti = [m for m in MODELLI if m.si_applica(modello.ente, modello.tipo_corso)]
        assert corrispondenti == [modello]
        assert modello_per(pratica_catalogo(modello.ente.upper(), modello.tipo_corso.lower())) == modello


@pytest.mark.parametrize("ente,tipo", [
    (ECAMPUS, "Percorso docenti"), (ECAMPUS, "CORSI SPECIALI"),
    ("Avatar4University", "MASTER"), (LINK[0], "LAUREE"), ("Altro ateneo", "MASTER"), (ECAMPUS, ""),
])
def test_nessun_modulo_inventato_per_tipi_senza_originale(ente, tipo):
    assert modello_per(pratica_catalogo(ente, tipo)) is None


@pytest.mark.parametrize("nome", PAGINE)
def test_tutti_i_moduli_compongono_pdf_a_anche_senza_scheda_universitaria(nome):
    dati = MODULI[nome].arricchisci(dati_pratica(generalita={}))
    pdf = motore.componi_pdf(nome, dati, {"firma": png_pieno()})
    assert pdf.startswith(b"%PDF-") and b"pdfaid" in pdf
    assert f"/Count {PAGINE[nome]}".encode() in pdf
    assert len(dati["pagine"]) == PAGINE[nome]


@pytest.mark.parametrize("nome", [n for n in PAGINE if n != "ecampus-laurea"])
def test_layout_validi_e_sfondi_presenti(nome):
    for pagina in pagine_modulo(nome):
        radice = motore.CARTELLA_MODELLI if pagina.sfondo.startswith("_comune/") else motore.CARTELLA_MODELLI / nome
        assert (radice / pagina.sfondo).is_file()
        for campo in pagina.campi:
            if isinstance(campo, Casella):
                assert 0 < campo.x < campo.x + campo.lato < 210
                assert 0 < campo.y < campo.y + campo.lato < 297
            else:
                assert 0 < campo.x0 < campo.x1 < 210 and 0 < campo.y < 297


@pytest.mark.parametrize("nome,aggiuntive", [("ecampus-singoli", 1), ("link-singoli", 1), ("ssml-singoli", 0)])
def test_sei_insegnamenti_richiesti_non_si_perdono_e_non_sono_gli_esami_sostenuti(nome, aggiuntive):
    dati = dati_pratica(esami=[{"insegnamento": "Esame gia sostenuto", "universita": "Ateneo di prova", "cfu": "6"}])
    dati["corsi_richiesti"] = [{"descrizione": f"Richiesto {i}", "corso_laurea": "Laurea di prova"} for i in range(6)]
    compilato = compila(nome, dati)
    assert len(compilato["pagine"]) == PAGINE[nome] + aggiuntive
    testi = [c["testo"] for p in compilato["pagine"] for c in p["campi"] if c["tipo"] == "testo"]
    assert all(testi.count(f"Richiesto {i}") == 1 for i in range(6))
    if nome == "ssml-singoli":
        assert "6" in testi  # CFU dell'esame sostenuto, non degli insegnamenti richiesti.
    assert b"pdfaid" in motore.componi_pdf(nome, compilato)


@pytest.mark.parametrize("nome", ["ssml-master", "link-singoli", "a4u-perfezionamento"])
def test_nuovi_enti_non_inventano_consensi(nome):
    campi = valori_modulo(dati_pratica(generalita={}), nome)
    assert not campi["privacy.consenso"] and not campi["privacy.diniego"]
    assert not campi["servizi.aderisce"] and not campi["servizi.non_aderisce"]


@pytest.mark.parametrize("carriera", [
    {"titolo_universitario": "Laurea magistrale"}, {"attIscritto_tipo": "Laurea I livello"},
    {"conclusione": "rinuncia"}, {"data_immatricolazione": "01/10/2015"},
])
def test_carriera_nota_non_dichiara_mai_immatricolato(carriera):
    dati = dati_pratica(generalita={"immatricolato": "0", **carriera})
    assert not valori_modulo(dati, "ssml-laurea")["mai_immatricolato"]


def test_ordinamento_sconosciuto_non_diventa_nuovo_ordinamento():
    dati = dati_pratica(generalita={"titolo_universitario": "Titolo non classificato", "materia_titolo": "Prova"})
    valori = valori_modulo(dati, "a4u-perfezionamento")
    assert valori["nuovo.denominazione"] == valori["vecchio.denominazione"] == ""


def test_anno_e_date_a4u_conservano_tutte_le_cifre():
    valori = valori_modulo(dati_pratica(generalita={"anno_scolastico": "2013/2014"}), "a4u-perfezionamento")
    assert valori["diploma.anno_cifre"] == "20132014"
    assert valori["firma.cifre"] == "17092026"


def test_la_griglia_non_tronca_email_lunghe():
    dati = compila("a4u-perfezionamento", dati_pratica(cliente={"email": "indirizzo.molto.lungo@example.org"}))
    prima = motore.componi_png("a4u-perfezionamento", dati, ppi=60)
    altra = deepcopy(dati)
    for campo in altra["pagine"][0]["campi"]:
        if campo.get("testo") == "indirizzo.molto.lungo@example.org":
            campo["testo"] = "indirizzo.molto.lungo@example.com"
    dopo = motore.componi_png("a4u-perfezionamento", altra, ppi=60)
    assert prima[0] != dopo[0] and prima[1:] == dopo[1:]
