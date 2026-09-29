"""Ripete l'intera unita transazionale, mai il solo statement fallito."""

from functools import wraps

from sqlalchemy.exc import IntegrityError, OperationalError


def ritenta(funzione):
    @wraps(funzione)
    def esegui(*args, **kwargs):
        for tentativo in range(3):
            try:
                return funzione(*args, **kwargs)
            except (IntegrityError, OperationalError) as errore:
                if tentativo == 2 or errore.orig.args[0] not in (1062, 1205, 1213):
                    raise

    return esegui
