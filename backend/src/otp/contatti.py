from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.auth.dipendenze import get_current_utente
from src.database import get_db
from src.otp.models import Attivazione
from src.otp.servizio import blocca_cliente, gia_verificato, verifica
from src.otp.invio import genera_e_invia
from src.otp.attivazione import prepara_attivazione, comunica_accesso
from src.otp.schemas import ConfermaSfida
from src.security.rete import ip_client
from src.otp.models import ContattoVerificato

router = APIRouter(prefix="/clienti", dependencies=[Depends(get_current_utente)])
Tipo = Literal["email", "cellulare"]


class InvioContatto(BaseModel):
    valore: str = Field(max_length=255)


def stato_contatti(db, cliente, utente):
    righe = {r.tipo: r for r in db.query(ContattoVerificato)
             .filter(ContattoVerificato.cliente_id == cliente.cliente_id).all()}
    return {tipo: {
        "valore": getattr(cliente, "cliente_" + tipo) or "",
        "verificato": gia_verificato(db, cliente, tipo),
        "verificato_il": righe[tipo].verificato.isoformat() if tipo in righe else None,
    } for tipo in ("email", "cellulare")} | {
        "attivazione": "in_attesa" if db.get(Attivazione, utente.utente_id) else
                       "attivo" if utente.utente_attivoSN == -1 else "disattivato"}

@router.get("/{cliente_id}/contatti")
def stato(cliente_id: int, db: Session = Depends(get_db)):
    cliente, utente = blocca_cliente(db, cliente_id)
    return stato_contatti(db, cliente, utente)


@router.post("/{cliente_id}/contatti/{tipo}/genera-otp")
def genera(cliente_id: int, tipo: Tipo, corpo: InvioContatto, request: Request,
           db: Session = Depends(get_db), autore=Depends(get_current_utente)):
    contesto = blocca_cliente(db, cliente_id)
    if corpo.valore != (getattr(contesto[0], "cliente_" + tipo) or ""):
        raise HTTPException(409, "Il contatto è cambiato. Salva e ricarica la scheda prima della verifica.")
    if gia_verificato(db, contesto[0], tipo):
        raise HTTPException(409, "Il contatto è già verificato.")
    return genera_e_invia(db, contesto, tipo, (autore.utente_id, ip_client(request)))


@router.post("/{cliente_id}/contatti/{tipo}/verifica-otp")
def conferma(cliente_id: int, tipo: Tipo, corpo: ConfermaSfida, db: Session = Depends(get_db)):
    cliente, utente = blocca_cliente(db, cliente_id)
    verifica(db, (cliente, utente), (corpo.sfida, corpo.codice), tipo)
    credenziali = prepara_attivazione(db, cliente, utente)
    destinatario = cliente.cliente_email
    db.commit()
    inviata = comunica_accesso(db, destinatario, credenziali)
    messaggio = "Contatto verificato."
    if inviata is True:
        messaggio = "Contatti verificati: account attivato e credenziali inviate via email."
    elif inviata is False:
        messaggio = "Account attivato, ma invio delle credenziali non riuscito. Contatta il tuo referente ERSAF."
    return {**stato_contatti(db, cliente, utente), "message": messaggio, "credenziali_inviate": inviata}
