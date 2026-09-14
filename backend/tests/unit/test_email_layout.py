"""Prove pure: nessuna connessione DB o invio a provider."""

from email import policy
from email.parser import BytesParser
from html import escape
from pathlib import Path
import re

import pytest

from src.notifiche.formato_email import applica_stili, come_testo
from src.notifiche.messaggio_email import crea_messaggio
from src.notifiche.stile_email import LOGO, LOGO_CID


RADICE = Path(__file__).resolve().parents[3]
SQL = (RADICE / "db/migrations/014_contenuti_email.sql").read_text(encoding="utf-8")
STRINGA_SQL = r"'((?:[^']|'')*)'"
MODELLI = [tuple(v.replace("''", "'") for v in valori) for valori in re.findall(
    rf"VALUES \({STRINGA_SQL}, {STRINGA_SQL}, {STRINGA_SQL}\)", SQL
)]
VALORI = {"nome": "Elena & Luca <Bianchi>", "link_reset": "https://test.example.org/reimposta-password?token=prova&x=1",
          "scadenza_minuti": "10", "data_ora": "14/09/2026 alle 18:30", "indirizzo_ip": "192.0.2.1",
          "codice_otp": "048216", "username": "elena.bianchi", "password": 'Prova<&"2026',
          "istruzioni_accesso": "Le credenziali saranno utilizzabili nei servizi abilitati per il tuo profilo."}


@pytest.mark.parametrize("codice,oggetto,corpo", MODELLI)
def test_email_complete_e_mime_rileggibile(codice, oggetto, corpo):
    corpo = re.sub(r"\{\{(\w+)\}\}", lambda m: escape(VALORI[m[1]], quote=True), corpo)
    email = crea_messaggio(oggetto, corpo, "elena@example.org", "ERSAF <noreply@example.org>")
    riletta = BytesParser(policy=policy.default).parsebytes(email.as_bytes())
    testo = riletta.get_body(preferencelist=("plain",)).get_content()
    html = riletta.get_body(preferencelist=("html",)).get_content()
    assert "Gentile Elena & Luca <Bianchi>" in testo
    assert "Gentile Elena &amp; Luca &lt;Bianchi&gt;" in html
    assert "{{" not in html
    assert "Find Your Goal" not in html
    assert "max-width:520px" in html
    assert f'cid:{LOGO_CID}' in html
    immagini = [p for p in riletta.walk() if p.get_content_maintype() == "image"]
    assert len(immagini) == 1
    assert immagini[0].get_content_disposition() == "inline"
    assert immagini[0]["Content-ID"] == f"<{LOGO_CID}>"
    assert immagini[0].get_payload(decode=True) == LOGO.read_bytes()
    if codice == "password_reset_richiesta":
        assert VALORI["link_reset"] in testo
        assert 'background:#302878' in html
        assert 'href="https://test.example.org/reimposta-password?token=prova&amp;x=1"' in html
    if codice in {"login_otp_nazionale", "otp_verifica_email"}:
        assert "048216" in testo and "10 minuti" in testo
        assert re.search(r"\b\d{6}\b", come_testo(html)).group() == "048216"
    if codice == "credenziali_accesso":
        assert VALORI["password"] in testo
        assert escape(VALORI["password"], quote=True) in html
        assert VALORI["istruzioni_accesso"] in testo
    if codice == "password_reset_eseguito":
        assert "token=" not in html and VALORI["password"] not in testo


def test_migrazione_limitata_ai_cinque_template():
    assert {m[0] for m in MODELLI} == {"password_reset_richiesta", "password_reset_eseguito",
        "login_otp_nazionale", "otp_verifica_email", "credenziali_accesso"}
    assert len(MODELLI) == 5


def test_stili_non_interpretano_valori_come_markup():
    valore = '" onclick="alert(1) <script>no</script> {{codice_otp}}'
    html = applica_stili(f'<p>{escape(valore)}</p>')
    assert "<script>" not in html
    assert escape(valore) in html
    assert "{{codice_otp}}" in html  # mai una seconda sostituzione


def test_testo_include_link_e_non_css():
    assert come_testo('<style>segreto-css</style><p>Vai <a href="https://test.example.org/">qui</a><br>Ora</p>') == "Vai qui (https://test.example.org/)\nOra"


def test_logo_identico_alla_sorgente_canonica():
    assert LOGO.read_bytes() == (RADICE / "frontend/src/assets/pratiche-universita.png").read_bytes()


def test_header_injection_rifiutata():
    with pytest.raises(ValueError):
        crea_messaggio("Titolo\nBcc: intruso@example.org", "<p>Ciao</p>", "elena@example.org", "noreply@example.org")


def test_flusso_reset_usa_template_db_e_sostituzione_unica(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test")
    from src.notifiche import email
    from src.notifiche.backend_invio import BackendMemoria
    monkeypatch.setattr(email, "get_impostazioni", lambda: SimpleNamespace(
        smtp_from="noreply@example.org", frontend_base_url="https://test.example.org"))
    monkeypatch.setattr(email, "SessionLocal", lambda: SimpleNamespace(close=lambda: None))
    _, oggetto, corpo = MODELLI[0]
    monkeypatch.setattr(email, "carica_template", lambda db, codice: (oggetto, corpo))
    mailer = BackendMemoria()
    email.invia_mail_reset(mailer, email.DatiInvioReset(1, "elena@example.org", "<Elena> {{link_reset}}", "a&b", 15))
    assert len(mailer.inviate) == 1
    html = mailer.inviate[0].get_body(preferencelist=("html",)).get_content()
    assert "&lt;Elena&gt; {{link_reset}}" in html
    assert 'href="https://test.example.org/reimposta-password?token=a%26b"' in html
    assert f'cid:{LOGO_CID}' in html


def test_flusso_otp_e_credenziali_usa_compositore_comune(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test")
    from src.notifiche import email
    from src.notifiche.backend_invio import BackendMemoria
    from src.otp import invio
    monkeypatch.setattr(email, "get_impostazioni", lambda: SimpleNamespace(smtp_from="noreply@example.org"))
    mailer = BackendMemoria()
    monkeypatch.setattr(invio, "get_mailer", lambda: mailer)
    for codice, oggetto, corpo in MODELLI[2:]:
        monkeypatch.setattr(invio, "carica_template", lambda db, tipo: (oggetto, corpo))
        invio.manda_email(None, codice, "elena@example.org", VALORI)
    assert len(mailer.inviate) == 3
    for messaggio in mailer.inviate:
        assert f'cid:{LOGO_CID}' in messaggio.get_body(preferencelist=("html",)).get_content()
