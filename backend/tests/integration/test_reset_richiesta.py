"""POST /auth/password-reset/request: gli esiti e la riga di audit."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from src.auth.models import Esito, PasswordResetRichiesta, PasswordResetToken
from src.auth.schemas import CORPO_RISPOSTA_GENERICA
from src.security.rete import impacchetta_ip
from src.security.tokens import TipoToken, impronta
from tests.conftest import corpo_html
from tests.support import factories as f

pytestmark = pytest.mark.mariadb

URL = "/auth/password-reset/request"


def _richiedi(client, email):
    return client.post(URL, json={"email": email})


def _audit(db):
    return db.execute(
        select(PasswordResetRichiesta).order_by(PasswordResetRichiesta.prr_id)
    ).scalars().all()


def test_attuatore_attivo_riceve_la_mail(client, db, mailer):
    attuatore = f.crea_attuatore(db, email="attuatore@example.org")

    risposta = _richiedi(client, attuatore.email)

    assert risposta.status_code == 200
    assert risposta.content == CORPO_RISPOSTA_GENERICA

    db.commit()
    righe = _audit(db)
    assert len(righe) == 1
    assert righe[0].prr_esito == Esito.EMAIL_INVIATA.value
    assert righe[0].prr_utente_id == attuatore.utente_id

    token = db.execute(select(PasswordResetToken)).scalar_one()
    assert token.utente_id == attuatore.utente_id
    assert len(token.prt_token_hash) == 64
    assert token.prt_email_inviata == attuatore.email
    assert len(mailer.inviate) == 1


@pytest.mark.parametrize(
    "descrizione, ruolo",
    [("sottoscrittore", f.RUOLO_SOTTOSCRITTORE), ("consulente", f.RUOLO_CONSULENTE),
     ("operatore", f.RUOLO_OPERATORE)],
)
def test_ruolo_non_abilitato(client, db, mailer, descrizione, ruolo):
    """Consulente e Operatore sono trattati come i sottoscrittori: nessuna mail."""
    attuatore = f.crea_attuatore(db, email=f"{descrizione}@example.org", ruolo=ruolo)
    assert _richiedi(client, attuatore.email).status_code == 200

    db.commit()
    assert _audit(db)[0].prr_esito == Esito.RUOLO_NON_ABILITATO.value
    assert db.execute(select(PasswordResetToken)).first() is None
    assert mailer.inviate == []


def test_indirizzo_sconosciuto_non_registra_l_utente(client, db, mailer):
    """prr_utente_id resta NULL: non si ricrea nel log l'oracolo che
    l'endpoint evita di esporre."""
    assert _richiedi(client, "nessuno@example.org").status_code == 200

    db.commit()
    riga = _audit(db)[0]
    assert riga.prr_esito == Esito.IDENTIFICATIVO_SCONOSCIUTO.value
    assert riga.prr_utente_id is None
    assert mailer.inviate == []


def test_attuatore_disattivato(client, db, mailer):
    attuatore = f.crea_attuatore(
        db, email="spento@example.org", attivo=f.DISATTIVO
    )
    assert _richiedi(client, attuatore.email).status_code == 200

    db.commit()
    assert _audit(db)[0].prr_esito == Esito.UTENTE_DISATTIVATO.value
    assert mailer.inviate == []


def test_email_condivisa_da_due_attuatori_e_ambigua(client, db, mailer):
    """Venti attuatori condividono l'indirizzo con un altro cliente: inviare a
    tutti significherebbe mandare a Tizio il link di reset di Caio."""
    f.crea_attuatore(db, email="condivisa@example.org", ruolo=f.RUOLO_ADERENTE)
    f.crea_attuatore(db, email="condivisa@example.org", ruolo=f.RUOLO_PROVINCIALE)

    assert _richiedi(client, "condivisa@example.org").status_code == 200

    db.commit()
    assert _audit(db)[0].prr_esito == Esito.IDENTIFICATIVO_AMBIGUO.value
    assert db.execute(select(PasswordResetToken)).first() is None
    assert mailer.inviate == []


def test_due_righe_clienti_dello_stesso_utente_non_sono_ambigue(client, db, mailer):
    """Quattro utenti hanno due righe `clienti`: la deduplicazione e' su
    utente_id, altrimenti resterebbero senza recupero password per un
    artefatto dei dati."""
    attuatore = f.crea_attuatore(db, email="doppio@example.org")
    f.crea_cliente(
        db, utente_id=attuatore.utente_id, email="doppio@example.org",
        ruolo=f.RUOLO_REGIONALE,
    )

    assert _richiedi(client, "doppio@example.org").status_code == 200

    db.commit()
    assert _audit(db)[0].prr_esito == Esito.EMAIL_INVIATA.value
    assert len(mailer.inviate) == 1


def test_attuatore_che_condivide_con_un_sottoscrittore_riceve_comunque(client, db, mailer):
    """Regola del paragrafo 2.2 presa alla lettera: ambiguo significa piu' di
    un utente IDONEO. Il limite e' dichiarato nell'analisi."""
    attuatore = f.crea_attuatore(db, email="mista@example.org", ruolo=f.RUOLO_ADERENTE)
    f.crea_attuatore(db, email="mista@example.org", ruolo=f.RUOLO_SOTTOSCRITTORE)

    assert _richiedi(client, "mista@example.org").status_code == 200

    db.commit()
    assert _audit(db)[0].prr_esito == Esito.EMAIL_INVIATA.value
    assert _audit(db)[0].prr_utente_id == attuatore.utente_id


def test_email_normalizzata(client, db, mailer):
    """strip e lower sul parametro; la colonna resta nuda per non annullare
    l'indice."""
    attuatore = f.crea_attuatore(db, email="mario.rossi@example.org")
    assert _richiedi(client, "  Mario.Rossi@Example.ORG  ").status_code == 200

    db.commit()
    assert _audit(db)[0].prr_esito == Esito.EMAIL_INVIATA.value
    assert _audit(db)[0].prr_utente_id == attuatore.utente_id


def test_email_malformata_non_produce_un_422(client, db, mailer):
    """Il trabocchetto: con EmailStr nello schema, Pydantic risponderebbe 422
    con il dettaglio della validazione e l'indistinguibilita' sarebbe bucata
    proprio nel caso che la specifica nomina."""
    for malformata in ["non-una-email", "@example.org", "a@b", "", "   ", "//"]:
        risposta = _richiedi(client, malformata)
        assert risposta.status_code == 200, malformata
        assert risposta.content == CORPO_RISPOSTA_GENERICA


def test_utente_orfano_non_causa_500(client, db, mailer):
    f.crea_utente_orfano(db)
    assert _richiedi(client, "orfano@example.org").status_code == 200


def test_l_indirizzo_non_e_conservato_in_chiaro(client, db, mailer):
    """La 003 salva solo l'impronta: una richiesta di reset non e' un dato che
    serva conservare in forma leggibile per contare cinque tentativi."""
    attuatore = f.crea_attuatore(db, email="riservata@example.org")
    _richiedi(client, attuatore.email)

    db.commit()
    riga = _audit(db)[0]
    assert riga.prr_identificativo_hash == impronta(attuatore.email, TipoToken.RESET)
    assert attuatore.email not in str(riga.__dict__)


def test_una_riga_di_audit_per_ogni_richiesta(client, db, mailer):
    f.crea_attuatore(db, email="conta@example.org")
    for _ in range(3):
        _richiedi(client, "conta@example.org")
    db.commit()
    assert len(_audit(db)) == 3


def test_una_nuova_richiesta_revoca_il_token_precedente(client, db, mailer):
    """Requisito 5: la query [A] della 002, prima dell'inserimento."""
    attuatore = f.crea_attuatore(db, email="revoca@example.org")
    _richiedi(client, attuatore.email)
    _richiedi(client, attuatore.email)

    db.commit()
    token = db.execute(
        select(PasswordResetToken).order_by(PasswordResetToken.prt_id)
    ).scalars().all()
    assert len(token) == 2
    assert token[0].prt_revoked_at is not None
    assert token[0].prt_revoked_reason == "nuova_richiesta"
    assert token[1].prt_revoked_at is None


def test_l_ip_e_registrato_impacchettato(client, db, mailer):
    f.crea_attuatore(db, email="ip@example.org")
    _richiedi(client, "ip@example.org")
    db.commit()
    assert _audit(db)[0].prr_ip == impacchetta_ip("203.0.113.7")


def test_la_mail_contiene_il_link_e_non_l_impronta(client, db, mailer):
    attuatore = f.crea_attuatore(db, email="link@example.org", nome="Mario")
    _richiedi(client, attuatore.email)

    db.commit()
    assert len(mailer.inviate) == 1
    html = corpo_html(mailer.inviate[0])
    token_db = db.execute(select(PasswordResetToken)).scalar_one()

    assert "/reimposta-password?token=" in html
    # Nel link va il token, non la sua impronta.
    assert token_db.prt_token_hash not in html
    assert "{{" not in html and "}}" not in html
    assert "Mario" in html
    # Un solo destinatario: nessun invio in copia a chi condivide la casella.
    assert mailer.inviate[0]["To"] == attuatore.email


def test_il_nome_del_cliente_e_escapato(client, db, mailer):
    attuatore = f.crea_attuatore(
        db, email="xss@example.org", nome="Mario <script>alert(1)</script>"
    )
    _richiedi(client, attuatore.email)

    html = corpo_html(mailer.inviate[0])
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_un_guasto_dell_invio_non_cambia_la_risposta(client, db, mailer):
    """Altrimenti l'attaccante scoprirebbe quali indirizzi fanno fallire
    l'invio."""
    attuatore = f.crea_attuatore(db, email="guasto@example.org")
    mailer.errore = RuntimeError("SMTP irraggiungibile")

    risposta = _richiedi(client, attuatore.email)
    assert risposta.status_code == 200
    assert risposta.content == CORPO_RISPOSTA_GENERICA

    db.commit()
    assert _audit(db)[0].prr_esito == Esito.ERRORE_INVIO.value
    # Il token resta valido: l'utente puo' ritentare.
    assert db.execute(select(PasswordResetToken)).scalar_one().prt_revoked_at is None
