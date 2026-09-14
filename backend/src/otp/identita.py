import hashlib
import hmac
import re
from fastapi import HTTPException
from src.config import get_impostazioni


def impronta(valore: str) -> str:
    return hmac.new(get_impostazioni().session_token_pepper.encode(),
                    ("ersaf-otp-v1:" + valore).encode(), hashlib.sha256).hexdigest()


def destinazione(cliente, tipo: str) -> str:
    if tipo == "cellulare":
        numero = re.sub(r"[\s().-]", "", cliente.cliente_cellulare or "")
        if numero.startswith("00"):
            numero = "+" + numero[2:]
        if not numero.startswith("+") and re.fullmatch(r"3\d{8,9}", numero):
            numero = "+39" + numero
        if not re.fullmatch(r"\+[1-9]\d{7,14}", numero):
            raise HTTPException(422, "Inserisci un cellulare valido con prefisso internazionale.")
        return numero
    email = (cliente.cliente_email or "").strip()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(422, "Inserisci un indirizzo email valido.")
    return email


def versione(cliente, tipo: str, utente=None) -> str:
    valore = cliente.cliente_cellulare if tipo == "cellulare" else cliente.cliente_email
    epoch = (utente.utente_password_hash or utente.utente_password) if tipo == "login" else ""
    return impronta(f"contatto:{cliente.cliente_id}:{tipo}:{valore}:{epoch}")


def maschera(valore: str) -> str:
    if "@" in valore:
        nome, dominio = valore.split("@", 1)
        return nome[:1] + "•••@" + dominio
    return valore[:3] + " ••• ••• " + valore[-3:]
