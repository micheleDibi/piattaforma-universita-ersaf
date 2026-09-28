from dataclasses import dataclass

from fastapi import HTTPException

from src.auth.visibilita import riga_di_me
from src.pratiche.accesso import pratica_visibile


@dataclass(frozen=True)
class ContestoChat:
    utente_id: int
    cliente_id: int
    username: str
    pratica_id: int
    numero: str
    studente_id: int

    def richiesta(self, dataset):
        return dict(userId=self.utente_id, clientId=self.cliente_id, username=self.username,
                    practiceId=self.pratica_id, practiceCode=self.numero,
                    studentId=self.studente_id, dataset=dataset)


def contesto_chat(db, pratica_id, vis, utente):
    pratica = pratica_visibile(db, pratica_id, vis)
    me = riga_di_me(db, utente.utente_id)
    if me is None or not pratica.pratica_numero:
        raise HTTPException(403, "Il tuo account non può accedere alla chat di questa pratica.")
    return ContestoChat(utente.utente_id, me.cliente_id, utente.utente_username,
                        pratica_id, pratica.pratica_numero, pratica.cliente_id)
