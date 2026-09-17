"""Importa l'applicazione senza leggere backend/.env.

Si usa solo dentro un sottoprocesso con ambiente pulito (vedi
generatori.ambiente_pulito): `load_dotenv` viene sostituito e i due
BaseSettings smettono di leggere il file prima che qualcuno li istanzi.
"""

from __future__ import annotations

import sys


def importa_app(backend: str):
    sys.path.insert(0, backend)
    import dotenv

    dotenv.load_dotenv = lambda *a, **k: False
    import src.config as config

    config.Impostazioni.model_config["env_file"] = None
    import src.notifiche.config_sms as config_sms

    config_sms.ConfigSMS.model_config["env_file"] = None
    import src.main as main

    return main
