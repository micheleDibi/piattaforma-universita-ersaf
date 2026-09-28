"""Client interno; credenziali e chiavi Java non arrivano mai al browser."""

from pathlib import Path
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException

from src.config import get_impostazioni

NON_DISPONIBILE = "La chat è temporaneamente non disponibile. Riprova tra poco."


class ServizioJava:
    def __init__(self, contesto):
        imp = get_impostazioni()
        parti = urlsplit(imp.chat_java_url)
        if (parti.scheme not in {"http", "https"} or not parti.hostname or parti.username
                or parti.query or parti.fragment or parti.path not in {"", "/"}
                or not imp.chat_dataset or not imp.chat_java_origine):
            raise HTTPException(503, NON_DISPONIBILE)
        try:
            secret = Path(imp.chat_java_secret_file).read_text(encoding="utf-8").strip()
        except OSError:
            raise HTTPException(503, NON_DISPONIBILE) from None
        if len(secret.encode()) < 32:
            raise HTTPException(503, NON_DISPONIBILE)
        self.base = imp.chat_java_url.rstrip("/")
        self.origine = imp.chat_java_origine
        self.contesto = contesto
        self.token = ""
        self._chiavi = {}
        risposta = self.richiesta("POST", "/internal/practices/session", token=secret,
                                  json=contesto.richiesta(imp.chat_dataset))
        self.token = risposta.get("accessToken", "")
        if not isinstance(self.token, str) or not self.token or str(risposta.get("userId")) != str(contesto.utente_id):
            self.chiudi()
            raise HTTPException(503, NON_DISPONIBILE)

    @property
    def socket_url(self):
        return ("wss" if self.base.startswith("https:") else "ws") + self.base[self.base.index(":"):] + "/ws"

    def richiesta(self, metodo, percorso, *, token=None, **opzioni):
        try:
            with httpx.Client(timeout=10, trust_env=False, follow_redirects=False) as client:
                risposta = client.request(metodo, self.base + percorso,
                    headers={"Authorization": "Bearer " + (token or self.token), "Origin": self.origine}, **opzioni)
            if risposta.status_code in {401, 403}:
                raise HTTPException(403, "Non sei tra i partecipanti autorizzati alla chat della pratica.")
            if risposta.status_code == 409:
                raise HTTPException(503, "I dati della pratica non sono allineati al servizio messaggi.")
            if risposta.status_code == 400:
                raise HTTPException(400, "Richiesta chat non valida. Ricarica i messaggi.")
            risposta.raise_for_status()
            return risposta.json() if risposta.content else {}
        except (httpx.HTTPError, ValueError, KeyError):
            raise HTTPException(503, NON_DISPONIBILE) from None

    def chiave(self, versione=None, ora=None, peer=None):
        indice = (versione, ora, peer)
        if indice in self._chiavi:
            return self._chiavi[indice]
        dati = dict(destinationType="PRACTICE", resourceId=str(self.contesto.pratica_id),
                    resourceCode=self.contesto.numero)
        if versione is not None:
            dati.update(keyVersion=versione, epochHour=ora)
        if peer is not None:
            dati["peerUserId"] = str(peer)
        chiave = self.richiesta("POST", "/crypto/key", json=dati)
        self._chiavi[indice] = chiave
        return chiave

    def chiudi(self):
        if self.token:
            try:
                self.richiesta("POST", "/auth/logout")
            except HTTPException:
                pass  # sessione comunque a scadenza assoluta breve
            self.token = ""
