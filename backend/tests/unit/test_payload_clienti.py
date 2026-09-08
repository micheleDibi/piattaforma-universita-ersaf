"""Le due funzioni pure di src/clienti/servizio.py.

Erano dentro un corpo di 188 righe raggiungibile solo con una richiesta HTTP e
un database: e' per questo che i difetti di conversione ci sono sopravvissuti.
Qui si testano con un dizionario in ingresso e uno in uscita.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.clienti.servizio import (
    CAMPI_ABILITAZIONE,
    TipoUtente,
    genera_password,
    payload_cliente,
    payload_universita,
)
from src.comune.flag_legacy import a_flag_legacy, a_flag_legacy_uno
from src.security.password import verifica_policy_password

DATI_MINIMI = {
    "cliente_nome": "Mario",
    "cliente_cognome": "Rossi",
    "cliente_email": "mario@example.org",
    "utente_username": "MarioRossi",
    "utente_password": "non-deve-uscire",
    "universita_immatricolato": 1,
    "universita_corsi_di_formazione": -1,
    "universita_istituto": "",
    "cliente_id": 99,
}


# =============================================================================
# payload_cliente
# =============================================================================
def test_payload_cliente_separa_i_campi_del_curriculum():
    payload = payload_cliente(DATI_MINIMI, TipoUtente.SOTTOSCRITTORE, utente_id=7)

    assert "universita_immatricolato" not in payload
    assert "universita_istituto" not in payload
    assert payload["cliente_nome"] == "Mario"


def test_payload_cliente_non_propaga_le_credenziali():
    """utente_username e utente_password non sono colonne di `clienti`."""
    payload = payload_cliente(DATI_MINIMI, TipoUtente.SOTTOSCRITTORE, utente_id=7)

    assert "utente_password" not in payload
    assert "utente_username" not in payload
    assert payload["utente_id"] == 7


def test_attuatore_accende_le_abilitazioni_con_la_convenzione_legacy():
    """-1, non 1: la convenzione della piattaforma Instant Developer."""
    payload = payload_cliente(DATI_MINIMI, TipoUtente.ATTUATORE, utente_id=7)

    assert payload["cliente_abilPraticheUniv"] == -1
    assert payload["cliente_abilitazione_ecampus"] == -1
    assert payload["cliente_abilitazione_link_campus"] == -1
    assert payload["cliente_abilitazione_a4u"] == -1


def test_sottoscrittore_lascia_le_abilitazioni_spente():
    payload = payload_cliente(DATI_MINIMI, TipoUtente.SOTTOSCRITTORE, utente_id=7)

    for campo in CAMPI_ABILITAZIONE:
        assert payload[campo] == 0, campo


def test_corsi_speciali_resta_spento_anche_per_gli_attuatori():
    """Si accende a mano dalla scheda utente: non e' una decisione del tipo."""
    payload = payload_cliente(DATI_MINIMI, TipoUtente.ATTUATORE, utente_id=7)

    assert payload["cliente_abilitazione_corsi_speciali"] == 0


def test_un_valore_esplicito_non_viene_sovrascritto():
    dati = {**DATI_MINIMI, "cliente_abilitazione_ecampus": 0}
    payload = payload_cliente(dati, TipoUtente.ATTUATORE, utente_id=7)

    assert payload["cliente_abilitazione_ecampus"] == 0


# =============================================================================
# payload_universita
# =============================================================================
def test_payload_universita_tiene_solo_i_campi_del_curriculum():
    payload = payload_universita(DATI_MINIMI, cliente_id=42, autore_id=7)

    assert "cliente_nome" not in payload
    assert payload["universita_immatricolato"] == 1
    assert payload["cliente_id"] == 42


def test_i_campi_vuoti_si_omettono_e_vale_il_default_della_tabella():
    """Erano tre diramazioni che assegnavano tutte None: dieci righe per una.

    Omettere la colonna e' meglio che scriverci None: sulle nullable il
    risultato e' lo stesso, e sulle cinque NOT NULL scrivere None sarebbe un
    IntegrityError.
    """
    payload = payload_universita(DATI_MINIMI, cliente_id=42, autore_id=7)

    assert "universita_istituto" not in payload
    assert None not in payload.values()


def test_l_attribuzione_e_le_date_le_decide_il_server():
    payload = payload_universita(
        {**DATI_MINIMI, "universita_createBy": 999},
        cliente_id=42,
        autore_id=7,
        oggi=date(2026, 9, 8),
    )

    assert payload["universita_createBy"] == 7
    assert payload["universita_updateBy"] == 7
    assert payload["universita_createDate"] == date(2026, 9, 8)
    assert payload["universita_updateDate"] == date(2026, 9, 8)


def test_il_curriculum_non_riscrive_il_cliente_id_ricevuto():
    """cliente_id compare in UniversitaBase: vince quello della riga creata."""
    payload = payload_universita(DATI_MINIMI, cliente_id=42, autore_id=7)

    assert payload["cliente_id"] == 42  # non 99, che arrivava nei dati


# =============================================================================
# Flag legacy: il difetto che perdeva il dato
# =============================================================================
@pytest.mark.parametrize("ingresso", [True, 1, -1, "1", "-1", "true"])
def test_ogni_forma_di_vero_diventa_meno_uno(ingresso):
    """Prima un -1 in ingresso non corrispondeva a nessun ramo, finiva
    nell'else e veniva salvato 0: un vero diventava un falso in silenzio."""
    assert a_flag_legacy(ingresso) == -1


@pytest.mark.parametrize("ingresso", [False, 0, "0", "", None, "false"])
def test_ogni_forma_di_falso_diventa_zero(ingresso):
    assert a_flag_legacy(ingresso) == 0


def test_immatricolato_usa_uno_e_non_meno_uno():
    """L'unica delle cinque colonne la cui convenzione di vero e' 1."""
    assert a_flag_legacy_uno(True) == 1
    assert a_flag_legacy_uno(False) == 0


def test_un_valore_inatteso_non_solleva():
    """Una riga legacy con un valore fuori convenzione non deve dare 500."""
    assert a_flag_legacy("boh") == 0
    assert a_flag_legacy(7) == -1


# =============================================================================
# Password generata
# =============================================================================
@pytest.mark.parametrize(
    ("nome", "cognome", "utente_id"),
    [
        ("Li", "Bo", 5),          # cinque caratteri: sotto il minimo
        ("A", "B", 1),            # tre caratteri
        ("Mario", "Rossi", 4772),  # caso normale
        ("Giuseppe", "Verdi", 12),
    ],
)
def test_la_password_generata_supera_sempre_la_policy(nome, cognome, utente_id):
    """Prima "Li Bo" con id 5 dava LiBo5: cinque caratteri, policy violata, e
    la creazione falliva su una password che l'operatore non aveva scelto -
    dopo avere gia' bruciato un valore di AUTO_INCREMENT."""
    username = f"{nome}{cognome}"
    password = genera_password(nome, cognome, utente_id, username)

    assert verifica_policy_password(password, username=username) == []


def test_la_password_generata_parte_dal_nome():
    """Il formato resta quello scelto: e' una decisione, non un difetto."""
    assert genera_password("Mario", "Rossi", 4772, "MarioRossi").startswith("MarRos4772")
