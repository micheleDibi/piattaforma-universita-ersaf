from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from src.auth.accesso import emetti_sessione
from src.auth.servizio_login import cliente_principale, codice_ruolo
from src.database import get_db
from src.otp.servizio import blocca_cliente, cerca_sfida, verifica
from src.otp.identita import versione
from src.otp.invio import genera_e_invia
from src.otp.schemas import RichiestaSfida, ConfermaSfida
from src.security.rete import ip_client

router = APIRouter(prefix="/auth")


def contesto_login(db, token):
    sfida = cerca_sfida(db, token)
    cliente, utente = blocca_cliente(db, sfida.cliente_id)
    db.refresh(sfida, with_for_update=True)
    principale = cliente_principale(db, utente.utente_id)
    if (sfida.tipo != "login" or sfida.stato not in {"inviato", "fallito"}
            or sfida.versione != versione(cliente, "login", utente)
            or utente.utente_attivoSN != -1 or not principale
            or principale.cliente_id != cliente.cliente_id
            or (codice_ruolo(db, cliente.cliente_ruolo) or "").lower() != "nazionale"):
        raise HTTPException(400, "Verifica non valida. Ripeti l'accesso.")
    from sqlalchemy import func, select
    if sfida.scadenza <= db.scalar(select(func.now())):
        raise HTTPException(400, "Verifica scaduta. Ripeti l'accesso.")
    return cliente, utente


@router.post("/verifica-otp")
def conferma(corpo: ConfermaSfida, request: Request, response: Response, db: Session = Depends(get_db)):
    contesto = contesto_login(db, corpo.sfida)
    verifica(db, contesto, (corpo.sfida, corpo.codice), "login")
    return emetti_sessione(db, contesto[1], "Nazionale", request, response)


@router.post("/rigenera-otp")
def rigenera(corpo: RichiestaSfida, request: Request, db: Session = Depends(get_db)):
    contesto = contesto_login(db, corpo.sfida)
    return genera_e_invia(db, contesto, "login", (contesto[1].utente_id, ip_client(request)))
