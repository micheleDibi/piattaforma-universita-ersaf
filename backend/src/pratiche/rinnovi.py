"""Scelta dell'anno di rinnovo, con la convenzione dei flag legacy."""

from src.comune.flag_legacy import a_flag_legacy

CAMPI_RINNOVO = ("pratica_rinnPrimoAnno", "pratica_rinnSecondoAnno", "pratica_rinnTerzoAnno")
SCELTA_MULTIPLA = "Solo un anno di rinnovo puo' essere selezionato alla volta."


def verifica_rinnovo(valori):
    if sum(bool(a_flag_legacy(valori.get(campo))) for campo in CAMPI_RINNOVO) > 1:
        raise ValueError(SCELTA_MULTIPLA)


def verifica_modifica_rinnovo(pratica, modifiche):
    # Una modifica delle sole note non deve bloccare righe legacy incoerenti.
    # Quando si tocca il rinnovo, conta il risultato persistito, non solo i
    # campi del payload: il chiamante tiene il blocco sulla pratica.
    if set(CAMPI_RINNOVO).intersection(modifiche):
        verifica_rinnovo({campo: modifiche.get(campo, getattr(pratica, campo))
                         for campo in CAMPI_RINNOVO})
