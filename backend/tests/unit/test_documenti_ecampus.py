"""Modulo eCampus lauree: regole delle crocette, formati, posizioni nel foglio, composizione completa."""

from __future__ import annotations

import pytest

from src.documenti import motore
from src.documenti.ecampus import laurea, pagine
from src.documenti.ecampus.valori import RIGHE_ESAMI, anni, email, telefono, valori
from src.documenti.impaginazione import Casella, impagina
from tests.support.immagini import png_pieno

TITOLI = ("diploma_universitario", "vecchio_ordinamento", "primo_livello", "secondo_livello", "ciclo_unico")
USCITE = ("trasferimento_rinuncia", "trasferimento", "rinuncia", "decadenza")
TORINO = {"indirizzo": "Corso Vittorio Emanuele II", "civico": "8/B", "cap": "10123", "comune": "Torino", "provincia": "TO"}


def dati_pratica(*, pratica=None, cliente=None, corso=None, generalita=None, esami=()) -> dict:
    """I dati comuni come li prepara src.documenti.dati: pratica, cliente e corso si
    modificano voce per voce, la scheda universitaria e gli esami si sostituiscono."""
    return {
        "pratica": {"numero": "000045", "anno_accademico": "2026/2027", "data_creazione": "17/09/2026",
                    "prezzo": "2.500,00", "sede_erogazione": "",
                    "rinnovo": {"primo_anno": False, "secondo_anno": False, "terzo_anno": False}, **(pratica or {})},
        "cliente": {
            "cognome": "Della Valle", "nome": "Maria", "codice_fiscale": "dllmra95m52f205z", "sesso": "donna",
            "cittadinanza": "ITALIANA", "email": "maria.dellavalle@example.org", "pec": "", "telefono": "",
            "cellulare": "3331234567", "luogo_nascita": "Milano", "provincia_nascita": "MI", "data_nascita": "12/08/1995",
            "tipo_documento": "Carta d'Identità", "documento": "CA12345AB", "comune_rilascio": "Milano",
            "data_rilascio": "03/02/2022", "scadenza_documento": "12/08/2032",
            "residenza": {"indirizzo": "Via Garibaldi", "civico": "14", "cap": "20121", "comune": "Milano", "provincia": "MI"},
            "domicilio": dict.fromkeys(TORINO, ""), **(cliente or {}),
        },
        "corso": {"descrizione": "SCIENZE E TECNICHE PSICOLOGICHE - L-24", "codice": "", "livello": "",
                  "ente": "Università Telematica eCampus", "tipo_corso": "LAUREE", "durata": "TRIENNALE",
                  "facolta": "", "corso_laurea": "", **(corso or {})},
        "generalita": {"immatricolato": "0", "iscrizioneAltraUniversita": "0", "diploma": "Liceo scientifico"}
        if generalita is None else generalita,
        "esami": list(esami),
    }


def barrate(v: dict, nomi: tuple[str, ...], prefisso: str = "") -> set[str]:
    return {nome for nome in nomi if v[f"{prefisso}{nome}"]}


@pytest.mark.parametrize("dati", [
    dati_pratica(),
    dati_pratica(generalita={}),
    dati_pratica(cliente={"sesso": "", "tipo_documento": "", "data_nascita": ""}, pratica={"anno_accademico": ""}),
])
def test_ogni_campo_ha_il_suo_valore_anche_con_dati_mancanti(dati):
    assert [p["sfondo"] for p in impagina(laurea.PAGINE, valori(dati))] == [f"pagina-{n:02d}.jpg" for n in range(1, 11)]


def test_le_posizioni_stanno_nel_foglio_e_le_pagine_esistono():
    for pagina in laurea.PAGINE:
        assert (motore.CARTELLA_MODELLI / laurea.NOME / pagina.sfondo).is_file()
        for campo in pagina.campi:
            if isinstance(campo, Casella):
                assert 0 < campo.x < campo.x + campo.lato < 210 and 0 < campo.y < campo.y + campo.lato < 297
            else:
                assert 0 < campo.x0 < campo.x1 < 210 and 0 < campo.y < 297
    assert len(pagine.RIGHE_TABELLA_ESAMI) == RIGHE_ESAMI


@pytest.mark.parametrize(("sesso", "atteso"), [("uomo", {"m"}), ("donna", {"f"}), ("F", {"f"}), ("", set()), ("/", set())])
def test_sesso(sesso, atteso):
    assert barrate(valori(dati_pratica(cliente={"sesso": sesso})), ("m", "f"), "sesso.") == atteso


@pytest.mark.parametrize(("durata", "atteso"), [
    ("TRIENNALE", "primo"), ("MAGISTRALE", "secondo"),
    ("CICLO UNICO", "ciclo_unico"),  # il gestionale barrava la casella sbagliata
])
def test_livello_del_corso(durata, atteso):
    assert barrate(valori(dati_pratica(corso={"durata": durata})), ("primo", "secondo", "ciclo_unico"), "livello.") == {atteso}


def test_senza_rinnovo_immatricolazione_con_rinnovo_iscrizione_all_anno():
    nuova = valori(dati_pratica())
    assert nuova["immatricolazione"] and not nuova["iscrizione"] and nuova["mai_immatricolato"]
    assert barrate(nuova, ("1", "2", "3"), "anno.") == set()
    rinnovo = valori(dati_pratica(pratica={"rinnovo": {"primo_anno": False, "secondo_anno": True, "terzo_anno": True}}))
    assert rinnovo["iscrizione"] and not rinnovo["immatricolazione"] and not rinnovo["mai_immatricolato"]
    assert barrate(rinnovo, ("1", "2", "3"), "anno.") == {"2"}  # come nel gestionale: vale l'anno piu' basso


@pytest.mark.parametrize("generalita", [
    {"immatricolato": "1"},
    {"immatricolato": "-1"},
    {"immatricolato": "0", "data_immatricolazione": "01/10/2015"},
])
def test_chi_si_e_gia_immatricolato_non_lo_nega(generalita):
    assert not valori(dati_pratica(generalita=generalita))["mai_immatricolato"]


def test_un_dato_mancante_non_diventa_una_dichiarazione():
    senza_scheda = valori(dati_pratica(generalita={}))
    assert not (senza_scheda["mai_immatricolato"] or senza_scheda["non_iscritto_altrove"] or senza_scheda["diploma"])
    assert valori(dati_pratica())["non_iscritto_altrove"]
    assert not valori(dati_pratica(generalita={"iscrizioneAltraUniversita": "-1"}))["non_iscritto_altrove"]


@pytest.mark.parametrize(("titolo", "atteso"), [
    ("Diploma Universitario ", "diploma_universitario"), ("diploma_universitario", "diploma_universitario"),
    ("Laurea (Laurea 1° Livello)", "primo_livello"), ("laurea_1_livello", "primo_livello"),
    ("Laurea Magistrale", "secondo_livello"), ("Laurea Specialistica", "ciclo_unico"),
    ("Laurea vecchio ordinamento", "vecchio_ordinamento"), ("laurea_vecchio_ordinamento", "vecchio_ordinamento"),
])
def test_titolo_universitario(titolo, atteso):
    v = valori(dati_pratica(generalita={"titolo_universitario": titolo}))
    assert v["titolo"] and barrate(v, TITOLI, "titolo.") == {atteso}


@pytest.mark.parametrize(("esito", "crocette", "sezione"), [
    ("Trasferimento", {"trasferimento_rinuncia", "trasferimento"}, "lasciata"),
    ("rinuncia", {"trasferimento_rinuncia", "rinuncia"}, "lasciata"),
    ("decadenza", {"decadenza"}, "decadenza"),
    ("conseguimento titolo finale", set(), None),
])
def test_uscita_da_un_altra_universita(esito, crocette, sezione):
    v = valori(dati_pratica(generalita={
        "conclusione": esito, "data_conclusione": "15/01/2020", "universitaConclusione": "Università degli Studi di Bergamo",
        "cittaUniConclusione": "Bergamo", "provinciaConclusione": "BG",
    }))
    assert barrate(v, USCITE) == crocette
    voci = ("universita", "citta", "provincia", "data.gg", "data.mm", "data.aaaa")
    for dove in ("lasciata", "decadenza"):
        atteso = ("Università degli Studi di Bergamo", "Bergamo", "BG", "15", "01", "2020") if dove == sezione else ("",) * 6
        assert tuple(v[f"{dove}.{voce}"] for voce in voci) == atteso


@pytest.mark.parametrize(("tipo", "modalita"), [("Laurea I Livello", "Part-Time"), ("laurea_i_livello", "part_time")])
def test_iscrizione_in_corso_dal_gestionale_e_dal_nuovo_form(tipo, modalita):
    v = valori(dati_pratica(generalita={"attIscritto_tipo": tipo, "attIscritto_modalita": modalita,
                                        "attIscritto_classeLaurea": "L-24"}))
    assert v["iscritto"] and v["iscritto.laurea_primo"] and v["iscritto.part_time"] and not v["iscritto.full_time"]
    assert v["iscritto.classe"] == "L-24"
    assert not valori(dati_pratica(generalita={"attIscritto_tipo": "Dottorato"}))["iscritto"]


def test_il_documento_si_scrive_solo_sulla_sua_riga():
    v = valori(dati_pratica(cliente={"tipo_documento": "Patente", "documento": "U1A234567B", "comune_rilascio": "MCTC Milano"}))
    assert v["documento.patente"] and (v["documento.patente.numero"], v["documento.patente.rilascio"]) == ("U1A234567B", "MCTC Milano")
    assert not any(v[f"documento.{tipo}"] or v[f"documento.{tipo}.numero"] for tipo in ("carta", "passaporto", "altro"))
    assert valori(dati_pratica(cliente={"tipo_documento": "Carta d'identità"}))["documento.carta"]


def test_corrispondenza_solo_se_diversa_dalla_residenza():
    diversa = valori(dati_pratica(cliente={"domicilio": TORINO}))
    assert (diversa["corrispondenza.indirizzo"], diversa["corrispondenza.cap"]) == ("Corso Vittorio Emanuele II, 8/B", "10123")
    uguale = {"indirizzo": "VIA GARIBALDI", "civico": "14", "cap": "20121", "comune": "milano", "provincia": "MI"}
    assert valori(dati_pratica(cliente={"domicilio": uguale}))["corrispondenza.indirizzo"] == ""
    scelta = valori(dati_pratica(cliente={"domicilio": TORINO}, generalita={"corrispondenza": "Residenza"}))
    assert scelta["corrispondenza.comune"] == ""


def test_la_tabella_degli_esami_dice_quanti_ne_restano_fuori():
    esami = [{"insegnamento": f"Esame {n}", "data": "11/06/2017", "ssd": "M-PED/01", "voto": "28", "cfu": "8",
              "universita": "Università degli Studi di Pavia"} for n in range(1, 18)]
    troppi = valori(dati_pratica(esami=esami))
    assert troppi["esami"] and troppi["esami.universita"] == "Università degli Studi di Pavia"
    assert (troppi["esami.14.insegnamento"], troppi["esami.15.insegnamento"]) == ("Esame 14", "… e altri 3 esami")
    assert troppi["esami.15.voto"] == ""
    assert valori(dati_pratica(esami=esami[:RIGHE_ESAMI]))["esami.15.insegnamento"] == "Esame 15"
    assert not valori(dati_pratica())["esami"]


@pytest.mark.parametrize(("valore", "anno_solo", "atteso"), [
    ("2024/2025", "inizio", ("2024", "2025")), ("2024/25", "inizio", ("2024", "2025")),
    ("25/26", "inizio", ("2025", "2026")), ("2024-2025", "inizio", ("2024", "2025")),
    ("2025", "inizio", ("2025", "")), ("2016", "fine", ("", "2016")),
    ("", "inizio", ("", "")), ("20215/26", "inizio", ("20215/26", "")),
])
def test_anni_accademici_e_scolastici(valore, anno_solo, atteso):
    risultato = anni(valore, anno_solo=anno_solo)
    assert (risultato["inizio"], risultato["fine"]) == atteso


@pytest.mark.parametrize(("valore", "atteso"), [
    ("+39 333 1234567", ("+39", "3331234567")), ("0039 333-1234567", ("+39", "3331234567")),
    ("3331234567", ("", "3331234567")), ("+41 79 123 45 67", ("", "+41 79 123 45 67")), ("", ("", "")),
])
def test_telefono(valore, atteso):
    assert (telefono(valore)["prefisso"], telefono(valore)["numero"]) == atteso


def test_email_e_retta():
    assert email("maria.dellavalle@example.org") == {"utente": "maria.dellavalle", "dominio": "example.org"}
    assert email("senza-chiocciola") == {"utente": "senza-chiocciola", "dominio": ""}
    assert valori(dati_pratica())["retta"] == "2.500"  # il modulo stampa gia' ",00"
    assert valori(dati_pratica(pratica={"prezzo": "0,00"}))["retta"] == ""
    assert valori(dati_pratica(pratica={"prezzo": "1.250,50"}))["retta"] == "1.250,50"


def test_il_modulo_completo_ha_dieci_pagine_e_la_firma_dove_serve():
    dati = laurea.arricchisci(dati_pratica())
    assert dati["titolo"] == "Domanda di immatricolazione eCampus, pratica 000045"
    senza = motore.componi_png(laurea.NOME, dati, ppi=12)
    con = motore.componi_png(laurea.NOME, dati, {"firma": png_pieno()}, ppi=12)
    assert [prima != dopo for prima, dopo in zip(senza, con, strict=True)] == [True] * 6 + [False] * 3 + [True]
    pdf = motore.componi_pdf(laurea.NOME, dati)
    assert b"/Count 10" in pdf and b"pdfaid" in pdf
