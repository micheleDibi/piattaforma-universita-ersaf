"""Valori aggiuntivi delle domande: titoli, corsi richiesti, date e importi.

Le dichiarazioni anagrafiche/universitarie riusano il mapping verificato per
eCampus. Non si deducono CFU, SSD, durata o consensi da una descrizione libera.
"""

from src.documenti.ecampus.valori import parti_data, piatto, valori


def _completi(dati: dict, campi: dict) -> dict:
    cliente, corso, pratica = dati["cliente"], dati["corso"], dati["pratica"]
    return {
        "nascita.data": cliente["data_nascita"], "nascita.cifre": cliente["data_nascita"].replace("/", ""),
        "email": cliente["email"], "telefono": cliente["telefono"], "cellulare": cliente["cellulare"],
        "recapito": cliente["cellulare"] or cliente["telefono"],
        "anno_accademico": pratica["anno_accademico"], "firma.cifre": pratica["data_creazione"].replace("/", ""),
        **piatto("firma.data", parti_data(pratica["data_creazione"])),
        "sede_erogazione": pratica["sede_erogazione"],
        "corso_livello": corso["descrizione"] + (f" - {corso['livello']} livello" if corso["livello"] else ""),
        "retta.intero": pratica["prezzo"].partition(",")[0] if campi["retta"] else "",
        "retta.decimali": pratica["prezzo"].partition(",")[2] if campi["retta"] else "",
        "titolo_accesso": campi["titolo.denominazione"] or campi["diploma.denominazione"],
        "accesso.diploma": campi["diploma"] and not campi["titolo"],
        **{f"accesso.{tipo}": campi[f"titolo.{tipo}"] for tipo in ("primo_livello", "secondo_livello", "vecchio_ordinamento")},
        "formazione": corso["tipo_corso"].casefold() == "corsi di formazione",
        "alta_formazione": corso["tipo_corso"].casefold() == "corsi di alta formazione",
        "singoli.domanda": f"di essere iscritto/a per l'anno accademico {pratica['anno_accademico']} ai seguenti insegnamenti:",
    }


def _singoli(dati: dict) -> dict:
    """Sei insegnamenti, senza confonderli con gli esami sostenuti dello studente."""
    corsi = dati.get("corsi_richiesti", [])
    return {f"richiesti.{i}.{campo}": corsi[i - 1].get(campo, "") if i <= len(corsi) else ""
            for i in range(1, 7) for campo in ("descrizione", "corso_laurea")}


def _date_e_titoli(dati: dict, campi: dict) -> dict:
    coppie = {f"{p}.voto_completo": "/".join(v for v in (campi[f"{p}.voto"], campi[f"{p}.voto_massimo"]) if v)
              for p in ("diploma", "integrativo", "titolo")}
    for p in ("diploma", "integrativo"):
        coppie[f"{p}.anno_completo"] = "/".join(v for v in (campi[f"{p}.anno.inizio"], campi[f"{p}.anno.fine"]) if v)
    for p in ("titolo", "lasciata", "decadenza"):
        coppie[f"{p}.data_completa"] = "/".join(campi[f"{p}.data.{c}"] for c in ("gg", "mm", "aaaa")).strip("/")
    coppie["documento.rilasciato_completo"] = dati["cliente"]["data_rilascio"]
    coppie["documento.scadenza_completa"] = dati["cliente"]["scadenza_documento"]
    coppie["diploma.anno_cifre"] = coppie["diploma.anno_completo"].replace("/", "")
    return coppie


def _ordinamenti(campi: dict) -> dict:
    coppie = {}
    nuovo = any(campi[f"titolo.{t}"] for t in ("primo_livello", "secondo_livello", "ciclo_unico"))
    for p, presente in (("vecchio", campi["titolo.vecchio_ordinamento"]), ("nuovo", nuovo)):
        for k in ("denominazione", "universita", "voto"):
            coppie[f"{p}.{k}"] = campi[f"titolo.{k}"] if presente else ""
        coppie[f"{p}.data"] = campi["titolo.data_completa"].replace("/", "") if presente else ""
    return coppie


def _carriera(dati: dict, campi: dict) -> dict:
    coppie = {"immatricolazione.cifre": dati["generalita"].get("data_immatricolazione", "").replace("/", "")}
    coppie["professione.mese_anno"] = "/".join(campi[f"professione.data.{p}"] for p in ("mm", "aaaa")).strip("/")
    coppie["qualifica.giorno_mese"] = "/".join(campi[f"qualifica.data.{p}"] for p in ("gg", "mm")).strip("/")
    uscita = "decadenza" if campi["decadenza"] else "lasciata"
    coppie["uscita"] = campi["decadenza"] or campi["trasferimento_rinuncia"]
    for k in ("universita", "citta", "provincia"):
        coppie[f"uscita.{k}"] = campi[f"{uscita}.{k}"]
    for k in ("gg", "mm", "aaaa"):
        coppie[f"uscita.{k}"] = campi[f"{uscita}.data.{k}"]
    return coppie


def valori_modulo(dati: dict, nome: str) -> dict:
    campi = valori(dati)
    campi.update(_completi(dati, campi))
    campi.update(_singoli(dati))
    campi.update(_date_e_titoli(dati, campi))
    campi.update(_ordinamenti(campi))
    campi.update(_carriera(dati, campi))
    if not nome.startswith("ecampus-"):
        # Il codice InDe allegato documenta queste scelte soltanto per eCampus.
        # Per gli altri enti non trasformiamo un dato assente in un consenso.
        campi["privacy.consenso"] = False
        campi["servizi.non_aderisce"] = False
    return campi
