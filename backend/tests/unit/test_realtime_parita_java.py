"""Vettori eseguiti sulle classi Java originali, con sole chiavi sintetiche.

La fixture conserva gli hash dei sorgenti di riferimento. Il test ordinario
non richiede un JDK e non accede al repository o ai servizi legacy.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from src.chat_pratiche import chiavi
from src.chat_pratiche.cifratura import codifica, decodifica
from src.realtime import crypto, lettura, paginazione
from src.realtime.contratti import json_limitato
from src.realtime.conversazioni import Conversazione
from src.realtime.dati import json_compatibile
from src.realtime.errori import ErroreRealtime
from src.realtime.scrittura import ORDINE

VETTORI = json.loads((Path(__file__).parents[1] / "support/realtime_java_vectors.json").read_text("utf-8"))


@pytest.mark.parametrize("caso", VETTORI["cases"], ids=lambda c: c["domain"] + ":" + c["variant"])
def test_cifratura_conforme_al_riferimento_java(caso, monkeypatch):
    monkeypatch.setattr(chiavi, "chiavi", lambda: {1: bytes(range(32))})
    monkeypatch.setattr(crypto, "configurazione", lambda: SimpleNamespace(chat_chiave_versione=1))
    monkeypatch.setattr(crypto.time, "time", lambda: VETTORI["epoch"] * 3600 + 1)
    c = Conversazione(caso["type"], caso["resource"], "PR-42", caso.get("public"), caso["domain"], ())
    assert codifica(chiavi.deriva(1, VETTORI["epoch"], c.dominio)) == caso["key"]
    comando = dict(content=caso["u2"], clientMessageId=caso["cid"])
    if caso["status"] != "accepted":
        with pytest.raises(ErroreRealtime) as errore:
            crypto.apri(c, int(caso["sender"]), comando)
        assert errore.value.detail == caso["status"]
        return
    materiale = crypto.apri(c, int(caso["sender"]), comando)
    assert materiale[0].decode() == caso["clear"]
    nonce = decodifica(caso["u3"][3:])[6:18]
    monkeypatch.setattr(crypto.os, "urandom", lambda n: nonce if n == 12 else bytes(n))
    assert crypto.conserva(c, int(caso["sender"]), 77, materiale) == caso["u3"]
    assert not any(materiale[0])


@pytest.mark.parametrize(
    "nome,ordine",
    [
        ("command", ORDINE),
        ("notification", ("target", "createdBy", "operation", "idRef", "title", "message")),
    ],
)
def test_hash_idempotenza_conforme_al_riferimento_java(nome, ordine):
    originale = VETTORI[nome]
    canonico = {campo: originale[campo] for campo in ordine if campo in originale}
    digest = hashlib.sha256(json_compatibile(canonico).encode()).hexdigest()
    assert digest == VETTORI[nome + "Hash"]


def test_cursore_conforme_al_riferimento_java(monkeypatch):
    monkeypatch.setattr(paginazione, "segreto", lambda: bytes(range(32)))
    identita = SimpleNamespace(utente_id=10, cliente_id=101)
    ambito = "conversations:PERSON:ricerca"
    assert paginazione.cursore(identita, ambito, 77) == VETTORI["cursor"]
    assert paginazione.confine(identita, ambito, VETTORI["cursor"]) == 77


@pytest.mark.parametrize("caso", VETTORI["json"])
def test_parser_conforme_al_riferimento_java(caso):
    if caso["accepted"]:
        assert type(json_limitato(caso["raw"])) is dict
    else:
        with pytest.raises(ErroreRealtime):
            json_limitato(caso["raw"])


@pytest.mark.parametrize("caso", VETTORI["dates"])
def test_timestamp_legacy_conforme_al_riferimento_java(caso, monkeypatch):
    monkeypatch.setattr(lettura, "esegui", lambda *args: SimpleNamespace(scalar=lambda: None))
    valore = lettura.istante(None, "PERSON", 77, datetime.fromisoformat(caso["local"]))
    assert datetime.fromisoformat(valore) == datetime.fromisoformat(caso["utc"])
