"""Hashing e politica delle password."""

from __future__ import annotations

import bcrypt
import pytest

from src.config import get_impostazioni
from src.errori import ErrorePasswordTroppoLunga
from src.security.password import (
    LIMITE_BYTE_BCRYPT,
    hash_fittizio,
    hash_password,
    needs_rehash,
    verifica_policy_password,
    verify_password,
)

PASSWORD_VALIDA = "cavallo-batteria-graffetta"


def test_hash_e_verifica():
    memorizzato = hash_password(PASSWORD_VALIDA)
    assert memorizzato.startswith("$2b$")
    assert len(memorizzato) == 60
    assert verify_password(PASSWORD_VALIDA, memorizzato)
    assert not verify_password("un'altra password", memorizzato)


def test_hash_diverso_a_ogni_chiamata():
    """bcrypt incorpora un salt casuale: due hash della stessa password non
    coincidono. E' anche il motivo per cui utenti.utente_salt non serve."""
    assert hash_password(PASSWORD_VALIDA) != hash_password(PASSWORD_VALIDA)


def test_costo_configurato():
    costo = get_impostazioni().bcrypt_cost
    assert hash_password(PASSWORD_VALIDA).split("$")[2] == f"{costo:02d}"


def test_settantadue_byte_esatti_sono_accettati():
    al_limite = "A" * LIMITE_BYTE_BCRYPT
    assert len(al_limite.encode("utf-8")) == 72
    assert verify_password(al_limite, hash_password(al_limite))


def test_oltre_72_byte_viene_rifiutata_non_troncata():
    """bcrypt ignora i byte oltre il 72esimo senza segnalarlo.

    Verificato sulla libreria nuda: hashpw non solleva e checkpw di 73 byte
    contro l'hash dei primi 72 restituisce True, cioe' due password diverse
    risultano uguali. Il nostro strato deve rifiutare.
    """
    settantatre = "a" * 73
    settantadue = "a" * 72
    grezzo = bcrypt.hashpw(settantadue.encode(), bcrypt.gensalt(4))
    assert bcrypt.checkpw(settantatre.encode(), grezzo) is True, (
        "se questo fallisce, bcrypt ha cambiato comportamento: rivedere il "
        "commento in src/security/password.py"
    )

    with pytest.raises(ErrorePasswordTroppoLunga):
        hash_password(settantatre)
    assert not verify_password(settantatre, hash_password(settantadue))


def test_il_limite_e_in_byte_non_in_caratteri():
    """40 lettere accentate sono 80 byte: bcrypt le troncherebbe."""
    accentata = "è" * 40
    assert len(accentata) == 40
    assert len(accentata.encode("utf-8")) == 80
    assert "lunghezza_massima_byte" in verifica_policy_password(accentata)


def test_verify_non_solleva_mai():
    """Asimmetria voluta: se verify_password sollevasse, un attaccante
    otterrebbe un 500 mandando 73 byte, e un 500 e' un oracolo."""
    for hash_non_valido in ("", None, "non-un-hash", "$2b$12$troppo-corto"):
        assert verify_password("qualcosa", hash_non_valido) is False


def test_normalizzazione_unicode_coerente():
    """La stessa password digitata su macOS (NFD) e su Windows (NFC) deve
    verificare, altrimenti l'utente non entra piu' dall'altro sistema."""
    composta = "perché-molto-lunga"       # é precomposta
    decomposta = "perché-molto-lunga"    # e + accento combinante
    assert composta != decomposta
    assert verify_password(decomposta, hash_password(composta))


def test_needs_rehash_su_valori_non_bcrypt():
    assert needs_rehash(None)
    assert needs_rehash("")
    assert needs_rehash("legacy-in-chiaro")
    assert not needs_rehash(hash_password(PASSWORD_VALIDA))


def test_needs_rehash_dopo_un_aumento_del_costo(monkeypatch):
    """E' il caso per cui la funzione esiste: alzando BCRYPT_COST, gli hash
    prodotti con il costo precedente vanno rigenerati al primo login."""
    al_costo_minimo = bcrypt.hashpw(b"x", bcrypt.gensalt(4)).decode()
    monkeypatch.setattr(get_impostazioni(), "bcrypt_cost", 12)
    assert needs_rehash(al_costo_minimo)
    assert not needs_rehash(bcrypt.hashpw(b"x", bcrypt.gensalt(12)).decode())


def test_hash_fittizio_e_valido_e_al_costo_giusto():
    """Se il costo non coincidesse con quello reale, la differenza di tempo fra
    ramo "utente inesistente" e ramo normale sarebbe essa stessa l'oracolo."""
    fittizio = hash_fittizio()
    assert fittizio.startswith("$2b$")
    assert fittizio.split("$")[2] == f"{get_impostazioni().bcrypt_cost:02d}"
    assert verify_password("qualunque cosa", fittizio) is False
    assert hash_fittizio() is fittizio  # memoizzato: un solo bcrypt per processo


@pytest.mark.parametrize(
    "descrizione, password, codice_atteso",
    [
        ("undici caratteri", "Undici12345", "lunghezza_minima"),
        ("oltre 72 byte", "a" * 73, "lunghezza_massima_byte"),
        ("nella blocklist", "123456789012", "troppo_comune"),
        ("radice password", "Password1234!", "troppo_comune"),
        ("radice ersaf", "Ersaf2026!!!", "troppo_comune"),
        ("un solo carattere", "aaaaaaaaaaaa", "troppo_comune"),
    ],
)
def test_policy_rifiuta(descrizione, password, codice_atteso):
    assert codice_atteso in verifica_policy_password(password), descrizione


def test_policy_uguale_a_username_o_email():
    assert "uguale_username" in verifica_policy_password(
        "MarioRossi01", username="mariorossi01"
    )
    assert "uguale_email" in verifica_policy_password(
        "mario.rossi@example.org", email="Mario.Rossi@Example.ORG"
    )
    # Anche la sola parte locale: chi la usa come password non sta meglio.
    assert "uguale_email" in verifica_policy_password(
        "mario.rossi1", email="mario.rossi1@example.org"
    )


def test_policy_accetta_una_password_ragionevole():
    """Niente obbligo di maiuscole, cifre o simboli: NIST SP 800-63B prescrive
    lunghezza, non composizione."""
    assert verifica_policy_password(
        "cavallo batteria graffetta", username="mrossi", email="m@example.org"
    ) == []


def test_policy_non_rifiuta_una_parola_vietata_solo_contenuta():
    """"ersaf" e' una radice vietata, ma non deve bloccare ogni password che la
    contenga: la regola confronta il nucleo di sole lettere."""
    assert verifica_policy_password("ErsafMontagna2026") == []
