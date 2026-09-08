"""La convenzione booleana della piattaforma Instant Developer.

Nelle tabelle legacy il vero non e' 1: e' -1. Non ovunque, pero', ed e' questo
che ha prodotto i difetti. Contati sui dati reali:

    universita_immatricolato                  0 -> 3910,  1 -> 90    vero = 1
    universita_iscrizioneAltraUniversita      0 -> 3964, -1 -> 36    vero = -1
    universita_attivita_professionalizzanti   0 -> 3943, -1 -> 57    vero = -1
    universita_corsi_di_formazione            0 -> 3911, -1 -> 89    vero = -1
    universita_altre_attivita_certificate     0 -> 3912, -1 -> 88    vero = -1

Quattro colonne su cinque usano -1; universita_immatricolato e' l'eccezione
perche' nasce da una tendina, non da una casella.

La conversione era riscritta a mano in ogni punto di scrittura, e divergeva:
clienti/routers.py scriveva 1 per tutte e cinque, e un -1 in ingresso non
corrispondeva a nessun ramo, finiva nell'else e veniva salvato 0 - cioe' un
vero diventava un falso senza alcun errore. Qui la regola sta in un posto solo.
"""

from __future__ import annotations

# Il falso e' 0 ovunque. Il vero dipende dalla colonna.
FALSO = 0
VERO = -1
VERO_UNO = 1

_FALSI = frozenset({None, "", "0", "false", "False", "no", "n", "N"})
_VERI = frozenset({"1", "-1", "true", "True", "si", "s", "S", "sì"})


def a_flag_legacy(valore: object, vero: int = VERO) -> int:
    """Normalizza un valore qualsiasi nella coppia (0, `vero`).

    Accetta cio' che arriva davvero dal frontend e dal database: booleani,
    interi, stringhe, None. Non solleva mai: un valore inatteso non deve
    trasformare la lettura di una riga legacy in un 500, e soprattutto non deve
    finire nel ramo "falso" - il difetto originale era proprio questo.

    Qualunque intero diverso da zero vale vero. Serve anche in lettura: le
    righe scritte con 1 su una colonna la cui convenzione e' -1 tornano cosi'
    nella forma canonica, e le caselle del curriculum si rispuntano da sole.
    """
    if isinstance(valore, bool):
        return vero if valore else FALSO

    if isinstance(valore, int):
        return vero if valore != FALSO else FALSO

    if valore is None:
        return FALSO

    if isinstance(valore, str):
        testo = valore.strip()
        if testo in _FALSI:
            return FALSO
        if testo in _VERI:
            return vero
        try:
            return vero if int(testo) != FALSO else FALSO
        except ValueError:
            # Una stringa che non e' ne' un booleano riconoscibile ne' un
            # numero: si considera assente, come il resto dei campi vuoti.
            return FALSO

    return FALSO


def a_flag_legacy_uno(valore: object) -> int:
    """Per le colonne la cui convenzione di vero e' 1 e non -1."""
    return a_flag_legacy(valore, vero=VERO_UNO)
