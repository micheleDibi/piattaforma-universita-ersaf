"""Ogni rotta chiede un token, tranne quelle pubbliche per progetto.

Diciotto endpoint su ventisei erano aperti: tutto `aziende`, tutto `ruoli`,
tutto `universita`, i due GET di `utenti`, tre rotte su quattro di `clienti` e
login-as. Nessuno se n'era accorto perche' l'autenticazione era dichiarata
endpoint per endpoint, e chi aggiungeva una rotta non aveva modo di sapere che
doveva ricordarsene.

Questo test si costruisce da solo dall'elenco delle rotte: una rotta nuova non
protetta lo fa fallire il giorno in cui viene scritta, senza che nessuno debba
aggiornare un elenco.
"""

from __future__ import annotations

import pytest
from fastapi.routing import APIRoute

from src.main import app

# Le uniche rotte che devono restare raggiungibili senza sessione.
#   /                      pagina di cortesia
#   /salute                sonda per il reverse proxy
#   /auth/login            deve essere pubblica per definizione
#   /auth/logout           sempre 204, anche con un token gia' revocato:
#                          un codice diverso direbbe se quel token e' esistito
#   /auth/password-reset/* il recupero password serve a chi non puo' accedere
PUBBLICHE = {
    ("GET", "/"),
    ("GET", "/salute"),
    ("POST", "/auth/login"),
    ("POST", "/auth/logout"),
    ("POST", "/auth/password-reset/request"),
    ("GET", "/auth/password-reset/validate"),
    ("POST", "/auth/password-reset/confirm"),
}

# Valori di esempio per i segnaposto: la rotta non deve essere raggiunta, il
# 401 deve arrivare prima che il corpo o l'id vengano guardati.
SEGNAPOSTO = {"utente_id": "1", "cliente_id": "1", "azienda_id": "1",
              "ruolo_id": "1", "universita_id": "1"}


def _rotte():
    def raccogli(contenitore):
        for rotta in getattr(contenitore, "routes", []) or []:
            if isinstance(rotta, APIRoute):
                yield rotta
            elif type(rotta).__name__ == "_IncludedRouter":
                # FastAPI annida i router inclusi invece di appiattirli.
                yield from raccogli(rotta.original_router)

    for rotta in raccogli(app):
        for metodo in sorted(rotta.methods - {"HEAD", "OPTIONS"}):
            percorso = rotta.path
            for nome, valore in SEGNAPOSTO.items():
                percorso = percorso.replace("{" + nome + "}", valore)
            yield metodo, rotta.path, percorso


TUTTE = list(_rotte())
DA_PROTEGGERE = [t for t in TUTTE if (t[0], t[1]) not in PUBBLICHE]


def test_l_elenco_delle_rotte_non_e_vuoto():
    """Se il walker smettesse di trovare le rotte, i test sotto passerebbero
    tutti senza provare nulla."""
    assert len(TUTTE) >= 25
    assert len(DA_PROTEGGERE) >= 18


@pytest.mark.parametrize(
    ("metodo", "percorso"),
    [(m, p) for m, _, p in DA_PROTEGGERE],
    ids=[f"{m} {t}" for m, t, _ in DA_PROTEGGERE],
)
def test_senza_bearer_risponde_401(client, metodo, percorso):
    risposta = client.request(metodo, percorso, json={})
    assert risposta.status_code == 401, (
        f"{metodo} {percorso} risponde {risposta.status_code} senza token"
    )


@pytest.mark.parametrize(
    ("metodo", "percorso"),
    [(m, p) for m, _, p in DA_PROTEGGERE],
    ids=[f"{m} {t}" for m, t, _ in DA_PROTEGGERE],
)
def test_un_token_inventato_non_vale(client, metodo, percorso):
    risposta = client.request(
        metodo, percorso, json={}, headers={"Authorization": "Bearer non-esiste"}
    )
    assert risposta.status_code == 401


def test_l_header_legacy_non_autentica_piu(client):
    """`x-utente-id` era un intero non firmato: bastava cambiarlo."""
    risposta = client.get("/clienti/", headers={"x-utente-id": "1"})
    assert risposta.status_code == 401
