"""Configurazione nativa separata dai parametri di login dell'app."""

import base64
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import DIR_BACKEND


class ConfigChat(BaseSettings):
    model_config = SettingsConfigDict(env_file=DIR_BACKEND / ".env", extra="ignore")
    chat_chiavi_file: str = ""
    chat_chiave_versione: int = 1
    chat_universo_jwt_file: str = ""
    chat_universo_issuer: str = "universo-realtime"
    chat_universo_audience: str = "universo-realtime-ws"
    chat_universo_origini: str = ""
    chat_universo_inattivita_secondi: int = 86400
    realtime_schema_ticket: str = "admin_gestionale_ticket"
    realtime_accesso_secondi: int = 900
    realtime_refresh_giorni: int = 30
    realtime_producer_token_file: str = ""
    realtime_manutenzione_secondi: int = 60
    realtime_max_connections: int = Field(default=2000, ge=1, le=100000)
    realtime_max_connections_per_user: int = Field(default=8, ge=1, le=100)
    realtime_max_connections_per_auth_session: int = Field(default=4, ge=1, le=50)
    realtime_command_workers: int = Field(default=2, ge=1, le=8)
    realtime_command_queue: int = Field(default=256, ge=16, le=4096)
    realtime_commands_per_user: int = Field(default=8, ge=1, le=64)
    realtime_outbound_queue_frames: int = Field(default=64, ge=4, le=1024)
    realtime_outbound_queue_bytes: int = Field(default=131072, ge=16384, le=16777216)
    realtime_outbound_global_queue_bytes: int = Field(default=134217728, ge=1048576, le=1073741824)
    realtime_send_timeout_millis: int = Field(default=10000, ge=1000, le=60000)


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
    result = {}
    try:
        for entry in config.chat_chiavi_file.split(","):
            versione, file = entry.split("=", 1)
            versione = int(versione)
            if not 1 <= versione <= 255 or versione in result:
                raise ValueError()
            result[versione] = bytearray(leggi_segreto(file))
        if config.chat_chiave_versione not in result:
            raise ValueError()
        return result
    except (HTTPException, ValueError, TypeError):
        for valore in result.values():
            valore[:] = b"\0" * len(valore)
        raise HTTPException(503, "Configurazione della chat non disponibile.") from None


def svuota_chiavi():
    if chiavi.cache_info().currsize:
        for valore in chiavi().values():
            valore[:] = b"\0" * len(valore)
    chiavi.cache_clear()
