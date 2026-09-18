"""Domanda di immatricolazione ai corsi di laurea eCampus: prima pagina e modulo completo."""

from __future__ import annotations

from src.documenti.ecampus.pagine import PAGINE_SUCCESSIVE, con_numero_pratica
from src.documenti.ecampus.valori import valori
from src.documenti.impaginazione import CENTRO, DESTRA, Casella, Pagina, Testo, data, impagina, luogo_data_firma

NOME = "ecampus-laurea"

DOMANDA = Pagina("pagina-01.jpg", (
    Testo("cognome", 48.1, 105.2, 70.8), Testo("nome", 115.2, 176.4, 70.8),
    Casella("sesso.m", 184.9, 68.1, 2.2), Casella("sesso.f", 193.2, 68.1, 2.2),
    *data("nascita", 75.7, (24.6, 30.6), (31.5, 37.6), (38.4, 47.4)),
    Testo("nascita.luogo", 50.0, 122.9, 75.7), Testo("nascita.provincia", 125.5, 134.4, 75.7, CENTRO),
    Testo("nascita.stato", 143.8, 197.4, 75.7),
    Testo("cittadinanza", 28.4, 105.8, 80.6), Testo("codice_fiscale", 116.0, 197.0, 80.6),
    Testo("residenza.indirizzo", 39.6, 197.3, 87.0),
    Testo("residenza.cap", 18.6, 46.9, 92.0, CENTRO), Testo("residenza.comune", 58.8, 185.1, 92.0),
    Testo("residenza.provincia", 186.9, 195.9, 92.0, CENTRO),
    Testo("corrispondenza.indirizzo", 78.4, 197.4, 96.9),
    Testo("corrispondenza.cap", 18.6, 46.9, 101.8, CENTRO), Testo("corrispondenza.comune", 58.8, 185.1, 101.8),
    Testo("corrispondenza.provincia", 186.9, 195.9, 101.8, CENTRO),
    Testo("telefono.prefisso", 19.5, 30.1, 106.8, CENTRO), Testo("telefono.numero", 31.0, 72.6, 106.8),
    Testo("email.utente", 81.8, 151.7, 106.8, DESTRA), Testo("email.dominio", 155.6, 197.3, 106.8),
    Testo("anno_accademico.inizio", 110.2, 125.1, 128.7, CENTRO), Testo("anno_accademico.fine", 126.5, 141.4, 128.7, CENTRO),
    Casella("immatricolazione", 73.2, 129.9, 2.5), Casella("iscrizione", 97.9, 129.9, 2.5),
    Testo("corso", 53.7, 182.7, 141.2), Testo("curriculum", 55.9, 184.9, 147.0),
    Casella("livello.primo", 53.9, 150.0, 2.5), Casella("livello.secondo", 60.3, 150.0, 2.5),
    Casella("livello.ciclo_unico", 67.7, 150.0, 2.5),
    Casella("corso_innovativo.si", 117.9, 150.2, 2.2), Casella("corso_innovativo.no", 125.0, 150.2, 2.2),
    Casella("anno.1", 149.0, 150.0, 2.5), Casella("anno.2", 155.6, 150.0, 2.5), Casella("anno.3", 162.9, 150.0, 2.5),
    Casella("servizi.aderisce", 107.5, 162.9, 2.2), Casella("servizi.non_aderisce", 144.1, 162.9, 2.2),
    Testo("retta", 164.6, 187.6, 196.1, DESTRA), Testo("servizi_integrativi", 167.1, 186.3, 203.0, DESTRA),
    *luogo_data_firma(265.85, (23.88, 82.63), (91.44, 117.69), (131.06, 196.09)),
))

# Sulla prima pagina il numero sta un poco piu' in basso, sopra le righe delle matricole.
PAGINE = (con_numero_pratica(DOMANDA, Testo("pratica.numero", 164.5, 200.0, 16.6)), *PAGINE_SUCCESSIVE)


def arricchisci(dati: dict) -> dict:
    """Quello che legge il modulo Typst: il titolo del PDF e le pagine con i campi gia' scritti."""
    numero = dati["pratica"]["numero"]
    titolo = "Domanda di immatricolazione eCampus" + (f", pratica {numero}" if numero else "")
    return {"titolo": titolo, "pagine": impagina(PAGINE, valori(dati))}
