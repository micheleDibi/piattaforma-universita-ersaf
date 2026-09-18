"""Autenticatore WebAuthn software per i test.

Chiave EC P-256, attestazione `none`, utente sempre presente e verificato,
flag di passkey sincronizzata. Produce le stesse strutture che il browser
consegna al server (campi base64url), cosi' i test attraversano il codice
reale di verifica di `webauthn` senza un telefono in mano.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import struct

import cbor2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

# UP presenza, UV verifica dell'utente, AT dati della credenziale, BE/BS passkey sincronizzata.
_UP, _UV, _BE, _BS, _AT = 0x01, 0x04, 0x08, 0x10, 0x40


def b64url(dati: bytes) -> str:
    return base64.urlsafe_b64encode(dati).rstrip(b"=").decode("ascii")


def dal_b64url(testo: str) -> bytes:
    return base64.urlsafe_b64decode(testo + "=" * (-len(testo) % 4))


class AutenticatoreVirtuale:
    def __init__(self) -> None:
        self.chiave = ec.generate_private_key(ec.SECP256R1())
        self.credential_id = os.urandom(32)
        self.contatore = 0
        self.aaguid = bytes(16)

    def _cose(self) -> bytes:
        numeri = self.chiave.public_key().public_numbers()
        return cbor2.dumps({1: 2, 3: -7, -1: 1, -2: numeri.x.to_bytes(32, "big"), -3: numeri.y.to_bytes(32, "big")})

    def _auth_data(self, rp_id: str, flags: int, con_credenziale: bool) -> bytes:
        dati = hashlib.sha256(rp_id.encode("utf-8")).digest() + bytes([flags]) + struct.pack(">I", self.contatore)
        if con_credenziale:
            dati += self.aaguid + struct.pack(">H", len(self.credential_id)) + self.credential_id + self._cose()
        return dati

    @staticmethod
    def _client_data(tipo: str, challenge: str, origin: str) -> bytes:
        return json.dumps({"type": tipo, "challenge": challenge, "origin": origin, "crossOrigin": False}).encode("utf-8")

    def registra(self, opzioni: dict, origin: str) -> dict:
        """Cio' che restituirebbe navigator.credentials.create() per le opzioni del server."""
        client_data = self._client_data("webauthn.create", opzioni["challenge"], origin)
        auth_data = self._auth_data(opzioni["rp"]["id"], _UP | _UV | _BE | _BS | _AT, con_credenziale=True)
        attestazione = cbor2.dumps({"fmt": "none", "attStmt": {}, "authData": auth_data})
        return {
            "id": b64url(self.credential_id), "rawId": b64url(self.credential_id), "type": "public-key",
            "response": {
                "clientDataJSON": b64url(client_data), "attestationObject": b64url(attestazione),
                "transports": ["hybrid", "internal"],
            },
            "clientExtensionResults": {}, "authenticatorAttachment": "cross-platform",
        }

    def autentica(self, opzioni: dict, origin: str, contatore: int | None = None) -> dict:
        """Cio' che restituirebbe navigator.credentials.get(); il contatore avanza da solo."""
        self.contatore = self.contatore + 1 if contatore is None else contatore
        client_data = self._client_data("webauthn.get", opzioni["challenge"], origin)
        auth_data = self._auth_data(opzioni["rpId"], _UP | _UV | _BE | _BS, con_credenziale=False)
        firma = self.chiave.sign(auth_data + hashlib.sha256(client_data).digest(), ec.ECDSA(hashes.SHA256()))
        return {
            "id": b64url(self.credential_id), "rawId": b64url(self.credential_id), "type": "public-key",
            "response": {
                "clientDataJSON": b64url(client_data), "authenticatorData": b64url(auth_data),
                "signature": b64url(firma),
            },
            "clientExtensionResults": {}, "authenticatorAttachment": "cross-platform",
        }
