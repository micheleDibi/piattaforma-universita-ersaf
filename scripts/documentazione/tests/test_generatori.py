from __future__ import annotations

import ast
import json
import shutil
import subprocess

import pytest

from comune import RADICE, leggi
from generatori import ErroreGeneratore
from generatori import configurazione, migrazioni

fastapi = pytest.importorskip("fastapi")

from generatori import api  # noqa: E402

lento = pytest.mark.lento


# --- resa dei tipi dell'OpenAPI ----------------------------------------------
@pytest.mark.parametrize(("schema", "resa"), [
    ({"$ref": "#/components/schemas/Cliente"}, "Cliente"),
    ({"anyOf": [{"type": "string", "maxLength": 3}, {"type": "null"}]}, "string | null"),
    ({"anyOf": [{"type": "null"}, {"type": "integer"}]}, "integer | null"),
    ({"anyOf": [{"type": "number"}, {"type": "string", "pattern": "^x$"}]}, "number | string"),
    ({"type": "string", "format": "date", "title": "Data"}, "string(date)"),
    ({"enum": ["M", "F"], "type": "string"}, '"M" | "F"'),
    ({"const": "totp", "type": "string"}, '"totp"'),
    ({"type": "array", "items": {"$ref": "#/components/schemas/Opzione"}}, "list[Opzione]"),
    ({"type": "array"}, "list"),
    ({"type": "object", "additionalProperties": True}, "dict"),
    ({"type": "object", "additionalProperties": {"type": "integer"}}, "dict[str, integer]"),
    ({"type": "object", "properties": {"a": {"type": "string"}}}, "object"),
    ({"allOf": [{"$ref": "#/components/schemas/X"}]}, "X"),
    ({}, "qualsiasi"),
    ({"title": "Documento", "description": "…"}, "qualsiasi"),
])
def test_resa_dei_tipi(schema, resa):
    assert api.tipo(schema) == resa


@pytest.mark.parametrize("schema", [
    {"type": "string", "discriminator": {}},
    {"$ref": "#/x", "nullable": True},
    {"allOf": [{"$ref": "#/a"}, {"$ref": "#/b"}]},
    {"type": "file"},
    [],
])
def test_forme_non_previste_fermano_il_generatore(schema):
    with pytest.raises(ErroreGeneratore):
        api.tipo(schema)


def test_componi_operazioni_e_modelli():
    dati = {
        "accessi": {"get /x/{id}": "sessione", "post /auth/verifica": "sfida", "get /pdf": "pubblica"},
        "openapi": {
            "paths": {
                "/x/{id}": {"get": {"tags": ["X"], "summary": "Leggi X", "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/c/X"}}}},
                                  "422": {"content": {"application/json": {}}}}}},
                "/auth/verifica": {"post": {"summary": "Verifica", "requestBody": {"required": True, "content": {
                    "application/json": {"schema": {"$ref": "#/c/Sfida"}}}},
                    "responses": {"204": {}}}},
                "/pdf": {"get": {"tags": ["X"], "summary": "Pdf",
                                 "responses": {"200": {"content": {"application/pdf": {}}}}}},
            },
            "components": {"schemas": {
                "X": {"type": "object", "properties": {"b": {"type": "string"}, "a": {"type": "integer"}},
                      "required": ["a"]},
                "Stato": {"enum": ["uno", "due"], "type": "string"},
                "ValidationError": {"type": "object"},
            }},
        },
    }
    testo = api.componi(dati)
    assert "### `GET /x/{id}`" in testo and "- **Accesso**: sessione" in testo
    assert "`id` (path, obbligatorio): `integer`" in testo
    assert "- **Risposta**: `200` `X`" in testo and "422" not in testo.split("## Modelli")[1]
    assert "- **Risposta**: `204` nessun contenuto" in testo
    assert "`200` application/pdf" in testo
    dati["openapi"]["paths"]["/pdf"]["get"]["responses"]["200"]["content"] = {"application/json": {"schema": {}}}
    assert "`200` schema non dichiarato" in api.componi(dati)
    assert "## Altre operazioni" in testo and "sfida di accesso" in testo
    assert "| `a` | `integer` | sì |\n| `b` | `string` | no |" in testo
    assert 'Valori: "uno" | "due".' in testo and "ValidationError" not in testo
    dati["accessi"].pop("get /pdf")
    with pytest.raises(ErroreGeneratore):
        api.componi(dati)


def test_dipendenze_dei_router_annidati_sono_visibili():
    """Il generatore conta su iter_route_contexts: se FastAPI la toglie o
    smette di unire le dipendenze del router padre, questo test fallisce."""
    from fastapi import APIRouter, Depends, FastAPI
    from fastapi.routing import APIRoute, iter_route_contexts

    def sessione():
        return 1

    padre = APIRouter(prefix="/padre", dependencies=[Depends(sessione)])
    figlio = APIRouter()

    @figlio.get("/figlia")
    def figlia():
        return {}

    padre.include_router(figlio)
    app = FastAPI()
    app.include_router(padre)
    [contesto] = [c for c in iter_route_contexts(app.routes) if isinstance(c.original_route, APIRoute)]
    assert contesto.path_format == "/padre/figlia"
    assert sessione in {d.call for d in contesto.dependant.dependencies}


@lento
def test_accessi_dell_applicazione_coincidono_con_le_rotte_pubbliche_attese():
    from generatori import python_backend

    sorgente = leggi(RADICE / "backend/tests/security/test_rotte_protette.py")
    albero = ast.parse(sorgente)
    [assegnazione] = [n for n in albero.body if isinstance(n, ast.Assign)
                      and any(getattr(t, "id", None) == "PUBBLICHE" for t in n.targets)]
    attese = {(m.lower(), p) for m, p in ast.literal_eval(assegnazione.value)}
    accessi = python_backend("_openapi.py", RADICE)["accessi"]
    senza_sessione = {tuple(chiave.split(" ", 1)) for chiave, valore in accessi.items() if valore != "sessione"}
    assert senza_sessione == attese
    sfide = {chiave for chiave, valore in accessi.items() if valore == "sfida"}
    assert sfide == {"post /auth/verifica-otp", "post /auth/rigenera-otp", "post /auth/mfa/verifica-totp",
                     "post /auth/mfa/verifica-passkey", "post /auth/mfa/metodo"}


# --- migrazioni --------------------------------------------------------------
def test_descrizione_delle_intestazioni():
    assert migrazioni.descrizione("-- ====\n-- 001 - TITOLO (x)\n-- ====\n-- DB : segreto\n") == ("TITOLO (x)", True)
    assert migrazioni.descrizione("-- 014 - Breve.\n-- altro\nSELECT 1;") == ("Breve", True)
    assert migrazioni.descrizione("-- Senza numero.\nCREATE TABLE x;") == ("Senza numero", False)
    assert migrazioni.descrizione("CREATE TABLE x;") == ("", False)


def test_anomalie_calcolate(tmp_path):
    (tmp_path / "db/migrations").mkdir(parents=True)
    (tmp_path / "db/rollback").mkdir(parents=True)
    for nome, testo in [("001_uno.sql", "-- 001 - Uno\n"), ("003_tre.sql", "-- Tre, scrivere a nome@esempio.it\n"),
                        ("004_quattro.sql", "-- 004 - Quattro\n"), ("Nome_Strano.sql", "")]:
        (tmp_path / "db/migrations" / nome).write_text(testo, encoding="utf-8")
    for nome in ("001_uno_down.sql", "003_tre.sql", "009_orfano_down.sql"):
        (tmp_path / "db/rollback" / nome).write_text("", encoding="utf-8")
    elenco, anomalie = migrazioni.leggi_migrazioni(tmp_path)
    assert [(m.numero, m.rollback, m.rollback_regolare) for m in elenco] == [
        (1, "001_uno_down.sql", True), (3, "003_tre.sql", False), (4, None, False)]
    assert elenco[1].descrizione == "Tre, scrivere a [email]"
    assert anomalie == [
        "`db/migrations/Nome_Strano.sql`: nome fuori dallo schema `NNN_nome.sql`.",
        "Il numero 002 non è usato.",
        "Il rollback della 003 si chiama `003_tre.sql`, senza il suffisso `_down`.",
        "L'intestazione della 003 non riporta il numero.",
        "La 004 non ha un file di rollback.",
        "`db/rollback/009_orfano_down.sql` non corrisponde a nessuna migrazione.",
    ]


# --- configurazione ----------------------------------------------------------
def test_commenti_degli_esempi(tmp_path):
    esempio = tmp_path / ".env.example"
    esempio.write_text("\n".join([
        "# Intestazione del file",
        "# ------",
        "# Titolo di sezione",
        "# ------",
        "# Descrive A e cita B.",
        "A=1",
        "B=2",
        "C=3",
        "# Solo D, collaudo su https://collaudo.rete.local",
        "D=4",
        "",
        "E=5",
        "# In fondo, senza variabile",
    ]), encoding="utf-8")
    assert configurazione.commenti_esempio(esempio) == {
        "A": "Descrive A e cita B.", "B": "Descrive A e cita B.", "D": "Solo D, collaudo su https://[dominio]"}


def test_i_predefiniti_passano_dalla_redazione():
    dati = {"impostazioni": [{"variabile": "HOST", "tipo": "testo", "predefinito": "collaudo.rete.local",
                              "obbligatoria": "no", "campo": "host"}], "sms": []}
    testo = configurazione.componi(RADICE, dati)
    assert "collaudo.rete.local" not in testo and "`[dominio]`" in testo


@lento
def test_variabili_trovate_nel_repository():
    from generatori import python_backend

    dati = python_backend("_impostazioni.py", RADICE)
    testo = configurazione.componi(RADICE, dati)
    for nome in ("DATABASE_URL", "TOTP_CHIAVE", "SMS_BACKEND", "SKEBBY_USER_KEY", "TEST_DATABASE_URL",
                 "RELEASE_TAG", "WEB_LAN_IP", "NOTIFICHE_REALI", "ERSAF_DEPLOY_BASE", "VERSIONE_NUMERO",
                 "VITE_API_BASE_URL", "VITE_VERSIONE", "VITE_AGGIORNATA_IL", "ERSAF_API_PROXY"):
        assert f"`{nome}`" in testo, nome
    obbligo = {v["variabile"]: v["obbligatoria"] for v in dati["impostazioni"] + dati["sms"]}
    assert obbligo["DATABASE_URL"] == obbligo["SESSION_TOKEN_PEPPER"] == obbligo["TOTP_CHIAVE"] == "sì"
    assert obbligo["FRONTEND_BASE_URL"] == obbligo["EMAIL_BACKEND"] == obbligo["SMTP_HOST"] == "in produzione"
    assert obbligo["SMS_BACKEND"] == "in produzione (skebby)"
    assert obbligo["SKEBBY_ACCESS_TOKEN"] == "con SMS_BACKEND=skebby"
    assert obbligo["BCRYPT_COST"] == obbligo["WEBAUTHN_RP_ID"] == "no"
    predefiniti = {v["variabile"]: v["predefinito"] for v in dati["impostazioni"]}
    assert predefiniti["SMTP_FROM"] == "(valore nel codice)"
    assert predefiniti["PASSWORD_MIN_LENGTH"] == "8"


# --- rotte del frontend ------------------------------------------------------
def _frontend_di_prova(tmp_path, app_jsx: str):
    reale = RADICE / "frontend"
    finto = tmp_path / "frontend"
    (finto / "src/config").mkdir(parents=True)
    shutil.copy(reale / "package.json", finto / "package.json")
    try:
        (finto / "node_modules").symlink_to(reale / "node_modules", target_is_directory=True)
    except OSError:
        pytest.skip("collegamenti simbolici non consentiti su questo sistema")
    shutil.copytree(reale / "src/config/routes", finto / "src/config/routes")
    shutil.copy(reale / "src/config/icone.js", finto / "src/config/icone.js")
    (finto / "src/App.jsx").write_text(app_jsx, encoding="utf-8")
    return finto


def _esegui_rotte(frontend):
    from generatori import CARTELLA

    return subprocess.run(["node", str(CARTELLA / "rotte_frontend.mjs"), str(frontend)],
                          capture_output=True, encoding="utf-8")


@lento
def test_rotte_del_repository():
    from generatori import rotte

    dati = rotte.leggi_rotte(RADICE)
    percorsi = {r["percorso"]: r for r in dati["rotte"]}
    assert percorsi["/"]["accesso"] == "solo ospiti"
    assert percorsi["/attuatori/nuovo"]["proprieta"] == {"tipoUtente": "attuatore"}
    assert percorsi["*"]["pagina"] == "PaginaNonTrovata"
    assert {v["rotta"] for v in dati["menu"] if v["soloNazionale"]} >= {"/prodotti"}
    voci = {v["rotta"]: v for v in dati["menu"]}
    assert voci["/dashboard"]["ruoli"] == list(rotte.RUOLI_CON_ACCESSO)
    assert voci["/prodotti"]["ruoli"] == ["nazionale"]
    testo = rotte.componi(dati)
    assert "| `/dashboard` | `Dashboard` | sessione | Dashboard |" in testo
    assert "Prodotti formativi (solo Nazionale) |" in testo


@pytest.mark.parametrize(("voce", "atteso"), [
    ({"soloNazionale": False, "ruoli": ["nazionale", "regionale", "provinciale", "aderente"]}, ""),
    ({"soloNazionale": True, "ruoli": ["nazionale"]}, "solo Nazionale"),
    ({"soloNazionale": False, "ruoli": ["nazionale", "regionale", "provinciale"]},
     "Nazionale, Regionale, Provinciale"),
    ({"soloNazionale": False, "ruoli": []}, "nessuno"),
    ({"soloNazionale": True}, "solo Nazionale"),  # dati senza l'elenco dei ruoli
    ({"soloNazionale": False}, ""),
])
def test_chi_vede_una_voce_del_menu(voce, atteso):
    from generatori import rotte

    assert rotte.chi_vede(voce) == atteso


@lento
def test_forma_sconosciuta_di_app_jsx(tmp_path):
    finto = _frontend_di_prova(tmp_path, """
import { ROTTE } from "./config/routes/percorsi.js";
export default function App() {
  const x = ROTTE;
  return <Routes>{condizione ? <Route path={ROTTE.dashboard} element={<Dashboard />} /> : null}</Routes>;
}
""")
    esito = _esegui_rotte(finto)
    assert esito.returncode == 2
    assert "App.jsx:5: espressione fra le rotte non prevista" in esito.stderr


@lento
def test_forma_supportata_minima(tmp_path):
    finto = _frontend_di_prova(tmp_path, """
import { ROTTE } from "./config/routes/percorsi.js";
export default function App() {
  return <Routes><Route path={ROTTE.dashboard} element={<Dashboard modo="x" attivo={true} />} /></Routes>;
}
""")
    esito = _esegui_rotte(finto)
    assert esito.returncode == 0, esito.stderr
    assert json.loads(esito.stdout)["rotte"] == [
        {"percorso": "/dashboard", "pagina": "Dashboard", "proprieta": {"modo": "x", "attivo": True},
         "accesso": "pubblica"}]


# --- genera.py ---------------------------------------------------------------
def test_versioni_diverse(tmp_path):
    import genera

    vincoli = tmp_path / "vincoli.txt"
    vincoli.write_text(f"# commento\nfastapi=={fastapi.__version__}\npacchetto-inesistente==1.0\n", encoding="utf-8")
    assert genera.versioni_diverse(vincoli) == ["pacchetto-inesistente: installata assente, attesa 1.0"]


@lento
def test_verifica_e_manomissione(tmp_path):
    import genera

    uscita = tmp_path / "riferimenti"
    assert genera.esegui(["--uscita", str(uscita)]) == 0
    assert sorted(p.name for p in uscita.iterdir()) == sorted(genera.GENERATORI)
    assert genera.esegui(["--verifica", "--uscita", str(uscita)]) == 0
    pagina = uscita / "migrazioni.md"
    pagina.write_text(pagina.read_text(encoding="utf-8").replace("| 001 |", "| 999 |"), encoding="utf-8")
    assert genera.esegui(["--verifica", "--uscita", str(uscita)]) == 1
    pagina.write_text(genera.GENERATORI["migrazioni.md"](RADICE).replace("\n", "\r\n"), encoding="utf-8",
                      newline="")
    assert genera.esegui(["--verifica", "--uscita", str(uscita)]) == 0


def test_le_pagine_del_repository_sono_aggiornate():
    """Lo stesso controllo della CI, sul repository vero."""
    import genera

    for nome in genera.GENERATORI:
        assert (RADICE / genera.CARTELLA_USCITA / nome).is_file(), nome
