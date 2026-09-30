"""Identita applicativa unica; gli ID cliente e utente restano distinti."""

from dataclasses import dataclass

from src.realtime.dati import esegui
from src.realtime.errori import richiedi


@dataclass(frozen=True)
class Identita:
    utente_id: int
    cliente_id: int
    azienda_id: int
    ruolo: str
    nome: str
    codice_fiscale: str


def carica(db, utente_id, blocca=False):
    if blocca:
        esegui(db, "SELECT utente_id FROM utenti WHERE utente_id=:u LOCK IN SHARE MODE", {"u": utente_id})
        esegui(db, "SELECT cliente_id FROM clienti WHERE utente_id=:u LOCK IN SHARE MODE", {"u": utente_id})
    righe = (
        esegui(
            db,
            """SELECT u.utente_id,c.cliente_id,COALESCE(c.azienda_id,0) AS azienda_id,
        r.ruolo_codice AS ruolo,TRIM(CONCAT_WS(' ',c.cliente_nome,c.cliente_cognome)) AS nome,
        COALESCE(c.cliente_codice_fiscale,'') AS codice_fiscale FROM utenti u
        JOIN clienti c ON c.utente_id=u.utente_id JOIN ruoli r ON r.ruolo_id=c.cliente_ruolo
        WHERE u.utente_id=:u AND u.utente_attivoSN=-1
        AND (SELECT COUNT(*) FROM clienti uc WHERE uc.utente_id=:u)=1
        LIMIT 2"""
            + (" LOCK IN SHARE MODE" if blocca else ""),
            {"u": utente_id},
        )
        .mappings()
        .all()
    )
    richiedi(len(righe) == 1, "identity_not_current", 403)
    return Identita(**righe[0])
