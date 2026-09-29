from fastapi import HTTPException


class ErroreRealtime(HTTPException):
    def __init__(self, codice, stato=400):
        super().__init__(stato, codice)


def richiedi(condizione, codice="invalid_request", stato=400):
    if not condizione:
        raise ErroreRealtime(codice, stato)
