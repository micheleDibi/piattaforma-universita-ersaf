"""Sottoprocesso: stampa in JSON l'OpenAPI e l'accesso richiesto da ogni rotta."""

from __future__ import annotations

import json
import sys

from _avvio import importa_app


def dipendenze(dependant, trovate):
    for figlia in dependant.dependencies:
        trovate.add(figlia.call)
        dipendenze(figlia, trovate)
    return trovate


def main(backend: str) -> None:
    app = importa_app(backend).app
    from fastapi.openapi.utils import get_openapi
    from fastapi.routing import APIRoute, iter_route_contexts

    from src.auth.dipendenze import get_current_utente, get_sessione_corrente
    from src.otp.schemas import RichiestaSfida

    sessione = {get_current_utente, get_sessione_corrente}
    accessi = {}
    # iter_route_contexts restituisce la rotta effettiva: le dipendenze dei
    # router che includono altri router sono nel suo dependant.
    for contesto in iter_route_contexts(app.routes):
        if not isinstance(contesto.original_route, APIRoute):
            continue
        campo = contesto.body_field
        corpo = campo.field_info.annotation if campo is not None else None
        if sessione & dipendenze(contesto.dependant, set()):
            accesso = "sessione"
        elif isinstance(corpo, type) and issubclass(corpo, RichiestaSfida):
            accesso = "sfida"
        else:
            accesso = "pubblica"
        for metodo in contesto.methods:
            accessi[f"{metodo.lower()} {contesto.path_format}"] = accesso

    schema = get_openapi(title=app.title, version="0", routes=app.routes,
                         separate_input_output_schemas=False)
    json.dump({"openapi": schema, "accessi": accessi}, sys.stdout, ensure_ascii=True, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1])
