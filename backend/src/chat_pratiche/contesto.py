from dataclasses import dataclass


@dataclass(frozen=True)
class ContestoChat:
    utente_id: int
    cliente_id: int
    username: str
    pratica_id: int
    numero: str
    studente_id: int
