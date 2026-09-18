"""Accordo eCampus condiviso da tutti i moduli, compilato con le rate salvate."""

from src.documenti.impaginazione import CENTRO, DESTRA, Firma, Pagina, Testo, impagina


def _valori(dati: dict) -> dict:
    cliente, pratica = dati["cliente"], dati["pratica"]
    residenza = cliente["residenza"]
    indirizzo = " ".join(filter(None, (residenza["indirizzo"], residenza["civico"])))
    comune = " ".join(filter(None, (residenza["cap"], residenza["comune"], residenza["provincia"])))
    return {
        "nome": " ".join(filter(None, (cliente["nome"], cliente["cognome"]))),
        "nascita.luogo": cliente["luogo_nascita"], "nascita.data": cliente["data_nascita"],
        "residenza": ", ".join(filter(None, (indirizzo, comune))),
        "data": pratica["data_creazione"], "luogo": dati["azienda"]["citta"],
        "prezzo": pratica["prezzo"], "corso": dati["corso"]["descrizione"],
        "pratica": pratica["numero"],
        "continuazione": "Accordo per la rateizzazione della retta - continuazione",
        "rinvio": "Il piano prosegue nelle pagine successive.",
        "colonna.rata": "Rata", "colonna.importo": "Importo (€)", "colonna.scadenza": "Scadenza",
    }


def _accordo(valori: dict, rate: list[dict]) -> Pagina:
    campi = [
        Testo("data", 165.5, 194.3, 55.2, CENTRO),
        Testo("nome", 15.2, 66, 87.7), Testo("nascita.luogo", 78.2, 119.1, 87.7),
        Testo("nascita.data", 122.8, 162.9, 87.7, CENTRO),
        Testo("residenza", 10, 62.6, 93.1),
        Testo("prezzo", 47.7, 80.5, 102, CENTRO), Testo("corso", 51.6, 190.4, 107.5),
        Testo("data", 31, 55.8, 187.5, CENTRO), Testo("luogo", 59.6, 99.8, 187.5),
        Firma(127.3, 186.5, 215.6),
    ]
    for i, rata in enumerate(rate[:12]):
        y = 125.6 + (i // 2) * 4.96
        x_importo, x_data = ((18.6, 55) if i % 2 == 0 else (120.7, 158.4))
        valori[f"importo.{i}"] = rata["importo"]
        valori[f"data.{i}"] = rata["data"]
        campi += [Testo(f"importo.{i}", x_importo, x_importo + 18, y, DESTRA),
                  Testo(f"data.{i}", x_data, x_data + 31.5, y, CENTRO)]
    if len(rate) > 12:
        campi.append(Testo("rinvio", 10, 192, 158))
    return Pagina("_comune/sfondi/ecampus-rateizzazione.jpg", tuple(campi))


def _continuazioni(valori: dict, rate: list[dict]) -> tuple[Pagina, ...]:
    pagine = []
    for inizio in range(12, len(rate), 24):
        campi = [Testo("continuazione", 20, 190, 25), Testo("pratica", 150, 190, 35),
                 Testo("nome", 20, 145, 35), Testo("corso", 20, 190, 43),
                 Testo("colonna.rata", 20, 35, 55), Testo("colonna.importo", 50, 95, 55, DESTRA),
                 Testo("colonna.scadenza", 110, 160, 55, CENTRO)]
        for posizione, rata in enumerate(rate[inizio:inizio + 24]):
            indice = inizio + posizione
            valori[f"numero.{indice}"] = str(indice + 1)
            valori[f"importo.{indice}"] = rata["importo"]
            valori[f"data.{indice}"] = rata["data"]
            y = 64 + posizione * 7
            campi += [Testo(f"numero.{indice}", 20, 35, y),
                      Testo(f"importo.{indice}", 50, 95, y, DESTRA),
                      Testo(f"data.{indice}", 110, 160, y, CENTRO)]
        campi += [Testo("data", 20, 60, 267), Testo("luogo", 65, 110, 267), Firma(125, 190, 267)]
        pagine.append(Pagina(None, tuple(campi)))
    return tuple(pagine)


def pagine_rateizzazione(dati: dict) -> list[dict]:
    """Nessun accordo senza rate; oltre dodici, continuazione senza troncamenti."""
    rate = dati.get("rateizzazione", [])
    if not rate:
        return []
    valori = _valori(dati)
    pagine = (_accordo(valori, rate), *_continuazioni(valori, rate))
    return impagina(pagine, valori)
