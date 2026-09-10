"""Rate limit: cinque richieste all'ora per IP e per account."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select

from src.auth.models import Esito, PasswordResetRichiesta, PasswordResetToken
from src.auth.schemas import CORPO_RISPOSTA_GENERICA
from src.config import get_impostazioni
from src.security.rete import impacchetta_ip
from src.security.tempo import istante_meno_ore
from src.security.tokens import TipoToken, impronta
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

URL = "/auth/password-reset/request"
LIMITE = 5


def _esiti(db):
    return [
        r.prr_esito
        for r in db.execute(
            select(PasswordResetRichiesta).order_by(PasswordResetRichiesta.prr_id)
        ).scalars()
    ]


def test_la_sesta_richiesta_dallo_stesso_ip_non_invia(client, db, mailer):
    """Indirizzi diversi, stesso IP: e' il limite per IP a scattare."""
    for numero in range(LIMITE):
        f.crea_attuatore(db, email=f"utente{numero}@example.org")
    for numero in range(LIMITE):
        assert client.post(URL, json={"email": f"utente{numero}@example.org"}).status_code == 200

    f.crea_attuatore(db, email="sesto@example.org")
    mailer.svuota()
    risposta = client.post(URL, json={"email": "sesto@example.org"})

    assert risposta.status_code == 200
    assert risposta.content == CORPO_RISPOSTA_GENERICA
    assert mailer.inviate == []

    db.commit()
    assert _esiti(db)[-1] == Esito.RATE_LIMITED_IP.value


def test_la_sesta_richiesta_sullo_stesso_account_non_invia(client_da, db, mailer):
    """IP diversi, stesso indirizzo: e' il limite per account a scattare."""
    f.crea_attuatore(db, email="bersaglio@example.org")
    for numero in range(LIMITE):
        cliente = client_da(f"203.0.113.{numero + 10}")
        assert cliente.post(URL, json={"email": "bersaglio@example.org"}).status_code == 200

    mailer.svuota()
    risposta = client_da("198.51.100.1").post(URL, json={"email": "bersaglio@example.org"})

    assert risposta.status_code == 200
    assert risposta.content == CORPO_RISPOSTA_GENERICA
    assert mailer.inviate == []

    db.commit()
    assert _esiti(db)[-1] == Esito.RATE_LIMITED_ACCOUNT.value


def test_il_limite_non_espone_un_retry_after(client, db, mailer):
    """Un header condizionale sarebbe distinguibile quanto un 429."""
    f.crea_attuatore(db, email="header@example.org")
    risposte = [client.post(URL, json={"email": "header@example.org"}) for _ in range(6)]
    assert {r.status_code for r in risposte} == {200}
    for risposta in risposte:
        assert "retry-after" not in {k.lower() for k in risposta.headers}


def test_il_controllo_precede_il_lookup(client, db, mailer):
    """Con il limite gia' saturo, un indirizzo sconosciuto deve dare un esito
    di rate limit e non 'identificativo_sconosciuto': altrimenti l'ordine delle
    operazioni rivelerebbe che la ricerca e' avvenuta."""
    for numero in range(LIMITE):
        client.post(URL, json={"email": f"ignoto{numero}@example.org"})

    client.post(URL, json={"email": "mai-visto@example.org"})
    db.commit()
    assert _esiti(db)[-1] == Esito.RATE_LIMITED_IP.value


def test_anche_le_richieste_bloccate_contano(client, db, mailer):
    """Il contatore include le righe di rate limit: la finestra non si svuota
    finche' non passa un'ora dalla quinta richiesta."""
    f.crea_attuatore(db, email="conta@example.org")
    for _ in range(8):
        client.post(URL, json={"email": "conta@example.org"})
    db.commit()
    esiti = _esiti(db)
    assert len(esiti) == 8
    assert esiti[:LIMITE] == [Esito.EMAIL_INVIATA.value] * LIMITE
    # Stesso IP e stesso indirizzo: entrambi i limiti scattano insieme, e il
    # controllo per IP viene per primo. Cio' che conta e' che le richieste
    # bloccate continuino a essere registrate e quindi conteggiate.
    assert set(esiti[LIMITE:]) <= {
        Esito.RATE_LIMITED_IP.value,
        Esito.RATE_LIMITED_ACCOUNT.value,
    }


def test_finestra_scorrevole_di_un_ora(client, db, mailer):
    """Cinque richieste di piu' di un'ora fa non contano piu'."""
    attuatore = f.crea_attuatore(db, email="finestra@example.org")
    impronta_email = impronta("finestra@example.org", TipoToken.RESET)
    for _ in range(LIMITE):
        db.add(
            PasswordResetRichiesta(
                prr_created_at=istante_meno_ore(2),
                prr_ip=impacchetta_ip("203.0.113.7"),
                prr_identificativo_hash=impronta_email,
                prr_utente_id=attuatore.utente_id,
                prr_esito=Esito.EMAIL_INVIATA.value,
            )
        )
    db.commit()

    mailer.svuota()
    assert client.post(URL, json={"email": "finestra@example.org"}).status_code == 200
    db.commit()
    assert _esiti(db)[-1] == Esito.EMAIL_INVIATA.value
    assert len(mailer.inviate) == 1


def test_ipv4_e_ipv6_hanno_contatori_distinti(client_da, db, mailer):
    for numero in range(LIMITE):
        f.crea_attuatore(db, email=f"v{numero}@example.org")
    ipv4 = client_da("203.0.113.50")
    for numero in range(LIMITE):
        ipv4.post(URL, json={"email": f"v{numero}@example.org"})

    f.crea_attuatore(db, email="da-ipv6@example.org")
    mailer.svuota()
    ipv6 = client_da("2001:db8::99")
    assert ipv6.post(URL, json={"email": "da-ipv6@example.org"}).status_code == 200

    db.commit()
    assert _esiti(db)[-1] == Esito.EMAIL_INVIATA.value
    assert len(mailer.inviate) == 1


def test_l_header_x_forwarded_for_non_aggira_il_limite(client, db, mailer):
    """Non si legge X-Forwarded-For nel codice applicativo: dietro proxy si usa
    uvicorn --proxy-headers. Un parser scritto in casa sarebbe la via classica
    per farsi falsificare l'IP."""
    for numero in range(LIMITE):
        f.crea_attuatore(db, email=f"xff{numero}@example.org")
        client.post(URL, json={"email": f"xff{numero}@example.org"})

    f.crea_attuatore(db, email="dopo-xff@example.org")
    mailer.svuota()
    risposta = client.post(
        URL,
        json={"email": "dopo-xff@example.org"},
        headers={"X-Forwarded-For": "198.51.100.77"},
    )
    assert risposta.status_code == 200
    db.commit()
    assert _esiti(db)[-1] == Esito.RATE_LIMITED_IP.value
    assert mailer.inviate == []


def test_il_limite_e_configurabile(client, db, mailer):
    assert get_impostazioni().password_reset_rate_limit_per_hour == LIMITE
