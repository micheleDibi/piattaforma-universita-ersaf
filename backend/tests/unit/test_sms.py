import json
import httpx
import pytest
from src.notifiche.config_sms import ConfigSMS
from src.notifiche.sms import BackendSkebby


def config():
    return ConfigSMS(sms_backend="skebby", skebby_user_key="utente-test",
                     skebby_access_token="token-test", _env_file=None)


def test_skebby_protocollo_ufficiale():
    def provider(request):
        assert request.url == "https://api.skebby.it/API/v1.0/REST/sms"
        assert request.headers["user_key"] == "utente-test"
        assert request.headers["Access_token"] == "token-test"
        assert json.loads(request.content) == {"message_type": "GP", "message": "OTP sintetico",
            "recipient": ["+390000000000"], "sender": None, "returnCredits": False}
        return httpx.Response(201, json={"result": "OK", "order_id": "ordine-test", "total_sent": 1})
    BackendSkebby(config(), httpx.MockTransport(provider)).invia("+390000000000", "OTP sintetico")


@pytest.mark.parametrize("stato,body", [(401, {}), (500, {}), (302, {}), (201, {"result": "KO"}),
    (201, {"result": "OK", "order_id": "ordine", "total_sent": 0})])
def test_skebby_non_dichiara_successo_se_provider_non_conferma(stato, body):
    with pytest.raises(RuntimeError, match="Invio SMS non confermato"):
        BackendSkebby(config(), httpx.MockTransport(lambda _: httpx.Response(stato, json=body))).invia("+390000000000", "codice")


def test_skebby_timeout_non_espone_dettaglio():
    def provider(_): raise httpx.ReadTimeout("token-test")
    with pytest.raises(RuntimeError) as errore:
        BackendSkebby(config(), httpx.MockTransport(provider)).invia("+390000000000", "codice")
    assert "token-test" not in str(errore.value)
