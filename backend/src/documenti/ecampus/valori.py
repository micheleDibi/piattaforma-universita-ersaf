"""Valori dei moduli eCampus: dai dati comuni di una pratica ai testi e alle crocette.

Le regole vengono dal gestionale precedente (ReportLaureeEcampus, pagine 1-5),
con tre differenze volute:
- "ciclo unico" barrava la casella sbagliata del livello;
- "di NON essersi mai immatricolato" compariva proprio quando la data di
  immatricolazione c'era: qui vale quando non c'e' ne' data ne' rinnovo;
- un dato che manca lascia la casella vuota invece di dichiarare il contrario
  (diploma non conseguito, iscrizione altrove).

Come nei PDF che il gestionale generava: il luogo delle firme e' la citta'
dell'azienda della pratica, il numero pratica sta in alto a destra, il contratto
riporta nome e cognome in quest'ordine e due caselle sono sempre barrate.
"""

from __future__ import annotations

import re
from collections import defaultdict

from src.documenti.dati import normalizza

RIGHE_ESAMI = 15
SESSI = {"uomo": "m", "maschio": "m", "m": "m", "donna": "f", "femmina": "f", "f": "f"}
LIVELLI = {"triennale": "primo", "magistrale": "secondo", "ciclounico": "ciclo_unico"}
RINNOVI = ("primo_anno", "secondo_anno", "terzo_anno")
DOCUMENTI = {"cartadidentita": "carta", "passaporto": "passaporto", "patente": "patente", "altro": "altro"}
# Cinque voci e cinque caselle, abbinate come nel gestionale; valgono anche i codici del nuovo form.
TITOLI = {
    "diplomauniversitario": "diploma_universitario",
    "laureavecchioordinamento": "vecchio_ordinamento",
    "laurealaurea1livello": "primo_livello",
    "laurea1livello": "primo_livello",
    "laureamagistrale": "secondo_livello",
    "laureaspecialistica": "ciclo_unico",
}
# Istituto, citta', provincia, anno scolastico, voto e voto massimo.
COLONNE_SCUOLA = {
    "diploma": ("istituto", "citta_istituto", "provincia_istituto", "anno_scolastico",
                "votoRicevuto_diploma", "votoMassimo_diploma"),
    "integrativo": ("istituto_ai", "citta_istituto_ai", "provincia_istituto_ai", "anno_scolastico_ai",
                    "votoRicevuto_ai", "votoMassimo_ai"),
}
ISCRIZIONI = {
    "laureailivello": "laurea_primo", "laureaiilivello": "laurea_secondo", "laureaciclounico": "laurea_ciclo_unico",
    "masterilivello": "master_primo", "masteriilivello": "master_secondo", "altro": "altro",
}


def piatto(prefisso: str, valori: dict) -> dict:
    """{"cap": "20100"} con prefisso "residenza" -> {"residenza.cap": "20100"}."""
    return {f"{prefisso}.{chiave}": valore for chiave, valore in valori.items()}


def parti_data(valore: str) -> dict:
    """'17/09/2026' -> giorno, mese e anno separati; vuoti se la data non c'e'."""
    parti = valore.split("/")
    gg, mm, aaaa = parti if len(parti) == 3 else ("", "", "")
    return {"gg": gg, "mm": mm, "aaaa": aaaa}


def anni(valore: str, *, anno_solo: str = "inizio") -> dict:
    """'2024/25', '2024-2025', '25/26' -> inizio e fine a quattro cifre; un anno solo va in `anno_solo`."""
    coppia = re.fullmatch(r"(\d{2}|\d{4})\s*[/-]\s*(\d{2}|\d{4})", valore)
    if coppia:
        inizio, fine = coppia.groups()
        inizio = inizio if len(inizio) == 4 else f"20{inizio}"
        return {"inizio": inizio, "fine": fine if len(fine) == 4 else inizio[:2] + fine}
    if re.fullmatch(r"\d{4}", valore):
        return {"inizio": "", "fine": "", anno_solo: valore}
    return {"inizio": valore, "fine": ""}  # scritto in un altro modo: resta com'e'


def telefono(valore: str) -> dict:
    """Il prefisso internazionale italiano, se c'e', separato dal numero."""
    compatto = re.sub(r"[\s./-]", "", valore)
    italiano = re.fullmatch(r"(?:\+|00)39(\d{6,})", compatto)
    if italiano:
        return {"prefisso": "+39", "numero": italiano.group(1)}
    return {"prefisso": "", "numero": valore}


def email(valore: str) -> dict:
    utente, chiocciola, dominio = valore.rpartition("@")
    return {"utente": utente, "dominio": dominio} if chiocciola else {"utente": valore, "dominio": ""}


def _indirizzo(parti: dict) -> dict:
    via, civico = parti["indirizzo"], parti["civico"]
    return {
        "via": via, "civico": civico, "indirizzo": ", ".join(v for v in (via, civico) if v),
        "cap": parti["cap"], "comune": parti["comune"], "provincia": parti["provincia"],
    }


def _corrispondenza(cliente: dict, generalita: dict) -> dict:
    """Il domicilio, solo se e' diverso dalla residenza: il modulo dice "se differente"."""
    domicilio, residenza = cliente["domicilio"], cliente["residenza"]
    uguale = all(normalizza(domicilio[k]) == normalizza(residenza[k]) for k in ("indirizzo", "civico", "comune"))
    if not domicilio["indirizzo"] or uguale or normalizza(generalita["corrispondenza"]) == "residenza":
        domicilio = dict.fromkeys(domicilio, "")
    return _indirizzo(domicilio)


def _anagrafica(cliente: dict) -> dict:
    sesso = SESSI.get(normalizza(cliente["sesso"]))
    nascita = {"luogo": cliente["luogo_nascita"], "provincia": cliente["provincia_nascita"], **parti_data(cliente["data_nascita"])}
    return {
        "cognome": cliente["cognome"], "nome": cliente["nome"],
        "nome_cognome": " ".join(v for v in (cliente["nome"], cliente["cognome"]) if v),
        "codice_fiscale": cliente["codice_fiscale"].upper(), "cittadinanza": cliente["cittadinanza"],
        "sesso.m": sesso == "m", "sesso.f": sesso == "f",
        **piatto("nascita", nascita),
        **piatto("telefono", telefono(cliente["cellulare"] or cliente["telefono"])),
        **piatto("email", email(cliente["email"])),
    }


def _domanda(pratica: dict, corso: dict) -> dict:
    """Pagina 1: anno accademico, immatricolazione o rinnovo, corso e retta."""
    # Come nel gestionale: se i rinnovi segnati sono piu' d'uno vale l'anno piu' basso.
    anno = next((numero for numero, chiave in enumerate(RINNOVI, 1) if pratica["rinnovo"][chiave]), None)
    livello = LIVELLI.get(normalizza(corso["durata"]))
    retta = "" if pratica["prezzo"] in ("", "0,00") else pratica["prezzo"].removesuffix(",00")
    return {
        **piatto("anno_accademico", anni(pratica["anno_accademico"])),
        "immatricolazione": anno is None, "iscrizione": anno is not None,
        **{f"anno.{numero}": anno == numero for numero in range(1, len(RINNOVI) + 1)},
        "corso": corso["descrizione"],
        **{f"livello.{nome}": livello == nome for nome in LIVELLI.values()},
        "retta": retta,
    }


def _documento(cliente: dict) -> dict:
    """Pagina 6: numero e rilascio solo sulla riga del tipo di documento."""
    tipo = DOCUMENTI.get(normalizza(cliente["tipo_documento"]))
    campi = {}
    for nome in DOCUMENTI.values():
        campi[f"documento.{nome}"] = nome == tipo
        campi[f"documento.{nome}.numero"] = cliente["documento"] if nome == tipo else ""
        campi[f"documento.{nome}.rilascio"] = cliente["comune_rilascio"] if nome == tipo else ""
    return {
        **campi,
        **piatto("documento.rilasciato", parti_data(cliente["data_rilascio"])),
        **piatto("documento.scadenza", parti_data(cliente["scadenza_documento"])),
    }


def _scuola(g: dict, prefisso: str) -> dict:
    """Dove e quando: per il diploma e per l'anno integrativo. Un anno solo e' quello di fine."""
    istituto, citta, provincia, anno, voto, massimo = (g[colonna] for colonna in COLONNE_SCUOLA[prefisso])
    return piatto(prefisso, {
        "istituto": istituto, "citta": citta, "provincia": provincia,
        **piatto("anno", anni(anno, anno_solo="fine")), "voto": voto, "voto_massimo": massimo,
    })


def _studi(g: dict) -> dict:
    """Pagina 4: diploma, anno integrativo e invalidita'."""
    return {
        "diploma": bool(g["diploma"]), "diploma.denominazione": g["diploma"],
        **_scuola(g, "diploma"),
        **_scuola(g, "integrativo"),
        "invalidita": bool(g["percentualeInvalidita"]), "invalidita.percentuale": g["percentualeInvalidita"],
    }


def _carriera(g: dict, *, compilata: bool, rinnovo: bool) -> dict:
    """Pagina 4: immatricolazioni, iscrizioni in corso e titolo universitario."""
    titolo = TITOLI.get(normalizza(g["titolo_universitario"]))
    carriera_presente = any(g[k] for k in ("titolo_universitario", "attIscritto_tipo", "conclusione", "data_immatricolazione"))
    mai_immatricolato = compilata and not rinnovo and g["immatricolato"] in ("", "0") and not carriera_presente
    return {
        "mai_immatricolato": mai_immatricolato,
        "non_iscritto_altrove": compilata and g["iscrizioneAltraUniversita"] in ("", "0"),
        "titolo": bool(g["titolo_universitario"]),
        **{f"titolo.{nome}": titolo == nome for nome in dict.fromkeys(TITOLI.values())},
        "titolo.denominazione": g["materia_titolo"], "titolo.universita": g["universita_titolo"],
        **piatto("titolo.data", parti_data(g["data_titolo"])),
        "titolo.voto": g["votoRicevuto_titolo"], "titolo.voto_massimo": g["votoMassimo_titolo"],
    }


def _uscita(g: dict) -> dict:
    """Pagina 4: trasferimento, rinuncia o decadenza da un'altra universita'."""
    esito = normalizza(g["conclusione"])
    dove = {"universita": g["universitaConclusione"], "citta": g["cittaUniConclusione"],
            "provincia": g["provinciaConclusione"], **piatto("data", parti_data(g["data_conclusione"]))}
    vuoto = dict.fromkeys(dove, "")
    lasciata = esito in ("trasferimento", "rinuncia")
    return {
        "trasferimento_rinuncia": lasciata, "trasferimento": esito == "trasferimento", "rinuncia": esito == "rinuncia",
        **piatto("lasciata", dove if lasciata else vuoto),
        "decadenza": esito == "decadenza",
        **piatto("decadenza", dove if esito == "decadenza" else vuoto),
    }


def _iscrizione_in_corso(g: dict) -> dict:
    """Pagina 5: il corso a cui lo studente e' iscritto adesso (iscrizione contemporanea)."""
    tipo = ISCRIZIONI.get(normalizza(g["attIscritto_tipo"]))
    modalita = normalizza(g["attIscritto_modalita"])
    return {
        "iscritto": tipo is not None,
        **{f"iscritto.{nome}": tipo == nome for nome in ISCRIZIONI.values()},
        **piatto("iscritto", {chiave: g[f"attIscritto_{colonna}"] for chiave, colonna in (
            ("altro_corso", "altro"), ("classe", "classeLaurea"), ("denominazione", "denominazione"),
            ("universita", "universita"), ("citta", "citta"), ("provincia", "provincia"), ("anno", "annoIscrizione"))}),
        "iscritto.part_time": modalita == "parttime", "iscritto.full_time": modalita == "fulltime",
    }


def _certificazioni(g: dict) -> dict:
    """Pagina 5: abilitazione professionale, albo e qualifica."""
    return {
        "professione": bool(g["professione"]), "professione.nome": g["professione"],
        "professione.presso": g["luogo_professione"], **piatto("professione.data", parti_data(g["data_professione"])),
        "albo": bool(g["albo"]), "albo.nome": g["albo"],
        "qualifica": bool(g["qualifica_professionale"]), "qualifica.nome": g["qualifica_professionale"],
        "qualifica.presso": g["luogo"], **piatto("qualifica.data", parti_data(g["data_qualifica"])),
    }


def _esami(esami: list[dict]) -> dict:
    """Pagina 5: la tabella ha quindici righe; se non bastano l'ultima dice quanti esami restano fuori."""
    riportati = esami if len(esami) <= RIGHE_ESAMI else esami[:RIGHE_ESAMI - 1]
    campi = {"esami": bool(esami), "esami.universita": ", ".join(dict.fromkeys(e["universita"] for e in esami if e["universita"]))}
    for numero in range(1, RIGHE_ESAMI + 1):
        esame = riportati[numero - 1] if numero <= len(riportati) else {}
        campi.update({f"esami.{numero}.{colonna}": esame.get(colonna, "") for colonna in ("insegnamento", "data", "ssd", "cfu", "voto")})
    if len(esami) > len(riportati):
        campi[f"esami.{RIGHE_ESAMI}.insegnamento"] = f"… e altri {len(esami) - len(riportati)} esami"
    return campi


def _senza_dati() -> dict:
    """Voci che il gestionale non raccoglie e che non compilava neanche nei suoi PDF."""
    return {
        "nascita.stato": "", "curriculum": "", "servizi_integrativi": "",
        "corso_innovativo.si": False, "corso_innovativo.no": False,
        "diploma.statale": False, "diploma.paritario": False,
    }


def _scelte_fisse() -> dict:
    """Caselle che i PDF del gestionale barravano sempre, senza un dato che le decidesse."""
    return {
        "privacy.consenso": True, "privacy.diniego": False,
        "servizi.aderisce": False, "servizi.non_aderisce": True,
    }


def valori(dati: dict) -> dict:
    """Tutti i valori dei campi dei moduli eCampus, con chiavi piatte."""
    cliente, pratica = dati["cliente"], dati["pratica"]
    generalita = defaultdict(str, dati["generalita"])  # senza scheda universitaria ogni voce e' vuota
    return {
        **_anagrafica(cliente),
        **piatto("residenza", _indirizzo(cliente["residenza"])),
        **piatto("corrispondenza", _corrispondenza(cliente, generalita)),
        **_domanda(pratica, dati["corso"]),
        **_documento(cliente),
        **_studi(generalita),
        **_carriera(generalita, compilata=bool(dati["generalita"]), rinnovo=any(pratica["rinnovo"].values())),
        **_uscita(generalita),
        **_iscrizione_in_corso(generalita),
        **_certificazioni(generalita),
        **_esami(dati["esami"]),
        **_senza_dati(),
        **_scelte_fisse(),
        "pratica.numero": pratica["numero"],
        "firma.luogo": dati["azienda"]["citta"],
        "firma.data": pratica["data_creazione"],
    }
