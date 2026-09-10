"""Il dominio `clienti`: creazione, aggiornamento parziale, curriculum.

Aveva copertura zero, e i difetti trovati sono esattamente quelli che un test
di questo tipo avrebbe intercettato il giorno stesso.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

from src.clienti.models import Cliente
from src.security.password import hash_password, verify_password
from src.universita.models import Universita
from src.utenti.models import Utente
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

PASSWORD_OPERATORE = "cavallo-batteria-graffetta"


def _operatore(client, db, ruolo=f.RUOLO_REGIONALE, email="operatore@example.org"):
    """Un attuatore autenticato, con il ruolo che amministra gli altri."""
    attuatore = f.crea_attuatore(
        db, email=email, ruolo=ruolo, password_hash=hash_password(PASSWORD_OPERATORE)
    )
    risposta = client.post(
        "/auth/login",
        json={
            "utente_username": attuatore.username,
            "utente_password": PASSWORD_OPERATORE,
        },
    )
    assert risposta.status_code == 200, risposta.text
    return attuatore, {"Authorization": f"Bearer {risposta.json()['token']}"}


def _anagrafica(**extra):
    """Il minimo che ClienteConUtenteCreate accetta."""
    base = {
        "cliente_codice": "COD-TEST-1",
        "cliente_nome": "Mario",
        "cliente_cognome": "Rossi",
        "cliente_email": "mario.rossi@example.org",
        "cliente_indirizzo": "Via Prova",
        "cliente_civico": "1",
        "cliente_citta": "Milano",
        "cliente_luogoNascita": "Milano",
        "cliente_dataNascita": "1990-01-01",
        "cliente_cittadinanza": "Italiana",
        "cliente_documento": "AA0000001",
        "cliente_comuneRilascio": "Milano",
        "cliente_dataRilascio": "2020-01-01",
        "cliente_dataScadenzaDocumento": "2030-01-01",
        "cliente_ruolo": f.RUOLO_ADERENTE,
    }
    base.update(extra)
    return base


# =============================================================================
# Creazione
# =============================================================================
def test_l_utente_creato_riesce_ad_accedere(client, db):
    """Il difetto era utente_attivoSN=1 dove la convenzione legacy vuole -1.

    Sia il login sia la validazione della sessione confrontano con -1: chi
    veniva creato riceveva lo stesso 401 indistinguibile di un account che non
    esiste, senza che nessuno potesse capire perche'.
    """
    _, intestazione = _operatore(client, db)

    creazione = client.post(
        "/clienti/con-utente?tipo_utente=sottoscrittore",
        json=_anagrafica(),
        headers=intestazione,
    )
    assert creazione.status_code == 201, creazione.text
    corpo = creazione.json()

    accesso = client.post(
        "/auth/login",
        json={
            "utente_username": corpo["username_generato"],
            "utente_password": corpo["password_generata"],
        },
    )
    assert accesso.status_code == 200, accesso.text
    assert accesso.json()["utente_id"] == corpo["utente_id"]


def test_la_password_non_finisce_in_chiaro_nel_database(client, db):
    _, intestazione = _operatore(client, db)

    corpo = client.post(
        "/clienti/con-utente", json=_anagrafica(), headers=intestazione
    ).json()

    utente = db.get(Utente, corpo["utente_id"])
    # NOT NULL: stringa vuota, mai NULL e mai la password.
    assert utente.utente_password == ""
    assert utente.utente_password_hash
    assert utente.utente_password_hash != corpo["password_generata"]
    assert verify_password(corpo["password_generata"], utente.utente_password_hash)


def test_l_utente_creato_e_attivo_con_la_convenzione_legacy(client, db):
    _, intestazione = _operatore(client, db)

    corpo = client.post(
        "/clienti/con-utente", json=_anagrafica(), headers=intestazione
    ).json()

    assert db.get(Utente, corpo["utente_id"]).utente_attivoSN == -1


def test_due_omonimi_ricevono_username_distinti(client, db):
    """Il database non ha la UNIQUE su utente_username e ne contiene gia'
    cinque gruppi di duplicati. Con due username uguali il login diventa
    ambiguo e viene negato a entrambi."""
    _, intestazione = _operatore(client, db)

    primo = client.post(
        "/clienti/con-utente",
        json=_anagrafica(cliente_codice="COD-A", cliente_email="a@example.org",
                         cliente_documento="AA1"),
        headers=intestazione,
    ).json()
    secondo = client.post(
        "/clienti/con-utente",
        json=_anagrafica(cliente_codice="COD-B", cliente_email="b@example.org",
                         cliente_documento="AA2"),
        headers=intestazione,
    ).json()

    assert primo["username_generato"] != secondo["username_generato"]
    assert secondo["username_generato"].startswith("MarioRossi")


def test_un_tipo_utente_scritto_male_non_passa_in_silenzio(client, db):
    """Era `str` libero: ?tipo_utente=Attuatorre cadeva nel ramo
    sottoscrittore e nessuno se ne accorgeva."""
    _, intestazione = _operatore(client, db)

    risposta = client.post(
        "/clienti/con-utente?tipo_utente=Attuatorre",
        json=_anagrafica(),
        headers=intestazione,
    )
    assert risposta.status_code == 422


def test_l_attuatore_riceve_le_abilitazioni_accese(client, db):
    _, intestazione = _operatore(client, db)

    corpo = client.post(
        "/clienti/con-utente?tipo_utente=attuatore",
        json=_anagrafica(),
        headers=intestazione,
    ).json()

    cliente = db.get(Cliente, corpo["cliente_id"])
    assert cliente.cliente_abilPraticheUniv == -1
    assert cliente.cliente_abilitazione_ecampus == -1
    # Si accende a mano dalla scheda utente.
    assert cliente.cliente_abilitazione_corsi_speciali == 0


def test_un_documento_duplicato_e_rifiutato(client, db):
    _, intestazione = _operatore(client, db)
    client.post("/clienti/con-utente", json=_anagrafica(), headers=intestazione)

    risposta = client.post(
        "/clienti/con-utente",
        json=_anagrafica(cliente_codice="COD-ALTRO", cliente_email="altro@example.org"),
        headers=intestazione,
    )
    assert risposta.status_code == 400
    assert "documento" in risposta.json()["detail"].lower()


# =============================================================================
# Aggiornamento parziale
# =============================================================================
def test_un_put_parziale_non_azzera_i_campi_omessi(client, db):
    """model_dump() senza exclude_unset riscriveva ogni campo non inviato con
    il default dello schema: un attuatore veniva declassato a ruolo 0 e
    perdeva azienda, associazioni e abilitazioni."""
    _, intestazione = _operatore(client, db)
    creato = client.post(
        "/clienti/con-utente?tipo_utente=attuatore",
        json=_anagrafica(cliente_ruolo=f.RUOLO_REGIONALE),
        headers=intestazione,
    ).json()

    risposta = client.put(
        f"/clienti/{creato['cliente_id']}",
        json={"cliente_citta": "Torino"},
        headers=intestazione,
    )
    assert risposta.status_code == 200, risposta.text

    db.expire_all()
    cliente = db.get(Cliente, creato["cliente_id"])
    assert cliente.cliente_citta == "Torino"
    assert cliente.cliente_ruolo == f.RUOLO_REGIONALE  # non azzerato
    assert cliente.utente_id == creato["utente_id"]    # NOT NULL, non None
    assert cliente.cliente_abilPraticheUniv == -1      # non azzerata
    assert cliente.cliente_nome == "Mario"


# =============================================================================
# Curriculum formativo
# =============================================================================
def test_il_curriculum_si_rilegge_dopo_la_creazione(client, db):
    """ClienteResponse non esponeva la relazione: in modifica il form leggeva
    undefined e la scheda restava sempre vuota."""
    _, intestazione = _operatore(client, db)
    creato = client.post(
        "/clienti/con-utente",
        json=_anagrafica(universita_istituto="Liceo Prova",
                         universita_corsi_di_formazione=True),
        headers=intestazione,
    ).json()

    letto = client.get(f"/clienti/{creato['cliente_id']}", headers=intestazione)
    assert letto.status_code == 200
    curriculum = letto.json()["curriculum"]
    assert curriculum is not None
    assert curriculum["universita_istituto"] == "Liceo Prova"


def test_il_curriculum_si_salva_anche_in_modifica(client, db):
    """PUT /clienti/{id} validava contro ClienteCreate, che non ha i campi
    universita_*: Pydantic li scartava in silenzio e rispondeva 200. Il
    curriculum si poteva scrivere solo alla creazione."""
    _, intestazione = _operatore(client, db)
    creato = client.post(
        "/clienti/con-utente", json=_anagrafica(), headers=intestazione
    ).json()

    risposta = client.put(
        f"/clienti/{creato['cliente_id']}",
        json={"universita_istituto": "Istituto Nuovo"},
        headers=intestazione,
    )
    assert risposta.status_code == 200, risposta.text
    assert risposta.json()["curriculum"]["universita_istituto"] == "Istituto Nuovo"

    db.expire_all()
    riga = db.scalars(
        select(Universita).where(Universita.cliente_id == creato["cliente_id"])
    ).one()
    assert riga.universita_istituto == "Istituto Nuovo"


@pytest.mark.parametrize(
    ("campo", "atteso"),
    [
        ("universita_iscrizioneAltraUniversita", -1),
        ("universita_attivita_professionalizzanti", -1),
        ("universita_corsi_di_formazione", -1),
        ("universita_altre_attivita_certificate", -1),
        # L'unica delle cinque la cui convenzione di vero e' 1.
        ("universita_immatricolato", 1),
    ],
)
def test_una_casella_spuntata_si_rilegge_spuntata(client, db, campo, atteso):
    """Il round-trip che perdeva il dato: il form mandava true, il backend
    scriveva 1 dove la colonna vuole -1, il form rileggeva === -1 e mostrava la
    casella vuota."""
    _, intestazione = _operatore(client, db)

    creato = client.post(
        "/clienti/con-utente", json=_anagrafica(**{campo: True}), headers=intestazione
    ).json()

    riga = db.scalars(
        select(Universita).where(Universita.cliente_id == creato["cliente_id"])
    ).one()
    assert getattr(riga, campo) == atteso

    letto = client.get(f"/clienti/{creato['cliente_id']}", headers=intestazione)
    assert letto.json()["curriculum"][campo] == atteso
