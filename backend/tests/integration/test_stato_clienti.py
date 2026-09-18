"""Gli stati mostrati negli elenchi clienti: contatti verificati e diploma.

Tutti i clienti sono figli dell'operatore, quindi visibili: qui si prova il
contenuto della risposta, non il filtro di visibilita'.
"""

from __future__ import annotations

import re

import pytest

from src.clienti.models import Cliente
from src.universita.models import Universita
from tests.integration.test_clienti import _anagrafica
from tests.support import factories as f
from tests.support.scenari import accedi, email_nuova

pytestmark = pytest.mark.mariadb

DIPLOMA = {
    "universita_diploma": "Liceo scientifico",
    "universita_anno_scolastico": "2014/2015",
    "universita_istituto": "Liceo Volta",
    "universita_votoRicevuto_diploma": 80,
    "universita_votoMassimo_diploma": 100,
}
DA_UNIVERSITA = re.compile(r"\bFROM universita\b")


def sottoscrittore(db, padre, ruolo=f.RUOLO_SOTTOSCRITTORE):
    return f.crea_attuatore(db, email=email_nuova("sott"), ruolo=ruolo, padre=padre)


def curriculum(db, cliente_id, **campi):
    riga = Universita(cliente_id=cliente_id, **campi)
    db.add(riga)
    db.commit()
    return riga


def elenco(client, sessione, **parametri):
    risposta = client.get("/clienti/", params={"limit": 200, **parametri}, headers=sessione)
    assert risposta.status_code == 200, risposta.text
    return {riga["cliente_id"]: riga for riga in risposta.json()}


def sottoscrittori(client, sessione):
    return elenco(client, sessione, solo_utenti="true")


# =============================================================================
# Email e cellulare
# =============================================================================
def test_contatti_verificati_in_elenco_finche_il_valore_non_cambia(client, db):
    io, sessione = accedi(client, db)
    persona = sottoscrittore(db, io.utente_id)
    riga = db.get(Cliente, persona.cliente_id)
    riga.cliente_cellulare = "+393331234567"
    db.commit()

    prima = sottoscrittori(client, sessione)[persona.cliente_id]
    assert (prima["email_verificata"], prima["cellulare_verificato"]) == (False, False)

    f.verifica_contatto(db, persona.cliente_id, "email")
    f.verifica_contatto(db, persona.cliente_id, "cellulare")
    dopo = sottoscrittori(client, sessione)[persona.cliente_id]
    assert (dopo["email_verificata"], dopo["cellulare_verificato"]) == (True, True)

    db.expire_all()
    riga = db.get(Cliente, persona.cliente_id)
    riga.cliente_email = "cambiata@example.org"
    riga.cliente_cellulare = "+393339999999"
    db.commit()
    cambiati = sottoscrittori(client, sessione)[persona.cliente_id]
    assert (cambiati["email_verificata"], cambiati["cellulare_verificato"]) == (False, False)


def test_anche_gli_attuatori_hanno_i_contatti_verificati(client, db):
    io, sessione = accedi(client, db)
    attuatore = sottoscrittore(db, io.utente_id, ruolo=f.RUOLO_ADERENTE)
    f.verifica_contatto(db, attuatore.cliente_id, "email")
    riga = elenco(client, sessione, solo_attuatori="true")[attuatore.cliente_id]
    assert (riga["email_verificata"], riga["cellulare_verificato"]) == (True, False)


# =============================================================================
# Diploma completo
# =============================================================================
def test_diploma_completo_in_elenco(client, db):
    io, sessione = accedi(client, db)
    completo = sottoscrittore(db, io.utente_id)
    curriculum(db, completo.cliente_id, **DIPLOMA)
    senza_curriculum = sottoscrittore(db, io.utente_id)

    righe = sottoscrittori(client, sessione)
    assert righe[completo.cliente_id]["diploma_completo"] is True
    assert righe[senza_curriculum.cliente_id]["diploma_completo"] is False


@pytest.mark.parametrize(("campo", "valore"), [
    *((campo, None) for campo in DIPLOMA),
    ("universita_diploma", "   "),
    ("universita_anno_scolastico", "   "),
    ("universita_istituto", "   "),
])
def test_un_solo_campo_mancante_rende_il_diploma_incompleto(client, db, campo, valore):
    io, sessione = accedi(client, db)
    persona = sottoscrittore(db, io.utente_id)
    riga = curriculum(db, persona.cliente_id, **DIPLOMA)
    # Scritto dopo, e direttamente: lo schema di scrittura ripulirebbe gli
    # spazi, qui si prova la regola sui dati gia' presenti.
    setattr(riga, campo, valore)
    db.commit()
    assert sottoscrittori(client, sessione)[persona.cliente_id]["diploma_completo"] is False


def test_conta_il_curriculum_piu_recente(client, db):
    io, sessione = accedi(client, db)
    recente_completo = sottoscrittore(db, io.utente_id)
    curriculum(db, recente_completo.cliente_id, universita_diploma="Vecchio")
    curriculum(db, recente_completo.cliente_id, **DIPLOMA)
    recente_incompleto = sottoscrittore(db, io.utente_id)
    curriculum(db, recente_incompleto.cliente_id, **DIPLOMA)
    curriculum(db, recente_incompleto.cliente_id, universita_diploma="Nuovo")

    righe = sottoscrittori(client, sessione)
    assert righe[recente_completo.cliente_id]["diploma_completo"] is True
    assert righe[recente_incompleto.cliente_id]["diploma_completo"] is False


def test_indirizzo_dell_istituto_e_voto_zero_non_contano(client, db):
    io, sessione = accedi(client, db)
    persona = sottoscrittore(db, io.utente_id)
    curriculum(db, persona.cliente_id, **{**DIPLOMA, "universita_votoRicevuto_diploma": 0},
               universita_via_istituto=None, universita_citta_istituto="",
               universita_provincia_istituto="  ")
    assert sottoscrittori(client, sessione)[persona.cliente_id]["diploma_completo"] is True


def test_negli_attuatori_il_diploma_non_si_calcola(client, db):
    io, sessione = accedi(client, db)
    attuatore = sottoscrittore(db, io.utente_id, ruolo=f.RUOLO_ADERENTE)
    curriculum(db, attuatore.cliente_id, **DIPLOMA)
    riga = elenco(client, sessione, solo_attuatori="true")[attuatore.cliente_id]
    assert riga["diploma_completo"] is None


def test_dettaglio_e_modifica_riportano_un_booleano(client, db):
    io, sessione = accedi(client, db)
    persona = sottoscrittore(db, io.utente_id)
    curriculum(db, persona.cliente_id, **DIPLOMA)

    dettaglio = client.get(f"/clienti/{persona.cliente_id}", headers=sessione).json()
    assert dettaglio["diploma_completo"] is True

    modificata = client.put(f"/clienti/{persona.cliente_id}",
                            json={"universita_istituto": ""}, headers=sessione)
    assert modificata.status_code == 200, modificata.text
    assert modificata.json()["diploma_completo"] is False


def test_la_modifica_riporta_il_diploma_anche_se_l_istanza_resta_viva(client, db, monkeypatch):
    """Se l'istanza creata da blocca_cliente resta in memoria, refresh() non
    ricarica `universita` e diploma_completo uscirebbe None. Di solito viene
    liberata subito, quindi il caso si provoca trattenendola."""
    import src.otp.servizio as servizio

    trattenute = []
    originale = servizio.blocca_cliente

    def trattieni(db_richiesta, cliente_id):
        risultato = originale(db_richiesta, cliente_id)
        trattenute.append(risultato)
        return risultato

    monkeypatch.setattr(servizio, "blocca_cliente", trattieni)
    io, sessione = accedi(client, db)
    persona = sottoscrittore(db, io.utente_id)
    curriculum(db, persona.cliente_id, **DIPLOMA)

    risposta = client.put(f"/clienti/{persona.cliente_id}",
                          json={"cliente_citta": "Torino"}, headers=sessione)
    assert risposta.status_code == 200, risposta.text
    assert trattenute, "blocca_cliente deve essere passato dal punto sostituito"
    assert risposta.json()["diploma_completo"] is True


def test_su_un_istanza_non_caricata_la_proprieta_non_interroga(db, spia_sql):
    io = f.crea_utente(db)
    persona = sottoscrittore(db, io.utente_id)
    curriculum(db, persona.cliente_id, **DIPLOMA)
    riga = db.get(Cliente, persona.cliente_id)
    db.expire(riga)
    spia_sql.clear()
    assert riga.diploma_completo is None
    assert spia_sql == []


# =============================================================================
# Query per pagina
# =============================================================================
def _statement_elenco(client, sessione, spia_sql, **parametri):
    """Statement di una pagina vera: risposta 200 e almeno una riga."""
    spia_sql.clear()
    risposta = client.get("/clienti/", params={"limit": 40, **parametri}, headers=sessione)
    statement = list(spia_sql)
    assert risposta.status_code == 200, risposta.text
    assert risposta.json(), "pagina vuota: non misura nulla"
    return statement


def test_una_pagina_costa_le_stesse_query_con_2_o_40_righe(client, db, spia_sql):
    """Stessa forma dei dati nelle due pagine: stesso padre (con riga clienti)
    per tutti, e un curriculum distinto per ciascuno."""
    io, sessione = accedi(client, db)
    for _ in range(2):
        curriculum(db, sottoscrittore(db, io.utente_id).cliente_id, **DIPLOMA)
    con_due = _statement_elenco(client, sessione, spia_sql, solo_utenti="true")

    for _ in range(38):
        curriculum(db, sottoscrittore(db, io.utente_id).cliente_id, **DIPLOMA)
    con_quaranta = _statement_elenco(client, sessione, spia_sql, solo_utenti="true")

    assert len(con_quaranta) == len(con_due)
    assert sum(bool(DA_UNIVERSITA.search(s)) for s in con_quaranta) == 1


def test_gli_attuatori_non_interrogano_universita(client, db, spia_sql):
    io, sessione = accedi(client, db)
    attuatore = sottoscrittore(db, io.utente_id, ruolo=f.RUOLO_ADERENTE)
    curriculum(db, attuatore.cliente_id, **DIPLOMA)
    statement = _statement_elenco(client, sessione, spia_sql, solo_attuatori="true")
    assert not any(DA_UNIVERSITA.search(s) for s in statement)


# =============================================================================
# Anno scolastico del diploma e dell'anno integrativo
# =============================================================================
def _curriculum_di(db, cliente_id):
    db.expire_all()
    return db.get(Cliente, cliente_id).curriculum


def test_la_creazione_salva_gli_anni_ripuliti(client, db):
    _, sessione = accedi(client, db)
    risposta = client.post("/clienti/con-utente", headers=sessione, json=_anagrafica(
        universita_anno_scolastico="  2014/2015 ",
        universita_anno_scolastico_ai="2016",
    ))
    assert risposta.status_code == 201, risposta.text
    riga = _curriculum_di(db, risposta.json()["cliente_id"])
    assert (riga.universita_anno_scolastico, riga.universita_anno_scolastico_ai) == ("2014/2015", "2016")


def test_la_modifica_salva_gli_anni(client, db):
    io, sessione = accedi(client, db)
    persona = sottoscrittore(db, io.utente_id)
    curriculum(db, persona.cliente_id, **DIPLOMA)

    risposta = client.put(f"/clienti/{persona.cliente_id}", headers=sessione, json={
        "universita_anno_scolastico": "2015",
        "universita_anno_scolastico_ai": " 2016/2017 ",
    })
    assert risposta.status_code == 200, risposta.text
    riga = _curriculum_di(db, persona.cliente_id)
    assert (riga.universita_anno_scolastico, riga.universita_anno_scolastico_ai) == ("2015", "2016/2017")


@pytest.mark.parametrize("campo", ["universita_anno_scolastico", "universita_anno_scolastico_ai"])
def test_un_anno_oltre_45_caratteri_e_rifiutato(client, db, campo):
    io, sessione = accedi(client, db)
    persona = sottoscrittore(db, io.utente_id)
    curriculum(db, persona.cliente_id, **DIPLOMA)
    risposta = client.put(f"/clienti/{persona.cliente_id}", headers=sessione, json={campo: "1" * 46})
    assert risposta.status_code == 422
    assert _curriculum_di(db, persona.cliente_id).universita_anno_scolastico == "2014/2015"
