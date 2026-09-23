"""docs/tecnica/riferimenti/rotte-frontend.md da App.jsx e dal menu."""

from __future__ import annotations

from pathlib import Path

from generatori import CARTELLA, cella, esegui_json, intestazione

# Gli stessi di rotte_frontend.mjs: i ruoli che accedono alla piattaforma.
RUOLI_CON_ACCESSO = ("nazionale", "regionale", "provinciale", "aderente")


def chi_vede(voce: dict) -> str:
    """I ruoli che vedono la voce, se non sono tutti quelli che accedono."""
    ruoli = voce.get("ruoli")
    if ruoli is None:  # dati senza l'elenco dei ruoli: vale solo soloNazionale
        return "solo Nazionale" if voce.get("soloNazionale") else ""
    if set(ruoli) >= set(RUOLI_CON_ACCESSO):
        return ""
    if list(ruoli) == ["nazionale"]:
        return "solo Nazionale"
    return ", ".join(ruolo.capitalize() for ruolo in ruoli) if ruoli else "nessuno"


def leggi_rotte(radice: Path) -> dict:
    frontend = radice / "frontend"
    if not (frontend / "node_modules" / "@babel" / "core").is_dir():
        from generatori import ErroreGeneratore
        raise ErroreGeneratore("mancano le dipendenze del frontend: eseguire `npm ci` in frontend/")
    return esegui_json(["node", str(CARTELLA / "rotte_frontend.mjs"), str(frontend)], radice)


def _pagina(rotta: dict) -> str:
    proprieta = rotta.get("proprieta") or {}
    dettagli = ", ".join(f"{k}={str(v).lower() if isinstance(v, bool) else v}" for k, v in proprieta.items())
    return f"`{rotta['pagina']}`" + (f" ({dettagli})" if dettagli else "")


def componi(dati: dict) -> str:
    menu = {voce["rotta"]: voce for voce in dati["menu"]}
    righe = [intestazione("Pagine del frontend",
                          "`frontend/src/App.jsx` e `frontend/src/config/routes/`").rstrip(), ""]
    righe += [
        "Pagine registrate nell'applicazione web, nell'ordine in cui sono dichiarate.",
        "",
        "- **Accesso**: `pubblica` per tutti; `solo ospiti` rimanda all'applicazione chi ha già una "
        "sessione; `sessione` richiede di aver effettuato l'accesso.",
        "- **Menu**: la voce del menu laterale, se esiste. Fra parentesi i ruoli che la vedono, quando "
        "non sono tutti quelli che accedono. Agli altri la voce è nascosta, ma la pagina resta "
        "raggiungibile digitando l'indirizzo: vedi i [limiti noti](../sicurezza.md#limiti-noti).",
        "",
        "| Percorso | Pagina | Accesso | Menu |",
        "|---|---|---|---|",
    ]
    for rotta in dati["rotte"]:
        voce = menu.get(rotta["percorso"])
        if voce:
            limite = chi_vede(voce)
            testo_menu = voce["etichetta"] + (f" ({limite})" if limite else "")
        else:
            testo_menu = "—"
        righe.append(f"| `{rotta['percorso']}` | {cella(_pagina(rotta))} | {rotta['accesso']} | "
                     f"{cella(testo_menu)} |")
    senza_pagina = [v for v in dati["menu"] if v["rotta"] not in {r["percorso"] for r in dati["rotte"]}]
    if senza_pagina:
        righe += ["", "Voci di menu senza una pagina registrata:", ""]
        righe += [f"- `{v['rotta']}` ({v['etichetta']})" for v in senza_pagina]
    return "\n".join(righe).rstrip() + "\n"


def genera(radice: Path) -> str:
    return componi(leggi_rotte(radice))
