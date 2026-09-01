from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from models.utente import Utente
from schemas.utente_schema import UtenteCreate
import uuid


def get_utente_by_username(db: Session, username: str) -> Optional[Utente]:
    return db.query(Utente).filter(Utente.utente_username == username).first()

def create_utente(db: Session, utente_dto: UtenteCreate) -> Utente:

    salt = str(uuid.uuid4())
    hashed_pwd = f"hashed_{utente_dto.utente_password}_{salt}"

    db_utente = Utente(
        utente_username=utente_dto.utente_username,
        utente_password=utente_dto.utente_password,
        utente_salt=salt,
        utente_padre=utente_dto.utente_padre,
        utente_attivoSN=utente_dto.utente_attivoSN,
        utente_created_at=datetime.utcnow(),
        utente_created_by=1  
    )
    db.add(db_utente)
    db.commit()
    db.refresh(db_utente)
    return db_utente


