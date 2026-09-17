"""docs/tecnica/riferimenti/configurazione.md: variabili di backend, deploy e frontend.

Non riporta mai un valore reale: dei file di esempio si leggono solo i nomi e
i commenti (ripuliti da indirizzi, domini e credenziali), dei campi del
backend solo i valori predefiniti scritti nel codice, e mai quelli dei segreti.
"""

from __future__ import annotations

import re
from pathlib import Path

from comune import leggi, redigi
from generatori import cella, intestazione, python_backend

_VARIABILE = re.compile(r"^([A-Z][A-Z0-9_]*)=")
_SEPARATORE = re.compile(r"^#\s*[-=]{5,}\s*$")
_USO_COMPOSE_ENV = re.compile(r"compose_env_(?:get|set)\s+([A-Z][A-Z0-9_]*)")
_AMBIENTE_SCRIPT = re.compile(r"\$\{(ERSAF_[A-Z0-9_]+):-")
_INTERPOLAZIONE = re.compile(r"\$\{([A-Z][A-Z0-9_]*)")
_VITE = re.compile(r"\bVITE_[A-Z0-9_]+\b")
_ENV_VITE_CONFIG = re.compile(r"\benv\.([A-Z][A-Z0-9_]+)\b")
_GETENV = re.compile(r"os\.(?:getenv|environ\.get)\(\s*[\"']([A-Z][A-Z0-9_]+)[\"']|os\.environ\[\s*[\"']([A-Z][A-Z0-9_]+)[\"']")


def commenti_esempio(percorso: Path) -> dict[str, str]:
    """Variabile -> commento che la precede.

    Un blocco di commento descrive la variabile che lo segue subito; le
    variabili successive dello stesso gruppo lo ereditano solo se il blocco le
    nomina. Righe vuote e separatori chiudono il blocco, così i titoli di
    sezione e le intestazioni del file non finiscono nelle descrizioni."""
    if not percorso.is_file():
        return {}
    descrizioni: dict[str, str] = {}
    blocco: list[str] = []
    prima = True
    for riga in leggi(percorso).split("\n"):
        pulita = riga.strip()
        if not pulita or _SEPARATORE.match(pulita):
            blocco, prima = [], True
            continue
        if pulita.startswith("#"):
            if not prima:
                blocco, prima = [], True
            blocco.append(pulita.lstrip("#").strip())
            continue
        variabile = _VARIABILE.match(pulita)
        if not variabile:
            continue
        nome = variabile.group(1)
        testo = " ".join(p for p in blocco if p)
        if testo and (prima or re.search(rf"\b{nome}\b", testo)):
            descrizioni.setdefault(nome, redigi(testo))
        prima = False
    return descrizioni


def _occorrenze(radice: Path, file: list[Path], regex: re.Pattern) -> dict[str, set[str]]:
    trovate: dict[str, set[str]] = {}
    for percorso in file:
        if not percorso.is_file():
            continue
        for corrispondenza in regex.finditer(leggi(percorso)):
            nome = next(g for g in corrispondenza.groups() if g) if corrispondenza.groups() else corrispondenza.group(0)
            trovate.setdefault(nome, set()).add(percorso.relative_to(radice).as_posix())
    return trovate


def _unisci(*mappe: dict[str, set[str]]) -> dict[str, set[str]]:
    risultato: dict[str, set[str]] = {}
    for mappa in mappe:
        for nome, dove in mappa.items():
            risultato.setdefault(nome, set()).update(dove)
    return risultato


def _dove(percorsi: set[str]) -> str:
    return ", ".join(f"`{p}`" for p in sorted(percorsi))


def _tabella_backend(voci: list[dict], descrizioni: dict[str, str]) -> list[str]:
    righe = ["| Variabile | Tipo | Predefinito | Obbligatoria | Descrizione |", "|---|---|---|---|---|"]
    for voce in voci:
        predefinito = voce["predefinito"]
        resa = predefinito if predefinito.startswith("(") or predefinito == "—" else f"`{predefinito}`"
        righe.append(
            f"| `{voce['variabile']}` | {cella(voce['tipo'])} | {cella(resa)} | {cella(voce['obbligatoria'])} "
            f"| {cella(descrizioni.get(voce['variabile'], ''))} |")
    return righe


def componi(radice: Path, dati: dict) -> str:
    esempio_backend = commenti_esempio(radice / "backend/.env.example")
    esempio_deploy = commenti_esempio(radice / "deploy/compose.env.example")
    esempio_frontend = commenti_esempio(radice / "frontend/.env.example")
    note_campi = {v["variabile"] for v in dati["impostazioni"] + dati["sms"]}

    script = sorted((radice / "deploy/remote").glob("*.sh"))
    yml = sorted((radice / "deploy").glob("*.yml"))
    deploy = _unisci(
        _occorrenze(radice, script, _USO_COMPOSE_ENV),
        _occorrenze(radice, yml, _INTERPOLAZIONE),
        {n: {"deploy/compose.env.example"} for n in esempio_deploy},
    )
    ambiente_script = _occorrenze(radice, script, _AMBIENTE_SCRIPT)
    backend_py = sorted((radice / "backend/src").rglob("*.py"))
    altre_backend = {n: d for n, d in _occorrenze(radice, backend_py, _GETENV).items() if n not in note_campi}
    sorgenti_frontend = sorted(p for p in (radice / "frontend/src").rglob("*") if p.suffix in (".js", ".jsx"))
    frontend = _unisci(
        _occorrenze(radice, sorgenti_frontend + [radice / "frontend/Dockerfile", radice / "deploy/compose.yml"], _VITE),
        _occorrenze(radice, [radice / "frontend/vite.config.js"], _ENV_VITE_CONFIG),
        {n: {"frontend/.env.example"} for n in esempio_frontend},
    )

    righe = [intestazione(
        "Variabili di configurazione",
        "`backend/src/config.py`, `backend/src/notifiche/config_sms.py`, i file `.env.example` "
        "e gli script di `deploy/`").rstrip(), ""]
    righe += [
        "Nomi, valori predefiniti e obbligatorietà delle variabili. I valori reali non compaiono mai: "
        "i segreti sono indicati con \"—\". Come preparare l'ambiente: "
        "[sviluppo locale](../sviluppo-locale.md) e [deploy](../deploy.md).",
        "",
        "## Backend (`backend/.env`)",
        "",
        "Letto da `backend/src/config.py`. \"Obbligatoria\" indica le variabili senza le quali la verifica "
        "di avvio rifiuta di partire, ricavate dal codice: \"sì\" in ogni ambiente, \"in produzione\" solo "
        "con `ERSAF_ENV=produzione`. La verifica controlla anche coerenza e formato di altri valori.",
        "",
    ]
    righe += _tabella_backend(dati["impostazioni"], esempio_backend)
    righe += ["", "## SMS (`backend/.env`)", "", "Letto da `backend/src/notifiche/config_sms.py`.", ""]
    righe += _tabella_backend(dati["sms"], esempio_backend)
    if altre_backend:
        righe += ["", "## Altre variabili lette dal backend", "", "| Variabile | Dove |", "|---|---|"]
        righe += [f"| `{n}` | {_dove(d)} |" for n, d in sorted(altre_backend.items())]
    righe += [
        "", "## Deploy (`compose.env` sul server)", "",
        "Gestito dagli script di deploy; non contiene segreti.", "",
        "| Variabile | Dove | Descrizione |", "|---|---|---|",
    ]
    righe += [f"| `{n}` | {_dove(d)} | {cella(esempio_deploy.get(n, ''))} |" for n, d in sorted(deploy.items())]
    if ambiente_script:
        righe += ["", "Variabili d'ambiente facoltative degli script sul server:", "",
                  "| Variabile | Dove |", "|---|---|"]
        righe += [f"| `{n}` | {_dove(d)} |" for n, d in sorted(ambiente_script.items())]
    righe += [
        "", "## Frontend (build e sviluppo)", "",
        "Le variabili `VITE_` finiscono nel codice pubblicato: non devono mai contenere segreti.", "",
        "| Variabile | Dove | Descrizione |", "|---|---|---|",
    ]
    righe += [f"| `{n}` | {_dove(d)} | {cella(esempio_frontend.get(n, ''))} |" for n, d in sorted(frontend.items())]
    return "\n".join(righe).rstrip() + "\n"


def genera(radice: Path) -> str:
    return componi(radice, python_backend("_impostazioni.py", radice))
