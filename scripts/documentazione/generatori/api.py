"""docs/tecnica/riferimenti/api.md dall'OpenAPI dell'applicazione."""

from __future__ import annotations

import json
from pathlib import Path

from generatori import ErroreGeneratore, cella, intestazione, python_backend

# Chiavi che descrivono o vincolano un valore ma non ne cambiano il tipo.
METADATI = frozenset({
    "title", "description", "default", "examples", "example", "deprecated", "readOnly", "writeOnly",
    "maxLength", "minLength", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "pattern", "multipleOf", "maxItems", "minItems", "uniqueItems", "format", "contentMediaType",
})
STRUTTURA = frozenset({"type", "items", "additionalProperties", "properties", "required"})
ORDINE_METODI = ("get", "post", "put", "patch", "delete", "head", "options")
ACCESSI = {
    "pubblica": "pubblica",
    "sfida": "sfida di accesso (dopo la password, prima della sessione)",
    "sessione": "sessione",
}
ESCLUSI = frozenset({"HTTPValidationError", "ValidationError"})


def nome_riferimento(riferimento: str) -> str:
    return riferimento.rsplit("/", 1)[-1]


def tipo(schema) -> str:
    """Resa sintetica e stabile di uno schema JSON dell'OpenAPI."""
    if not isinstance(schema, dict):
        raise ErroreGeneratore(f"schema non valido: {schema!r}")
    chiavi = set(schema) - METADATI
    if not chiavi:
        formato = schema.get("format")
        return f"qualsiasi({formato})" if formato else "qualsiasi"
    if "$ref" in chiavi:
        if chiavi != {"$ref"}:
            raise ErroreGeneratore(f"$ref con altre chiavi: {sorted(chiavi)}")
        return nome_riferimento(schema["$ref"])
    for combinazione in ("anyOf", "oneOf"):
        if combinazione in chiavi:
            if chiavi != {combinazione}:
                raise ErroreGeneratore(f"{combinazione} con altre chiavi: {sorted(chiavi)}")
            parti = []
            for alternativa in schema[combinazione]:
                resa = tipo(alternativa)
                if resa not in parti:
                    parti.append(resa)
            parti.sort(key=lambda p: p == "null")
            return " | ".join(parti)
    if "allOf" in chiavi:
        if chiavi != {"allOf"} or len(schema["allOf"]) != 1:
            raise ErroreGeneratore(f"allOf non previsto: {schema}")
        return tipo(schema["allOf"][0])
    if "const" in chiavi:
        if chiavi - {"const", "type"}:
            raise ErroreGeneratore(f"const con altre chiavi: {sorted(chiavi)}")
        return json.dumps(schema["const"], ensure_ascii=False)
    if "enum" in chiavi:
        if chiavi - {"enum", "type"}:
            raise ErroreGeneratore(f"enum con altre chiavi: {sorted(chiavi)}")
        return " | ".join(json.dumps(v, ensure_ascii=False) for v in schema["enum"])
    if chiavi - STRUTTURA:
        raise ErroreGeneratore(f"forma di schema non prevista: {sorted(chiavi - STRUTTURA)}")
    genere = schema.get("type")
    if isinstance(genere, list):
        return " | ".join(genere)
    if genere == "array":
        return f"list[{tipo(schema['items'])}]" if "items" in schema else "list"
    if genere == "object":
        extra = schema.get("additionalProperties")
        if isinstance(extra, dict):
            return f"dict[str, {tipo(extra)}]"
        return "dict" if extra is True else "object"
    if genere in ("string", "integer", "number", "boolean", "null"):
        formato = schema.get("format")
        return f"{genere}({formato})" if formato else genere
    raise ErroreGeneratore(f"tipo non previsto: {genere!r}")


def _corpo(operazione: dict) -> str:
    corpo = operazione.get("requestBody")
    if not corpo:
        return "—"
    parti = []
    for media, contenuto in sorted(corpo.get("content", {}).items()):
        resa = tipo(contenuto.get("schema", {}))
        parti.append(f"`{resa}` ({media})")
    obbligatorio = " obbligatorio" if corpo.get("required") else ""
    return ", ".join(parti) + obbligatorio


def _risposte(operazione: dict) -> str:
    parti = []
    for codice, risposta in sorted(operazione.get("responses", {}).items()):
        if codice == "422" or not codice.startswith("2"):
            continue
        contenuti = risposta.get("content", {})
        if not contenuti:
            parti.append(f"`{codice}` nessun contenuto")
            continue
        for media, contenuto in sorted(contenuti.items()):
            if media == "application/json":
                parti.append(f"`{codice}` `{tipo(contenuto.get('schema', {}))}`")
            else:
                parti.append(f"`{codice}` {media}")
    return ", ".join(parti) or "—"


def _parametri(operazione: dict) -> str:
    parti = []
    for parametro in sorted(operazione.get("parameters", []), key=lambda p: (p["in"], p["name"])):
        obbligo = ", obbligatorio" if parametro.get("required") else ""
        parti.append(f"`{parametro['name']}` ({parametro['in']}{obbligo}): `{tipo(parametro.get('schema', {}))}`")
    return "; ".join(parti) or "—"


def _modello(nome: str, schema: dict) -> list[str]:
    righe = [f"### {nome}", ""]
    if "enum" in schema:
        righe += [f"Valori: {tipo(schema)}.", ""]
        return righe
    if schema.get("type") != "object":
        return righe + [f"Tipo: `{tipo(schema)}`.", ""]
    proprieta = schema.get("properties", {})
    if not proprieta:
        return righe + ["Nessun campo dichiarato.", ""]
    obbligatori = set(schema.get("required", []))
    righe += ["| Campo | Tipo | Obbligatorio |", "|---|---|---|"]
    for campo in sorted(proprieta):
        righe.append(f"| `{campo}` | `{cella(tipo(proprieta[campo]))}` | "
                     f"{'sì' if campo in obbligatori else 'no'} |")
    return righe + [""]


def componi(dati: dict) -> str:
    openapi, accessi = dati["openapi"], dati["accessi"]
    gruppi: dict[str, list[tuple[str, str, dict]]] = {}
    for percorso, operazioni in openapi.get("paths", {}).items():
        for metodo, operazione in operazioni.items():
            if metodo not in ORDINE_METODI:
                raise ErroreGeneratore(f"metodo non previsto: {metodo} {percorso}")
            chiave = f"{metodo} {percorso}"
            if chiave not in accessi:
                raise ErroreGeneratore(f"accesso sconosciuto per {chiave}")
            tag = (operazione.get("tags") or ["Senza categoria"])[0]
            gruppi.setdefault(tag, []).append((percorso, metodo, operazione))

    righe = [intestazione("Riferimento delle API", "`backend/src/main.py` (OpenAPI dell'applicazione)").rstrip(), ""]
    righe += [
        "Elenco delle operazioni esposte dal backend, raggruppate per categoria. Per ognuna:",
        "",
        "- **Accesso**: `pubblica`; `sfida di accesso` quando serve la sfida ottenuta con la password, "
        "prima che esista una sessione; `sessione` quando serve il cookie di sessione.",
        "- Le richieste che modificano dati passano anche dai controlli del browser e dal token CSRF "
        "descritti in [sicurezza](../sicurezza.md).",
        "- I controlli sul ruolo avvengono dentro le operazioni e qui non compaiono: vedi "
        "[ruoli e permessi](../../funzionale/ruoli-e-permessi.md) e i "
        "[limiti noti](../sicurezza.md#limiti-noti).",
        "- La risposta `422` per i dati non validi vale per tutte le operazioni con parametri o corpo "
        "e non viene ripetuta.",
        "",
    ]
    for tag in sorted(gruppi):
        righe += [f"## {tag}", ""]
        for percorso, metodo, operazione in sorted(
                gruppi[tag], key=lambda o: (o[0], ORDINE_METODI.index(o[1]))):
            righe += [
                f"### `{metodo.upper()} {percorso}`",
                "",
                f"{operazione.get('summary', '').strip() or 'Operazione senza titolo'}.",
                "",
                f"- **Accesso**: {ACCESSI[accessi[f'{metodo} {percorso}']]}",
                f"- **Parametri**: {_parametri(operazione)}",
                f"- **Corpo**: {_corpo(operazione)}",
                f"- **Risposta**: {_risposte(operazione)}",
                "",
            ]
    righe += ["## Modelli", ""]
    for nome, schema in sorted(openapi.get("components", {}).get("schemas", {}).items()):
        if nome not in ESCLUSI:
            righe += _modello(nome, schema)
    return "\n".join(righe).rstrip() + "\n"


def genera(radice: Path) -> str:
    return componi(python_backend("_openapi.py", radice))
