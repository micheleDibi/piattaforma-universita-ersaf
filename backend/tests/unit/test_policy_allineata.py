"""La politica delle password del frontend deve coincidere con quella del server.

Le due implementazioni sono duplicate di proposito: un endpoint che espone la
politica introdurrebbe un giro di rete su una pagina che deve disegnare le
regole subito, e regalerebbe l'elenco delle password vietate su una rotta non
autenticata; generare il JavaScript dal Python aggiungerebbe uno step di build
a un progetto che oggi fa solo `vite build`.

La duplicazione e' sorvegliata qui, e in due modi: si confrontano le costanti,
e — se node e' disponibile — si confronta il COMPORTAMENTO su un insieme di
password, eseguendo davvero il modulo JavaScript. La seconda verifica coglie
anche le divergenze di logica, non solo di dati.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from src.config import DIR_BACKEND, get_impostazioni
from src.security.password import (
    BLOCKLIST_ESATTA,
    LIMITE_BYTE_BCRYPT,
    RADICI_VIETATE,
    verifica_policy_password,
)

MODULO_JS = DIR_BACKEND.parent / "frontend" / "src" / "lib" / "passwordPolicy.js"


@pytest.fixture(scope="module")
def sorgente_js() -> str:
    assert MODULO_JS.exists(), f"atteso {MODULO_JS}"
    return MODULO_JS.read_text(encoding="utf-8")


def _costante_numerica(sorgente: str, nome: str) -> int:
    trovato = re.search(rf"export const {nome} = (\d+)", sorgente)
    assert trovato, f"costante {nome} assente da passwordPolicy.js"
    return int(trovato.group(1))


def _elenco(sorgente: str, nome: str) -> set[str]:
    trovato = re.search(rf"export const {nome} = \[(.*?)\];", sorgente, re.S)
    assert trovato, f"elenco {nome} assente da passwordPolicy.js"
    return set(re.findall(r'"([^"]+)"', trovato.group(1)))


def test_lunghezza_minima_identica(sorgente_js):
    assert _costante_numerica(sorgente_js, "LUNGHEZZA_MINIMA") == (
        get_impostazioni().password_min_length
    )


def test_limite_in_byte_identico(sorgente_js):
    assert _costante_numerica(sorgente_js, "BYTE_MASSIMI") == LIMITE_BYTE_BCRYPT


def test_blocklist_identica(sorgente_js):
    assert _elenco(sorgente_js, "BLOCKLIST_ESATTA") == set(BLOCKLIST_ESATTA)


def test_radici_identiche(sorgente_js):
    assert _elenco(sorgente_js, "RADICI_VIETATE") == set(RADICI_VIETATE)


# --- equivalenza di comportamento -------------------------------------------

# I casi AL CONFINE sono quelli che contano: senza, una divergenza di sola
# logica (un >= diventato >) passerebbe inosservata perche' nessuna password di
# prova cadrebbe esattamente sul limite.
_BASE = "Cavallo-Batteria-Graffetta-Corretta-Montagna-Fiume-Lago-Sole-Ombra-"
CONFINE_72_BYTE = _BASE + "x" * (72 - len(_BASE.encode("utf-8")))
assert len(CONFINE_72_BYTE.encode("utf-8")) == 72

CASI = [
    ("cavallo batteria graffetta", None, None),
    ("Xyzwvutsrqpo", None, None),      # esattamente 12 caratteri: accettata
    ("Xyzwvutsrqp", None, None),       # 11: rifiutata
    (CONFINE_72_BYTE, None, None),     # esattamente 72 byte: accettata
    (CONFINE_72_BYTE + "X", None, None),  # 73: rifiutata
    ("è" * 36, None, None),            # 72 byte con caratteri accentati
    ("è" * 37, None, None),            # 74 byte
    ("Corta123", None, None),
    ("a" * 73, None, None),
    ("è" * 40, None, None),
    ("Password1234!", None, None),
    ("Ersaf2026!!!", None, None),
    ("ErsafMontagna2026", None, None),
    ("aaaaaaaaaaaa", None, None),
    ("123456789012", None, None),
    ("A" * 72, None, None),
    ("mario.rossi@example.org", "mario.rossi@example.org", "mrossi"),
    ("MARIO.ROSSI@EXAMPLE.ORG", "mario.rossi@example.org", "mrossi"),
    ("mario.rossi", "mario.rossi@example.org", "mrossi"),
    ("nome.utente.lungo", None, "nome.utente.lungo"),
    ("passphrase corretta 2026", "mario@example.org", "mrossi"),
]

# Il client raggruppa uguale_email e uguale_username in una sola regola
# visibile: due righe che dicono entrambe "verificata al salvataggio" sarebbero
# rumore. La corrispondenza e' dichiarata in CODICI_SERVER_PER_REGOLA e questo
# test la usa, invece di far finta che gli identificatori coincidano.
SCRIPT = """
import { valutaPassword, CODICI_SERVER_PER_REGOLA } from %(modulo)s;
const casi = JSON.parse(process.argv[2]);
const esiti = casi.map(([pw, email, username]) => {
  const { regole, valida } = valutaPassword(pw, { email, username });
  const violate = regole
    .filter((r) => r.stato === "ko")
    .flatMap((r) => CODICI_SERVER_PER_REGOLA[r.id]);
  return { valida, violate, regoleViolate: regole.filter((r) => r.stato === "ko").map((r) => r.id) };
});
process.stdout.write(JSON.stringify(esiti));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node non disponibile")
def test_il_comportamento_coincide(tmp_path: Path):
    """Esegue davvero il modulo JavaScript e confronta gli esiti.

    Coglie le divergenze di logica, non solo quelle di dati: un confronto di
    sole costanti non si accorgerebbe, per esempio, di un `>=` diventato `>`.
    """
    script = tmp_path / "confronto.mjs"
    script.write_text(SCRIPT % {"modulo": json.dumps(str(MODULO_JS))}, encoding="utf-8")

    esito = subprocess.run(
        ["node", str(script), json.dumps(CASI)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert esito.returncode == 0, esito.stderr
    dal_javascript = json.loads(esito.stdout)

    differenze = []
    for (pw, email, username), lato_js in zip(CASI, dal_javascript):
        violate_python = sorted(
            verifica_policy_password(pw, username=username, email=email)
        )
        # Il client non conosce gli identificativi su /reimposta-password, ma
        # in questo confronto glieli passiamo per poter verificare anche
        # quella regola.
        # Si confrontano gli INSIEMI: la regola raggruppata del client copre
        # due codici del server, e solo uno dei due puo' essere violato.
        if not set(violate_python) <= set(lato_js["violate"]) or (
            bool(violate_python) != bool(lato_js["violate"])
        ):
            differenze.append(
                f"  {pw[:24]!r}: python={violate_python} javascript={lato_js['violate']}"
            )
        if (not violate_python) != lato_js["valida"]:
            differenze.append(f"  {pw[:24]!r}: verdetto complessivo diverso")

    assert not differenze, "le due politiche divergono:\n" + "\n".join(differenze)
