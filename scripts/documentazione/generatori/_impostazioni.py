"""Sottoprocesso: campi di configurazione del backend e loro obbligatorietà.

L'obbligatorietà non è scritta a mano: si parte da una configurazione valida
fatta di valori finti espliciti, si riporta un campo alla volta al valore
predefinito e si guarda se la verifica di avvio lo nomina.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import re
import sys
import typing

from _avvio import importa_app

# Valori finti: nessuno è un segreto reale o un indirizzo esistente.
BASE_COMUNE = {
    "database_url": "mysql+pymysql://utente:segreto@localhost/esempio",
    "password_reset_token_pepper": "finto-pepper-per-il-reset-" + "a" * 32,
    "session_token_pepper": "finto-pepper-per-le-sessioni-" + "b" * 32,
    "totp_chiave": "finta-chiave-per-i-codici-" + "c" * 32,
}
BASI = {
    "sviluppo": {**BASE_COMUNE, "ersaf_env": "sviluppo"},
    "produzione": {
        **BASE_COMUNE,
        "ersaf_env": "produzione",
        "email_backend": "smtp",
        "smtp_host": "smtp.example.com",
        "frontend_base_url": "https://app.example.com",
    },
}
NOMI_SEGRETI = re.compile(r"(?:^|_)(?:PEPPER|PASSWORD|TOKEN|CHIAVE|KEY|USER)(?:_|$)")


def descrivi_tipo(annotazione) -> str:
    from pydantic import SecretStr

    if typing.get_origin(annotazione) is typing.Literal:
        return " | ".join(str(v) for v in typing.get_args(annotazione))
    return {str: "testo", int: "intero", bool: "sì/no", SecretStr: "testo segreto"}.get(
        annotazione, getattr(annotazione, "__name__", str(annotazione)))


def campi(modello) -> list[dict]:
    from pydantic import SecretStr

    risultato = []
    for nome, campo in modello.model_fields.items():
        variabile = nome.upper()
        annotazione = campo.annotation
        segreto = annotazione in (str, SecretStr) and bool(NOMI_SEGRETI.search(variabile))
        predefinito = campo.default
        if isinstance(predefinito, SecretStr):
            predefinito = predefinito.get_secret_value()
        if segreto:
            resa = "—" if predefinito else "(vuoto)"
        elif isinstance(predefinito, str):
            if not predefinito:
                resa = "(vuoto)"
            elif "@" in predefinito:
                resa = "(valore nel codice)"
            else:
                resa = predefinito
        else:
            resa = str(predefinito)
        risultato.append({"campo": nome, "variabile": variabile, "tipo": descrivi_tipo(annotazione),
                          "predefinito": resa})
    return risultato


def obbligatori(config) -> dict[str, list[str]]:
    from src.errori import ErroreConfigurazione

    def problemi(valori: dict) -> str:
        try:
            config.verifica_configurazione(config.Impostazioni(**valori))
        except ErroreConfigurazione as errore:
            return str(errore)
        return ""

    esito: dict[str, list[str]] = {}
    for ambiente, base in BASI.items():
        if problemi(base):
            raise SystemExit(f"la configurazione finta di {ambiente} non è valida: {problemi(base)}")
        for campo in base:
            if campo == "ersaf_env":
                continue
            ridotta = {k: v for k, v in base.items() if k != campo}
            if re.search(rf"\b{campo.upper()}\b", problemi(ridotta)):
                esito.setdefault(campo, []).append(ambiente)
    return esito


def obbligatori_sms(config_sms) -> dict[str, str]:
    def rifiutata(**valori) -> bool:
        try:
            config_sms.ConfigSMS(**valori).verifica()
        except ValueError:
            return True
        return False

    completa = {"sms_backend": "skebby", "skebby_user_key": "x", "skebby_access_token": "y",
                "skebby_sender": "z", "skebby_message_type": "GP"}
    if rifiutata(**completa):
        raise SystemExit("la configurazione SMS finta non è valida")
    return {campo: "con SMS_BACKEND=skebby" for campo in completa
            if campo != "sms_backend" and rifiutata(**{k: v for k, v in completa.items() if k != campo})}


def sms_in_produzione(main, config) -> bool:
    """Vero se l'avvio in produzione rifiuta un SMS_BACKEND diverso da skebby."""
    ambiente = {k.upper(): v for k, v in BASI["produzione"].items()}
    ambiente.update(SMS_BACKEND="memoria", LOG_FILE="")
    os.environ.update(ambiente)
    config.get_impostazioni.cache_clear()

    async def avvia():
        async with main.lifespan(main.app):
            pass

    try:
        asyncio.run(avvia())
    except ValueError as errore:
        return "SMS_BACKEND" in str(errore)
    finally:
        for chiave in ambiente:
            os.environ.pop(chiave, None)
        config.get_impostazioni.cache_clear()
    return False


def raccogli(backend: str) -> dict:
    main = importa_app(backend)
    import src.config as config
    import src.notifiche.config_sms as config_sms

    obbligo = obbligatori(config)
    impostazioni = campi(config.Impostazioni)
    for voce in impostazioni:
        ambienti = obbligo.get(voce["campo"], [])
        voce["obbligatoria"] = ("sì" if set(ambienti) == set(BASI)
                                else "in produzione" if ambienti == ["produzione"] else "no")
    sms = campi(config_sms.ConfigSMS)
    obbligo_sms = obbligatori_sms(config_sms)
    produzione = sms_in_produzione(main, config)
    for voce in sms:
        voce["obbligatoria"] = obbligo_sms.get(voce["campo"], "no")
        if voce["campo"] == "sms_backend" and produzione:
            voce["obbligatoria"] = "in produzione (skebby)"
    return {"impostazioni": impostazioni, "sms": sms}


def main(backend: str) -> None:
    # L'avvio dell'applicazione configura un log su stdout: qui stdout deve
    # contenere solo il JSON.
    with contextlib.redirect_stdout(sys.stderr):
        dati = raccogli(backend)
    json.dump(dati, sys.stdout, ensure_ascii=True, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1])
