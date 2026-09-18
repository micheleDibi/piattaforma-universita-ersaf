"""Accesso di prova per i test della visibilita'.

Ogni helper svuota i cookie del client dopo il login e restituisce le
intestazioni esplicite della sessione: con piu' utenti nello stesso test, un
cookie rimasto nel client farebbe partire la richiesta a nome dell'ultimo che
ha fatto login, non di quello che il test intende.
"""

from __future__ import annotations

import itertools
import re

from src.notifiche.formato_email import come_testo
from src.security.password import hash_password
from tests.support import factories as f
from tests.support.sessioni import intestazioni_sessione, token_cookie

PASSWORD = "cavallo-batteria-graffetta"
_progressivo = itertools.count(1)


def email_nuova(prefisso: str = "vis") -> str:
    return f"{prefisso}{next(_progressivo)}@example.org"


def accedi(client, db, *, ruolo=f.RUOLO_REGIONALE, padre=None, azienda_id=None):
    """Un attuatore non Nazionale con sessione valida."""
    persona = f.crea_attuatore(
        db, email=email_nuova(), ruolo=ruolo, password_hash=hash_password(PASSWORD),
        padre=padre, azienda_id=azienda_id,
    )
    risposta = client.post(
        "/auth/login",
        json={"utente_username": persona.username, "utente_password": PASSWORD},
    )
    assert risposta.status_code == 200, risposta.text
    intestazioni = intestazioni_sessione(token_cookie(risposta))
    client.cookies.clear()
    return persona, intestazioni


def accedi_nazionale(client, db, mailer, *, azienda_id=None):
    """Un Nazionale: la sessione nasce solo dopo l'OTP di login via email."""
    from tests.conftest import corpo_html

    persona = f.crea_attuatore(
        db, email=email_nuova("naz"), ruolo=f.RUOLO_NAZIONALE,
        password_hash=hash_password(PASSWORD), azienda_id=azienda_id,
    )
    f.verifica_email(db, persona.cliente_id)
    avvio = client.post(
        "/auth/login",
        json={"utente_username": persona.username, "utente_password": PASSWORD},
    )
    assert avvio.status_code == 200, avvio.text
    codice = re.search(r"\b\d{6}\b", come_testo(corpo_html(mailer.inviate[-1]))).group()
    fine = client.post(
        "/auth/verifica-otp", json={"sfida": avvio.json()["sfida"], "codice": codice}
    )
    assert fine.status_code == 200, fine.text
    intestazioni = intestazioni_sessione(token_cookie(fine))
    client.cookies.clear()
    mailer.svuota()
    return persona, intestazioni


def riferimenti_pratiche(db):
    """Le righe di riferimento che una pratica richiede, con id fissi.

    Stesso allestimento di test_filtri_pratiche: si cancellano e si
    reinseriscono, perche' queste tabelle non si svuotano fra un test e
    l'altro. Il percorso va rimosso dal chiamante a fine test.
    """
    from src.database import Base
    from src.listini_testa.models import ListinoTestaDB

    for tabella, dati in {
        "listini_tipi": {"listino_tipo_codice": "TEST", "listino_tipo_descrizione": "Test"},
        "nome_universita": {"nome_universita_codice": "TEST", "nome_universita_descrizione": "Test"},
        "listini_tipicorsi": {"listino_tipoCorso_descrizione": "Test"},
        "pratiche_stati": {"pratica_stato_codice": "TEST", "pratica_stato_descrizione": "Test"},
    }.items():
        tabella_db = Base.metadata.tables[tabella]
        chiave = list(tabella_db.primary_key)[0]
        db.execute(tabella_db.delete().where(chiave.in_([900001, 900002])))
        for numero in (900001, 900002):
            db.execute(tabella_db.insert().values(**{chiave.name: numero}, **dati))
    percorsi = [
        ListinoTestaDB(listTesta_codice=f"TEST-VIS-{n}", listTesta_descrizione=f"Percorso visibilita {n}",
                       listino_tipo_id=900001, listino_tipoCorso_id=900001, nome_universita_id=900001)
        for n in range(2)
    ]
    db.add_all(percorsi)
    db.commit()
    return percorsi
