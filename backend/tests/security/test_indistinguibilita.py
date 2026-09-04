"""I rami di /password-reset/request devono essere indistinguibili.

Il messaggio identico non basta: se differisse il codice, la forma del corpo,
un header o il tempo di risposta, l'endpoint tornerebbe a essere un oracolo su
quali indirizzi esistono.
"""

from __future__ import annotations

import statistics
import time

import pytest
from sqlalchemy import select

from src.auth.models import Esito, PasswordResetRichiesta
from src.auth.schemas import CORPO_RISPOSTA_GENERICA
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

URL = "/auth/password-reset/request"

# Header aggiunti dal server e non dall'applicazione: variano per natura.
HEADER_IGNORATI = {"date", "server"}


def _impronta(risposta) -> tuple:
    """Codice, BYTE del corpo, header.

    Si confronta response.content e non .json(): .json() normalizza l'ordine
    delle chiavi, la spaziatura e la codifica, nascondendo proprio le
    differenze che si stanno cercando.
    """
    return (
        risposta.status_code,
        risposta.content,
        tuple(
            sorted(
                (chiave.lower(), valore)
                for chiave, valore in risposta.headers.items()
                if chiave.lower() not in HEADER_IGNORATI
            )
        ),
    )


def _prepara_scenari(db):
    """Nove situazioni che il codice distingue internamente e che dall'esterno
    devono risultare identiche."""
    f.crea_attuatore(db, email="valido@example.org")
    f.crea_attuatore(db, email="sottoscrittore@example.org", ruolo=f.RUOLO_SOTTOSCRITTORE)
    f.crea_attuatore(db, email="consulente@example.org", ruolo=f.RUOLO_CONSULENTE)
    f.crea_attuatore(db, email="spento@example.org", attivo=f.DISATTIVO)
    f.crea_attuatore(db, email="ambigua@example.org", ruolo=f.RUOLO_ADERENTE)
    f.crea_attuatore(db, email="ambigua@example.org", ruolo=f.RUOLO_REGIONALE)
    return [
        ("attuatore attivo", "valido@example.org"),
        ("sottoscrittore", "sottoscrittore@example.org"),
        ("consulente", "consulente@example.org"),
        ("attuatore disattivato", "spento@example.org"),
        ("indirizzo sconosciuto", "mai-visto@example.org"),
        ("indirizzo ambiguo", "ambigua@example.org"),
        ("indirizzo malformato", "non-una-email"),
        ("indirizzo vuoto", ""),
        ("indirizzo con soli spazi", "   "),
    ]


def test_i_nove_scenari_producono_la_stessa_risposta(client_da, db, mailer):
    # Un IP distinto per scenario: con lo stesso client i rami successivi al
    # quinto verrebbero tutti bloccati dal rate limit e il confronto sarebbe
    # vacuo. Che anche le risposte bloccate siano identiche e' verificato a
    # parte, dal test qui sotto.
    scenari = _prepara_scenari(db)
    impronte = {}
    for numero, (descrizione, email) in enumerate(scenari):
        cliente = client_da(f"203.0.113.{numero + 20}")
        impronte[descrizione] = _impronta(cliente.post(URL, json={"email": email}))

    distinte = set(impronte.values())
    assert len(distinte) == 1, (
        "risposte distinguibili fra loro:\n"
        + "\n".join(f"  {d}: {i}" for d, i in impronte.items())
    )
    assert next(iter(distinte))[1] == CORPO_RISPOSTA_GENERICA


def test_gli_esiti_interni_sono_invece_diversi(client_da, db, mailer):
    """Contro-prova: se il codice non distinguesse davvero i rami, il test
    precedente non proverebbe nulla."""
    scenari = _prepara_scenari(db)
    for numero, (_, email) in enumerate(scenari):
        client_da(f"203.0.113.{numero + 40}").post(URL, json={"email": email})

    db.commit()
    esiti = {
        r.prr_esito
        for r in db.execute(
            select(PasswordResetRichiesta).order_by(PasswordResetRichiesta.prr_id)
        ).scalars()
    }
    assert esiti == {
        Esito.EMAIL_INVIATA.value,
        Esito.RUOLO_NON_ABILITATO.value,
        Esito.UTENTE_DISATTIVATO.value,
        Esito.IDENTIFICATIVO_SCONOSCIUTO.value,
        Esito.IDENTIFICATIVO_AMBIGUO.value,
    }


def test_sempre_duecento_mai_un_429(client, db, mailer):
    """Un 429 direbbe all'attaccante che quell'indirizzo vale la pena
    insistere. Qui si usa di proposito un solo client, cosi' oltre la quinta
    richiesta interviene il rate limit."""
    scenari = _prepara_scenari(db)
    codici = set()
    for _ in range(2):
        for _, email in scenari:
            codici.add(client.post(URL, json={"email": email}).status_code)
    assert codici == {200}


def test_anche_la_risposta_bloccata_dal_limite_e_identica(client, db, mailer):
    """Il rate limit deve restare invisibile: la sesta richiesta e' identica
    alla prima, byte per byte."""
    f.crea_attuatore(db, email="valido@example.org")
    prima = _impronta(client.post(URL, json={"email": "valido@example.org"}))
    for _ in range(5):
        client.post(URL, json={"email": "valido@example.org"})
    bloccata = _impronta(client.post(URL, json={"email": "valido@example.org"}))
    assert bloccata == prima


def test_nessun_header_condizionale(client, db, mailer):
    scenari = _prepara_scenari(db)  # anche con il rate limit attivo
    vietati = {"retry-after", "set-cookie", "www-authenticate"}
    for _, email in scenari:
        risposta = client.post(URL, json={"email": email})
        presenti = {k.lower() for k in risposta.headers}
        assert not (presenti & vietati)
        assert not any(k.startswith("x-") for k in presenti)


def test_content_length_identico(client_da, db, mailer):
    scenari = _prepara_scenari(db)
    lunghezze = {
        client_da(f"203.0.113.{numero + 60}")
        .post(URL, json={"email": email})
        .headers.get("content-length")
        for numero, (_, email) in enumerate(scenari)
    }
    assert len(lunghezze) == 1
    assert lunghezze == {str(len(CORPO_RISPOSTA_GENERICA))}


def test_il_corpo_non_contiene_dettagli(client, db, mailer):
    scenari = _prepara_scenari(db)
    for descrizione, email in scenari:
        corpo = client.post(URL, json={"email": email}).json()
        assert set(corpo) == {"message"}, descrizione
        assert "esito" not in str(corpo).lower()


# --- tempi ------------------------------------------------------------------
#
# Una misura di latenza e' intrinsecamente rumorosa: questi test sono marcati
# `timing` ed esclusi dal gate per difetto. NON sono una prova di assenza di
# canali laterali temporali — sotto rete il jitter e' di ordini di grandezza
# superiore — ma un rilevatore di regressioni grossolane: un invio SMTP finito
# dentro il ciclo di richiesta, o un bcrypt eseguito in un ramo solo, si
# vedono benissimo anche con una misura rozza.

RIPETIZIONI = 25
RISCALDAMENTO = 5


def _mediane(client, scenari) -> dict[str, float]:
    """Misure INTERLACCIATE: A,B,C,A,B,C... e non 25 A poi 25 B.

    Cosi' il rumore della macchina — pause del garbage collector, altro carico,
    scaling della frequenza — colpisce tutti i rami allo stesso modo. E' la
    singola scelta che piu' riduce la fragilita' di questo test.
    """
    campioni: dict[str, list[float]] = {d: [] for d, _ in scenari}
    for giro in range(RIPETIZIONI + RISCALDAMENTO):
        for descrizione, email in scenari:
            inizio = time.perf_counter()
            client.post(URL, json={"email": email})
            trascorso = time.perf_counter() - inizio
            if giro >= RISCALDAMENTO:
                campioni[descrizione].append(trascorso)
    return {d: statistics.median(v) for d, v in campioni.items()}


@pytest.mark.timing
@pytest.mark.lento
def test_i_tempi_dei_rami_sono_sovrapponibili(client, db, mailer):
    """Soglia AUTO-CALIBRATA sul rumore misurato, non un numero assoluto.

    Si esegue due volte lo stesso scenario per stimare il rumore N, poi si
    pretende che lo scarto fra due rami qualsiasi resti sotto max(3*N, 20 ms).
    Il pavimento a 20 ms impedisce che il test diventi assurdamente severo su
    una macchina veloce; il 3*N impedisce che diventi inutile su un runner
    lento.
    """
    scenari = _prepara_scenari(db)
    riferimento = scenari[0]
    rumore_a = _mediane(client, [riferimento, ("controllo", riferimento[1])])
    rumore = abs(rumore_a[riferimento[0]] - rumore_a["controllo"])

    mediane = _mediane(client, scenari)
    soglia = max(3 * rumore, 0.020)
    scarto = max(mediane.values()) - min(mediane.values())

    assert scarto <= soglia, (
        f"scarto fra i rami {scarto * 1000:.1f} ms, soglia {soglia * 1000:.1f} ms "
        f"(rumore misurato {rumore * 1000:.1f} ms)\n"
        + "\n".join(f"  {d}: {v * 1000:.1f} ms" for d, v in sorted(mediane.items()))
    )


@pytest.mark.timing
@pytest.mark.lento
def test_nessun_ramo_supera_il_budget(client, db, mailer):
    """Il test assoluto, quello che coglie i bug veri: un invio SMTP dentro il
    ciclo di richiesta o un bcrypt in un ramo solo sforerebbero sempre."""
    from src.config import get_impostazioni

    budget = get_impostazioni().password_reset_budget_ms / 1000.0
    mediane = _mediane(client, _prepara_scenari(db))
    peggiore = max(mediane.values())
    assert peggiore < budget * 3, (
        f"il ramo piu' lento impiega {peggiore * 1000:.0f} ms, con un budget di "
        f"{budget * 1000:.0f} ms"
    )


@pytest.mark.timing
def test_riepilogo_dei_tempi(client, db, mailer):
    """Non fallisce mai: stampa le misure, cosi' quando il gate fallisce la
    diagnosi e' gia' nell'output."""
    mediane = _mediane(client, _prepara_scenari(db))
    print("\n  mediane per ramo:")
    for descrizione, valore in sorted(mediane.items(), key=lambda x: -x[1]):
        print(f"    {descrizione:26} {valore * 1000:7.1f} ms")
