"""Trasporto cookie e CSRF per richieste HTTP di test."""

from src.security.browser import nome_cookie, token_csrf


def token_cookie(risposta):
    return risposta.cookies[nome_cookie()]


def intestazioni_sessione(token):
    return {"Cookie": f"{nome_cookie()}={token}", "X-CSRF-Token": token_csrf(token)}
