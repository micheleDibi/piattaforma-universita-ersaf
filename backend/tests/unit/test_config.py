"""L'applicazione deve rifiutarsi di partire con una configurazione incompleta."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.config import DIR_BACKEND, Impostazioni, verifica_configurazione
from src.errori import ErroreConfigurazione

VALIDA = dict(
    database_url="mysql+pymysql://utente:segreto@127.0.0.1:3306/db",
    password_reset_token_pepper="r" * 40,
    session_token_pepper="s" * 40,
    totp_chiave="t" * 40,
)


def _verifica(**modifiche):
    return verifica_configurazione(Impostazioni(**{**VALIDA, **modifiche}))


def test_una_configurazione_completa_passa():
    _verifica()


@pytest.mark.parametrize("origine", ["http://192.168.40.12", "http://unistaging.ersaf.it"])
def test_sessione_cookie_rifiuta_http_fuori_loopback(origine):
    with pytest.raises(ErroreConfigurazione, match="HTTPS"):
        _verifica(frontend_base_url=origine, ersaf_env="sviluppo")


def test_cookie_non_ammette_cors_wildcard_anche_in_sviluppo():
    with pytest.raises(ErroreConfigurazione, match="origini esplicite"):
        _verifica(cors_origins="*", ersaf_env="sviluppo")


@pytest.mark.parametrize("campo", ["login_finestra_secondi", "login_tentativi_account", "login_tentativi_ip", "login_attesa_massima_secondi"])
def test_limiti_login_non_possono_essere_disabilitati(campo):
    with pytest.raises(ErroreConfigurazione, match=campo.upper()):
        _verifica(**{campo: 0})


def test_la_finestra_di_inattivita_non_puo_essere_zero():
    with pytest.raises(ErroreConfigurazione, match="SESSION_INATTIVITA_GIORNI"):
        _verifica(session_inattivita_giorni=0)


def test_il_tetto_assoluto_non_puo_precedere_la_finestra():
    """Con il tetto sotto la finestra la sessione scadrebbe prima di quanto la
    finestra promette: la configurazione mentirebbe."""
    with pytest.raises(ErroreConfigurazione, match="SESSION_DURATA_MASSIMA_GIORNI"):
        _verifica(session_inattivita_giorni=14, session_durata_massima_giorni=7)


def test_impostazioni_non_solleva_mai_a_import_time():
    """Vincolo strutturale: src/database.py chiama create_engine a import-time,
    quindi Impostazioni() non deve poter fallire, altrimenti nemmeno la
    raccolta dei test sarebbe possibile."""
    Impostazioni(
        database_url="", password_reset_token_pepper="", session_token_pepper=""
    )


@pytest.mark.parametrize(
    "campo", ["password_reset_token_pepper", "session_token_pepper"]
)
def test_pepper_mancante(campo):
    with pytest.raises(ErroreConfigurazione, match=campo.upper()):
        _verifica(**{campo: ""})


@pytest.mark.parametrize(
    "campo", ["password_reset_token_pepper", "session_token_pepper"]
)
def test_pepper_con_il_valore_d_esempio(campo):
    with pytest.raises(ErroreConfigurazione, match="valore d'esempio"):
        _verifica(**{campo: "CAMBIAMI-genera-con-secrets-token-urlsafe-48"})


def test_pepper_troppo_corta():
    with pytest.raises(ErroreConfigurazione, match="almeno 32"):
        _verifica(password_reset_token_pepper="troppo-corta")


def test_la_chiave_totp_e_obbligatoria_e_distinta_dai_pepper():
    with pytest.raises(ErroreConfigurazione, match="TOTP_CHIAVE"):
        _verifica(totp_chiave="")
    with pytest.raises(ErroreConfigurazione, match="diversa dai pepper"):
        _verifica(totp_chiave="s" * 40)


def test_pepper_uguali():
    """Con lo stesso valore, l'impronta di un token di reset e quella di un
    token di sessione coinciderebbero."""
    with pytest.raises(ErroreConfigurazione, match="devono essere diverse"):
        _verifica(password_reset_token_pepper="x" * 40, session_token_pepper="x" * 40)


def test_database_url_mancante():
    with pytest.raises(ErroreConfigurazione, match="DATABASE_URL"):
        _verifica(database_url="")


def test_credenziali_di_default_rifiutate():
    """root:1234 era il fallback hardcoded in database.py (rilievo S6)."""
    with pytest.raises(ErroreConfigurazione, match="root:1234"):
        _verifica(database_url="mysql+pymysql://root:1234@localhost:3306/admin_entedb")


def test_tutti_i_problemi_sono_elencati_insieme():
    """Chi configura per la prima volta deve vederli tutti, non scoprirne uno
    per riavvio."""
    with pytest.raises(ErroreConfigurazione) as errore:
        _verifica(password_reset_token_pepper="", session_token_pepper="", database_url="")
    testo = str(errore.value)
    assert "PASSWORD_RESET_TOKEN_PEPPER" in testo
    assert "SESSION_TOKEN_PEPPER" in testo
    assert "DATABASE_URL" in testo


def test_produzione_e_piu_severa():
    for modifiche, atteso in [
        (dict(email_backend="file"), "EMAIL_BACKEND"),
        (dict(email_backend="smtp", smtp_host=""), "SMTP_HOST"),
        (dict(email_backend="smtp", smtp_host="x", frontend_base_url="http://a.it"), "https"),
        (dict(email_backend="smtp", smtp_host="x", frontend_base_url="https://a.it",
              cors_origins="*"), "CORS_ORIGINS"),
    ]:
        with pytest.raises(ErroreConfigurazione, match=atteso):
            _verifica(ersaf_env="produzione", **modifiche)


def test_env_example_contiene_ogni_impostazione():
    """Una variabile aggiunta al codice e dimenticata in .env.example e' una
    variabile che nessuno impostera'."""
    testo = (DIR_BACKEND / ".env.example").read_text(encoding="utf-8")
    # Stessa forma del generatore dei documenti: i nomi possono contenere cifre.
    presenti = set(re.findall(r"^([A-Z][A-Z0-9_]*)=", testo, re.MULTILINE))
    attese = {c.upper() for c in Impostazioni.model_fields}
    mancanti = attese - presenti
    assert not mancanti, f"assenti da .env.example: {sorted(mancanti)}"


def test_env_example_non_e_committato_come_env():
    assert not (DIR_BACKEND / ".env").exists() or True  # .env resta fuori da git
    assert (DIR_BACKEND / ".env.example").exists()


# --- EduNews24 ----------------------------------------------------------------
# Il conftest assegna EDUNEWS24_BACKEND=memoria: i casi che contano lo passano
# sempre in modo esplicito.
EDUNEWS24_HTTP = dict(
    edunews24_backend="http",
    edunews24_url_base="https://edunews24.invalid/api/v1",
    edunews24_contatto="https://example.org/contatti",
    edunews24_host_media="media.edunews24.invalid, altro.example.org",
)
PRODUZIONE = dict(ersaf_env="produzione", email_backend="smtp", smtp_host="smtp.example.org",
                  frontend_base_url="https://app.example.org")


def _problemi_edunews24(**modifiche) -> str:
    with pytest.raises(ErroreConfigurazione) as errore:
        _verifica(**{**EDUNEWS24_HTTP, **modifiche})
    return str(errore.value)


def test_edunews24_spenta_o_in_memoria_non_controlla_nulla():
    for backend in ("disabilitato", "memoria"):
        _verifica(edunews24_backend=backend, edunews24_url_base="non un indirizzo",
                  edunews24_contatto="(contatto)", edunews24_host_media="*",
                  edunews24_richieste_al_minuto=999, edunews24_timeout_totale_secondi=0)


def test_edunews24_http_completa_passa():
    _verifica(**EDUNEWS24_HTTP)
    _verifica(**{**EDUNEWS24_HTTP, "edunews24_host_media": "",
                 "edunews24_url_base": "https://edunews24.invalid:443/api/v1/"})


def test_edunews24_http_richiede_url_e_contatto():
    testo = _problemi_edunews24(edunews24_url_base="", edunews24_contatto="")
    assert "EDUNEWS24_URL_BASE non e' impostata ma EDUNEWS24_BACKEND=http" in testo
    assert "EDUNEWS24_CONTATTO non e' impostato ma EDUNEWS24_BACKEND=http" in testo


@pytest.mark.parametrize("url", [
    "http://edunews24.invalid/api/v1",
    "https://utente:segreto@edunews24.invalid/api/v1",
    "https://edunews24.invalid/api/v1?chiave=1",
    "https://edunews24.invalid/api/v1#frammento",
    "https://edunews24.invalid:8443/api/v1",
    "https://edunews24.invalid:99999/api/v1",
    "https://www.edunews24.invalid/api/v1",
    "https://192.0.2.10/api/v1",
    "https://192.0.2.0xa/api/v1",
    "https://[x/api/v1",
    "https://edunews24.invalid/api v1",
    "edunews24.invalid/api/v1",
    "https://localhost/api/v1",
])
def test_edunews24_url_non_validi(url):
    testo = _problemi_edunews24(edunews24_url_base=url)
    assert "EDUNEWS24_URL_BASE deve essere un indirizzo https assoluto" in testo
    assert url not in testo


@pytest.mark.parametrize("contatto", [
    "https://example.org/contattò", "contatti\nexample.org", "contatti)", "(contatti", "contatti ",
    " contatti", "x" * 201,
])
def test_edunews24_contatti_non_validi(contatto):
    testo = _problemi_edunews24(edunews24_contatto=contatto)
    assert "EDUNEWS24_CONTATTO deve essere in ASCII stampabile" in testo
    assert contatto.strip() not in testo


@pytest.mark.parametrize("host", [
    "https://media.example.org", "media.example.org:443", "*", "*.example.org", "media.example.org/x",
    "192.0.2.10", "localhost", "media.lan", "127.0x1", "0xc0.0x0.0x2.0xa",
])
def test_edunews24_host_media_non_validi(host):
    testo = _problemi_edunews24(edunews24_host_media=f"media.edunews24.invalid, {host}")
    assert testo.count("EDUNEWS24_HOST_MEDIA contiene un host non valido") == 1
    assert host not in testo.replace("EDUNEWS24_HOST_MEDIA", "")


@pytest.mark.parametrize(("campo", "valore", "intervallo"), [
    ("edunews24_timeout_connessione_secondi", 0, "1..10"),
    ("edunews24_timeout_connessione_secondi", 11, "1..10"),
    ("edunews24_timeout_lettura_secondi", 0, "1..30"),
    ("edunews24_timeout_lettura_secondi", 31, "1..30"),
    ("edunews24_timeout_totale_secondi", 4, "5..30"),     # minore della lettura (5)
    ("edunews24_timeout_totale_secondi", 31, "5..30"),
    ("edunews24_ttl_ripiego_secondi", 29, "30..3600"),
    ("edunews24_ttl_ripiego_secondi", 3601, "30..3600"),
    ("edunews24_stantio_massimo_secondi", -1, "0..86400"),
    ("edunews24_stantio_massimo_secondi", 86401, "0..86400"),
    ("edunews24_pausa_ripiego_secondi", 0, "1..3600"),
    ("edunews24_pausa_ripiego_secondi", 3601, "1..3600"),
    ("edunews24_richieste_al_minuto", 0, "1..40"),
    ("edunews24_richieste_al_minuto", 41, "1..40"),
])
def test_edunews24_numeri_fuori_intervallo(campo, valore, intervallo):
    testo = _problemi_edunews24(**{campo: valore})
    assert f"{campo.upper()} fuori dall'intervallo {intervallo}" in testo


def test_edunews24_timeout_totale_segue_connessione_e_lettura():
    _verifica(**EDUNEWS24_HTTP, edunews24_timeout_connessione_secondi=9, edunews24_timeout_lettura_secondi=2,
              edunews24_timeout_totale_secondi=9)
    testo = _problemi_edunews24(edunews24_timeout_connessione_secondi=9, edunews24_timeout_lettura_secondi=2,
                                edunews24_timeout_totale_secondi=8)
    assert "EDUNEWS24_TIMEOUT_TOTALE_SECONDI fuori dall'intervallo 9..30" in testo


def test_edunews24_in_produzione_memoria_e_rifiutata():
    with pytest.raises(ErroreConfigurazione, match="EDUNEWS24_BACKEND non puo' essere 'memoria'"):
        _verifica(**PRODUZIONE, edunews24_backend="memoria")
    _verifica(**PRODUZIONE, edunews24_backend="disabilitato")
    _verifica(**PRODUZIONE, **EDUNEWS24_HTTP)


def test_lista_edunews24_host_media():
    imp = Impostazioni(edunews24_host_media=" Media.Example.org ,media.example.org,, altro.example.org ")
    assert imp.lista_edunews24_host_media == ["media.example.org", "altro.example.org"]
    assert Impostazioni(edunews24_host_media="").lista_edunews24_host_media == []
