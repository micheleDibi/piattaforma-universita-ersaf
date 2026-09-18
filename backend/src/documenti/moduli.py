"""Composizione dei moduli calibrati: le coordinate sono dati, non logica duplicata.

I modelli dichiarano soltanto la sequenza di pagine e i layout condivisi.
Ogni layout contiene campi tipizzati in millimetri: T(esto), G(riglia),
C(asella), F(irma). Un campo sconosciuto o senza valore e' un errore.
"""

from functools import lru_cache
from dataclasses import replace
import json

from src.documenti.impaginazione import Casella, Copertura, Firma, Griglia, Pagina, Testo, impagina
from src.documenti.motore import CARTELLA_MODELLI
from src.documenti.valori_moduli import valori_modulo
from src.documenti.ecampus import pagine as ecampus

TIPI = {"T": Testo, "G": Griglia, "C": Casella, "F": Firma, "M": Copertura}
RIGHE_INSEGNAMENTI = {"ecampus-singoli": 3, "link-singoli": 4, "ssml-singoli": 6}
LAYOUT_COMUNI = {
    "ecampus-privacy": ecampus.PRIVACY.campi,
    "ecampus-dichiarazioni": ecampus.AUTOCERTIFICAZIONE_DICHIARAZIONI.campi,
    "ecampus-carriera": ecampus.AUTOCERTIFICAZIONE_CARRIERA.campi,
    "carriera-senza-tabella": tuple(c for c in ecampus.AUTOCERTIFICAZIONE_CARRIERA.campi
                                    if not getattr(c, "chiave", "").startswith("esami.")
                                    or c.chiave == "esami.universita"),
    "ecampus-foto": ecampus.AUTENTICAZIONE_FOTO.campi,
}


def _campi_layout(layout):
    nome = layout if isinstance(layout, str) else layout["nome"]
    if nome in LAYOUT_COMUNI:
        campi = LAYOUT_COMUNI[nome]
    else:
        righe = json.loads((CARTELLA_MODELLI / "layout" / f"{nome}.json").read_text(encoding="utf-8"))
        campi = tuple(TIPI[tipo](*argomenti) for tipo, *argomenti in righe)
    dy = 0 if isinstance(layout, str) else layout.get("dy", 0)
    return tuple(replace(campo, y=campo.y + dy) for campo in campi)


@lru_cache(maxsize=32)
def pagine_modulo(nome: str) -> tuple[Pagina, ...]:
    """Solo nomi del registro interno; nessun percorso arriva dal chiamante HTTP."""
    configurazione = json.loads((CARTELLA_MODELLI / nome / "pagine.json").read_text(encoding="utf-8"))
    pagine = []
    for pagina in configurazione:
        campi = []
        for layout in pagina["layout"]:
            campi.extend(_campi_layout(layout))
        pagine.append(Pagina(pagina["sfondo"], tuple(campi)))
    return tuple(pagine)


def _continuazione(nome: str, dati: dict, campi: dict) -> tuple[Pagina, ...]:
    capacita = RIGHE_INSEGNAMENTI.get(nome)
    if capacita and len(dati.get("corsi_richiesti", [])) > capacita:
        campi["continuazione.titolo"] = "Insegnamenti richiesti - continuazione della domanda"
        aggiunta = [Testo("continuazione.titolo", 20, 190, 30), Testo("pratica.numero", 163, 199, 15)]
        for i in range(capacita + 1, len(dati["corsi_richiesti"]) + 1):
            y = 50 + (i - capacita - 1) * 24
            aggiunta += [Testo(f"richiesti.{i}.descrizione", 20, 190, y), Testo(f"richiesti.{i}.corso_laurea", 20, 190, y + 7)]
        aggiunta += [Testo("firma.data", 20, 70, 260), Firma(120, 190, 260)]
        return (Pagina(None, tuple(aggiunta)),)
    return ()


def compila(nome: str, dati: dict) -> dict:
    """Stessa pipeline per ogni ente, con dati vuoti lasciati vuoti."""
    campi = valori_modulo(dati, nome)
    pagine = pagine_modulo(nome) + _continuazione(nome, dati, campi)
    return {
        "titolo": f"Domanda di iscrizione - {dati['pratica']['numero']}",
        "pagine": impagina(pagine, campi),
    }
