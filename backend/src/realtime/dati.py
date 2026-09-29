"""SQL confinato al database principale e allo schema ticket configurato."""

import json
import re
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from sqlalchemy import text
from src.chat_pratiche.configurazione import configurazione


def ora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def iso(data):
    return data.isoformat(timespec="microseconds") + "Z" if data else None


def json_compatibile(valore):
    # Le ricevute Java usano JsonObject.toString(), non Gson.toJson():
    # nessuna escape HTML. Alterarla cambierebbe l'hash dei comandi storici.
    valore = json.dumps(valore, ensure_ascii=False, separators=(",", ":"))
    return valore.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def schema_ticket():
    nome = configurazione().realtime_schema_ticket
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", nome):
        raise ValueError("Configurare REALTIME_SCHEMA_TICKET sullo stesso server MariaDB.")
    return "`" + nome + "`."


def esegui(db, sql, valori=None):
    sql = sql.replace("{ticket}", schema_ticket()).replace("{entity}", "")
    # Limiti della singola query: nessuna impostazione residua sulle connessioni del pool.
    return db.execute(
        text("SET STATEMENT max_statement_time=4, innodb_lock_wait_timeout=2 FOR " + sql), valori or {}
    )


@lru_cache
def query(nome):
    # I nomi provengono esclusivamente dai moduli, mai dalla richiesta HTTP.
    return (Path(__file__).parent / "sql" / (nome + ".sql")).read_text(encoding="utf-8")
