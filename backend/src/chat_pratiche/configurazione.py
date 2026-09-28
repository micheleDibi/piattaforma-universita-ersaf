"""Configurazione nativa separata dai parametri di login dell'app."""
import base64
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import DIR_BACKEND


class ConfigChat(BaseSettings):
    model_config = SettingsConfigDict(env_file=DIR_BACKEND / ".env", extra="ignore")
    chat_abilitata: bool = False
    chat_chiavi_file: str = ""
    chat_chiave_versione: int = 1
    chat_universo_jwt_file: str = ""
    chat_universo_issuer: str = "universo-realtime"
    chat_universo_audience: str = "universo-realtime-ws"
    chat_universo_origini: str = ""
    chat_universo_inattivita_secondi: int = 86400


def leggi_segreto(percorso, minimo=32, massimo=32):
    try:
        raw = Path(percorso).read_bytes()
        if not 1 <= len(raw) <= 4096:
            raise ValueError()
        valore = base64.b64decode(raw.strip(), validate=True)
        if not minimo <= len(valore) <= massimo:
            raise ValueError()
        return valore
    except (OSError, ValueError):
        raise HTTPException(503, "Configurazione della chat non disponibile.") from None


@lru_cache
def configurazione():
    return ConfigChat()


@lru_cache
def chiavi():
    config = configurazione()
    if not config.chat_abilitata:
        raise HTTPException(503, "La chat è temporaneamente non disponibile.")
    try:
        result = {}
        for entry in config.chat_chiavi_file.split(","):
            versione, file = entry.split("=", 1)
            versione = int(versione)
            if not 1 <= versione <= 255 or versione in result:
                raise ValueError()
            result[versione] = leggi_segreto(file)
        if config.chat_chiave_versione not in result:
            raise ValueError()
        return result
    except (ValueError, TypeError):
        raise HTTPException(503, "Configurazione della chat non disponibile.") from None
