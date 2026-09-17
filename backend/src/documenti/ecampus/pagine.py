"""Pagine 2-10 del modulo eCampus: regolamento, privacy, autocertificazione e contratto.

Secondo chi ha preparato i modelli, tra un corso e l'altro cambia soltanto la
prima pagina: queste si riusano. Le misure sono in millimetri (vedi
`src/documenti/impaginazione.py`).
"""

from __future__ import annotations

from src.documenti.impaginazione import (
    CENTRO, DESTRA, SINISTRA, Casella, Firma, Griglia, Pagina, Testo, data, luogo_data_firma,
)

# Riga "Luogo, Data, Firma" comune alle pagine 4, 5 e 6.
FIRMA_AUTOCERTIFICAZIONE = luogo_data_firma(274.66, (23.88, 82.63), (91.44, 117.69), (131.06, 196.09))

# Come nei PDF del gestionale: sul regolamento la data e la firma, ma non il luogo.
REGOLAMENTO = Pagina("pagina-02.jpg", (Testo("firma.data", 92.79, 119.04, 274.66, CENTRO), Firma(127.68, 194.23, 274.66)))

PRIVACY = Pagina("pagina-03.jpg", (
    Casella("privacy.consenso", 64.69, 266.02, 2.2), Casella("privacy.diniego", 105.49, 266.02, 2.2),
    *luogo_data_firma(281.94, (22.01, 77.05), (86.7, 119.38), (129.03, 196.09), altezza=10.0),
))


def _dove(chiave: str, y: float) -> tuple[Testo, Testo]:
    """"della Citta' ____ ( __ )": ricorre uguale in tutta l'autocertificazione."""
    return Testo(f"{chiave}.citta", 35.9, 105.83, y), Testo(f"{chiave}.provincia", 107.87, 116.84, y, CENTRO)


AUTOCERTIFICAZIONE_DICHIARAZIONI = Pagina("pagina-04.jpg", (
    Testo("cognome", 59.77, 121.58, 54.36), Testo("nome", 132.59, 194.39, 54.36),
    Testo("nascita.luogo", 44.7, 151.72, 82.13), Testo("nascita.provincia", 153.59, 162.39, 82.13, CENTRO),
    *data("nascita", 82.13, (165.78, 173.57), (174.41, 182.2), (183.05, 195.07)),
    Griglia("codice_fiscale", 69.6, 164.25, 88.4, 16),
    Testo("residenza.via", 48.77, 181.02, 94.15), Testo("residenza.civico", 184.57, 195.07, 94.15, CENTRO),
    Testo("residenza.comune", 34.54, 149.01, 99.06), Testo("residenza.provincia", 150.71, 159.68, 99.06, CENTRO),
    Testo("residenza.cap", 166.79, 195.07, 99.06, CENTRO),
    Testo("telefono.prefisso", 28.45, 43.52, 103.97, CENTRO), Testo("telefono.numero", 44.87, 82.13, 103.97),
    # Diploma di maturita' e anno integrativo
    Casella("diploma", 90.59, 108.37, 2.2), Testo("diploma.denominazione", 53.68, 195.07, 115.99),
    Casella("diploma.statale", 43.86, 118.19, 2.2), Casella("diploma.paritario", 56.73, 118.19, 2.2),
    Testo("diploma.istituto", 71.63, 195.07, 120.9), *_dove("diploma", 125.98),
    Testo("diploma.anno.inizio", 60.79, 72.98, 130.89, CENTRO), Testo("diploma.anno.fine", 74.0, 86.02, 130.89, CENTRO),
    Testo("diploma.voto", 104.31, 117.86, 130.89, CENTRO), Testo("diploma.voto_massimo", 118.7, 132.08, 130.89, CENTRO),
    Testo("integrativo.istituto", 110.24, 195.07, 137.84), *_dove("integrativo", 142.92),
    Testo("integrativo.anno.inizio", 47.24, 59.44, 147.83, CENTRO), Testo("integrativo.anno.fine", 60.28, 72.47, 147.83, CENTRO),
    Testo("integrativo.voto", 90.76, 104.31, 147.83, CENTRO), Testo("integrativo.voto_massimo", 105.16, 118.53, 147.83, CENTRO),
    Casella("invalidita", 17.61, 152.06, 2.2), Testo("invalidita.percentuale", 116.5, 131.74, 154.77, CENTRO),
    # Carriera universitaria
    Casella("mai_immatricolato", 17.61, 175.09, 2.2), Casella("non_iscritto_altrove", 17.61, 188.47, 2.2),
    Casella("titolo", 17.61, 195.58, 2.2),
    Casella("titolo.diploma_universitario", 23.71, 200.49, 2.2), Casella("titolo.vecchio_ordinamento", 59.1, 200.49, 2.2),
    Casella("titolo.primo_livello", 92.63, 200.49, 2.2), Casella("titolo.secondo_livello", 120.23, 200.49, 2.2),
    Casella("titolo.ciclo_unico", 147.83, 200.49, 2.2),
    Testo("titolo.denominazione", 79.93, 194.39, 208.11), Testo("titolo.universita", 62.31, 194.73, 213.02),
    *data("titolo.data", 223.01, (32.17, 39.79), (40.81, 48.43), (49.28, 61.3)),
    Testo("titolo.voto", 79.59, 93.13, 223.01, CENTRO), Testo("titolo.voto_massimo", 94.15, 107.53, 223.01, CENTRO),
    Casella("trasferimento_rinuncia", 17.61, 227.25, 2.2),
    Casella("trasferimento", 118.87, 227.25, 2.2), Casella("rinuncia", 140.21, 227.25, 2.2),
    *data("lasciata.data", 236.39, (32.34, 39.96), (40.81, 48.6), (49.45, 61.47)),
    Testo("lasciata.universita", 84.67, 194.39, 236.39), *_dove("lasciata", 241.3),
    Casella("decadenza", 17.61, 245.7, 2.2),
    *data("decadenza.data", 254.68, (32.34, 39.96), (40.81, 48.6), (49.45, 61.47)),
    Testo("decadenza.universita", 84.67, 194.39, 254.68), *_dove("decadenza", 259.59),
    *FIRMA_AUTOCERTIFICAZIONE,
))

# Tabella degli esami: linea di fondo di ogni riga e colonne.
RIGHE_TABELLA_ESAMI = (173.91, 178.99, 183.9, 188.81, 193.72, 198.63, 203.54, 208.62,
                       213.53, 218.44, 223.35, 228.26, 233.17, 238.25, 243.16)
COLONNE_TABELLA_ESAMI = (("insegnamento", 27.09, 134.75, SINISTRA), ("data", 134.75, 159.58, CENTRO),
                         ("ssd", 159.58, 179.55, CENTRO), ("voto", 179.55, 193.1, CENTRO))


def _riga_esame(numero: int, fondo: float) -> tuple[Testo, ...]:
    # Il testo sta a meta' riga, non sulla linea di fondo.
    return tuple(Testo(f"esami.{numero}.{colonna}", x0, x1, fondo - 0.4, allinea)
                 for colonna, x0, x1, allinea in COLONNE_TABELLA_ESAMI)


AUTOCERTIFICAZIONE_CARRIERA = Pagina("pagina-05.jpg", (
    Casella("iscritto", 18.12, 38.1, 2.2),
    Casella("iscritto.laurea_primo", 24.05, 56.39, 2.2), Casella("iscritto.laurea_secondo", 51.82, 56.39, 2.2),
    Casella("iscritto.laurea_ciclo_unico", 79.42, 56.39, 2.2), Casella("iscritto.master_primo", 112.44, 56.39, 2.2),
    Casella("iscritto.master_secondo", 140.38, 56.39, 2.2), Casella("iscritto.altro", 24.05, 61.3, 2.2),
    Testo("iscritto.altro_corso", 33.53, 162.73, 64.01),
    Testo("iscritto.classe", 43.35, 59.77, 69.77, CENTRO), Testo("iscritto.denominazione", 80.26, 194.9, 69.77),
    Testo("iscritto.universita", 46.06, 194.9, 74.68),
    Testo("iscritto.citta", 36.24, 106.17, 79.59), Testo("iscritto.provincia", 108.2, 117.18, 79.59, CENTRO),
    Testo("iscritto.anno", 45.04, 62.82, 84.5, CENTRO),
    Casella("iscritto.part_time", 78.91, 81.79, 2.2), Casella("iscritto.full_time", 94.66, 81.79, 2.2),
    Casella("professione", 17.44, 116.84, 2.2), Testo("professione.nome", 108.54, 195.75, 119.55),
    *data("professione.data", 124.46, (31.83, 37.93), (38.78, 46.57), (47.41, 59.44)),
    Testo("professione.presso", 69.43, 195.75, 124.46),
    Casella("albo", 17.44, 128.86, 2.2), Testo("albo.nome", 72.47, 195.75, 131.57),
    Casella("qualifica", 17.44, 135.81, 2.2), Testo("qualifica.nome", 95.0, 195.75, 138.51),
    *data("qualifica.data", 143.59, (31.83, 37.93), (38.78, 46.57), (47.41, 59.44)),
    Testo("qualifica.presso", 69.43, 195.75, 143.59),
    Casella("esami", 17.44, 147.83, 2.2), Testo("esami.universita", 45.72, 194.56, 155.45),
    *(campo for numero, fondo in enumerate(RIGHE_TABELLA_ESAMI, 1) for campo in _riga_esame(numero, fondo)),
    *FIRMA_AUTOCERTIFICAZIONE,
))

# Tipo, casella in alto a sinistra, linea del numero e linea di chi l'ha rilasciato.
DOCUMENTI_IDENTITA = (
    ("carta", 196.26, (53.17, 95.0), (128.02, 194.73)),
    ("passaporto", 202.69, (47.24, 89.07), (126.32, 194.9)),
    ("patente", 208.96, (42.5, 84.33), (121.24, 194.73)),
    ("altro", 215.39, (28.28, 86.7), (106.34, 194.73)),
)


def _documento(tipo: str, y: float, numero: tuple[float, float], rilascio: tuple[float, float]) -> tuple:
    linea = y + 3.05
    return (Casella(f"documento.{tipo}", 23.03, y, 2.2),
            Testo(f"documento.{tipo}.numero", *numero, linea), Testo(f"documento.{tipo}.rilascio", *rilascio, linea))


AUTENTICAZIONE_FOTO = Pagina("pagina-06.jpg", (
    Testo("cognome", 59.61, 121.41, 114.64), Testo("nome", 132.42, 194.23, 114.64),
    Testo("nascita.luogo", 27.26, 138.01, 121.07), Testo("nascita.provincia", 140.38, 153.75, 121.07, CENTRO),
    *data("nascita", 121.07, (159.0, 168.99), (170.18, 180.34), (181.36, 194.73)),
    Testo("residenza.via", 31.83, 180.34, 133.77), Testo("residenza.civico", 184.4, 194.39, 133.77, CENTRO),
    Testo("residenza.comune", 43.86, 140.72, 140.04), Testo("residenza.provincia", 143.09, 156.29, 140.04, CENTRO),
    Testo("residenza.cap", 164.59, 194.56, 140.04, CENTRO),
    Testo("corrispondenza.via", 88.56, 180.51, 152.74), Testo("corrispondenza.civico", 184.4, 194.39, 152.74, CENTRO),
    Testo("corrispondenza.comune", 43.86, 140.72, 159.17),
    Testo("corrispondenza.provincia", 143.09, 156.29, 159.17, CENTRO), Testo("corrispondenza.cap", 164.59, 194.56, 159.17, CENTRO),
    Testo("telefono.prefisso", 19.81, 29.8, 171.87, CENTRO), Testo("telefono.numero", 32.17, 68.92, 171.87),
    Testo("email.utente", 77.55, 147.66, 171.87, DESTRA), Testo("email.dominio", 151.38, 194.73, 171.87),
    *data("documento.rilasciato", 190.84, (107.36, 114.13), (115.32, 123.61), (124.8, 138.18)),
    *data("documento.scadenza", 190.84, (163.75, 170.52), (171.7, 180.0), (181.19, 194.56)),
    *(campo for riga in DOCUMENTI_IDENTITA for campo in _documento(*riga)),
    *FIRMA_AUTOCERTIFICAZIONE,
))

# Il contratto usa linee di trattini bassi: le quote sono il fondo dei trattini.
CONTRATTO_STUDENTE = Pagina("pagina-07.jpg", (
    Testo("nome_cognome", 32.2, 121.9, 124.97), Testo("cittadinanza", 143.4, 194.4, 124.97),
    Testo("nascita.luogo", 24.8, 147.9, 129.88), Testo("nascita.provincia", 150.1, 162.6, 129.88, CENTRO),
    *data("nascita", 129.88, (167.1, 174.8), (175.9, 182.7), (183.8, 194.4)),
    Testo("residenza.via", 33.3, 114.0, 134.79), Testo("residenza.civico", 115.7, 124.5, 134.79, CENTRO),
    Testo("residenza.cap", 21.7, 50.0, 139.7, CENTRO), Testo("residenza.comune", 57.6, 178.4, 139.7),
    Testo("residenza.provincia", 180.6, 193.0, 139.7, CENTRO),
))

CONTRATTO_CLAUSOLE = Pagina("pagina-08.jpg")
CONTRATTO_OBBLIGHI = Pagina("pagina-09.jpg")

CONTRATTO_FIRME = Pagina("pagina-10.jpg", (
    *luogo_data_firma(207.94, (23.54, 77.72), (89.58, 119.04), (127.68, 194.23)),
    Firma(22.35, 99.06, 253.66, 14.0),  # approvazione specifica delle clausole
))

# Come nei PDF del gestionale: il numero pratica in alto a destra, su ogni pagina tranne il regolamento.
NUMERO_PRATICA = Testo("pratica.numero", 165.5, 200.0, 15.6)


def con_numero_pratica(pagina: Pagina, numero: Testo = NUMERO_PRATICA) -> Pagina:
    return Pagina(pagina.sfondo, (numero, *pagina.campi))


PAGINE_SUCCESSIVE = (
    REGOLAMENTO,
    *(con_numero_pratica(pagina) for pagina in (
        PRIVACY, AUTOCERTIFICAZIONE_DICHIARAZIONI, AUTOCERTIFICAZIONE_CARRIERA, AUTENTICAZIONE_FOTO,
        CONTRATTO_STUDENTE, CONTRATTO_CLAUSOLE, CONTRATTO_OBBLIGHI, CONTRATTO_FIRME,
    )),
)
